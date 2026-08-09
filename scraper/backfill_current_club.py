"""
Sett `athletes.current_club_id` for utøvere som mangler den, men som har
resultater med klubb.

BAKGRUNN
--------
Ca. 18 400 utøvere har `current_club_id = NULL`. Diagnosen 2026-08-09 viste at
de deler seg i to:

  A) ~6 500 har resultater der `results.club_id` er satt. Klubbtilknytningen
     finnes altså allerede i basen — den er bare ikke løftet opp på utøveren.
     Det er disse dette skriptet fikser.

  B) ~11 400 har ingen resultater i det hele tatt. Kontroll mot kilden viser at
     de er tomme der også. Det er ekte personer i utøverregisteret uten
     registrerte resultater. De skal IKKE røres — se OPERATIONS_LOG.md.

METODE
------
Klubben hentes fra utøverens **nyeste** resultat med klubb, slik at en utøver
som har byttet klubb får den siste. Ingen data hentes utenfra; vi kobler kun
sammen det som allerede står i basen.

BRUK
----
    python backfill_current_club.py                # dry-run (standard)
    python backfill_current_club.py --apply        # utfører
    python backfill_current_club.py --apply --yes  # uten bekreftelse
"""

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SCRIPT_NAME = Path(__file__).stem
TIMESTAMP = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOG_DIR = Path(__file__).parent / 'logs'
BACKUP_DIR = Path(__file__).parent / 'backups'
LOG_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log', encoding='utf-8'),
    ],
)
logger = logging.getLogger(__name__)

CHUNK = 200


def fetch_all(sb: Client, table: str, columns: str, chunk: int = 1000, **eq):
    rows, start = [], 0
    while True:
        q = sb.table(table).select(columns)
        for k, v in eq.items():
            q = q.is_(k, v) if v is None else q.eq(k, v)
        res = q.range(start, start + chunk - 1).execute()
        rows.extend(res.data)
        if len(res.data) < chunk:
            return rows
        start += chunk


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='Utfør oppdateringen.')
    ap.add_argument('--yes', action='store_true', help='Hopp over bekreftelse.')
    args = ap.parse_args()

    url, key = os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY')
    if not url or not key:
        logger.error('Mangler SUPABASE_URL / SUPABASE_SERVICE_KEY i .env')
        sys.exit(1)
    sb = create_client(url, key)

    logger.info('=' * 72)
    logger.info('Backfill av current_club_id — modus: %s',
                'APPLY' if args.apply else 'DRY-RUN')
    logger.info('=' * 72)

    missing = fetch_all(sb, 'athletes', 'id,full_name', current_club_id=None)
    logger.info('Utøvere uten current_club_id: %d', len(missing))

    # Hent resultater for disse utøverne, i porsjoner.
    latest = {}   # athlete_id -> (dato, club_id)
    ids = [a['id'] for a in missing]
    for i in range(0, len(ids), CHUNK):
        batch = ids[i:i + CHUNK]
        rows = sb.table('results').select('athlete_id,club_id,date')\
                 .in_('athlete_id', batch).not_.is_('club_id', None).execute().data
        for r in rows:
            prev = latest.get(r['athlete_id'])
            if prev is None or (r['date'] or '') > prev[0]:
                latest[r['athlete_id']] = (r['date'] or '', r['club_id'])
        if (i // CHUNK) % 20 == 0:
            logger.info('  ... %d/%d utøvere gjennomgått', min(i + CHUNK, len(ids)), len(ids))

    logger.info('')
    logger.info('Kan settes fra eget resultat:  %d', len(latest))
    logger.info('Har ingen resultat med klubb:  %d  (røres ikke)',
                len(missing) - len(latest))

    by_club = defaultdict(list)
    for aid, (_, cid) in latest.items():
        by_club[cid].append(aid)
    logger.info('Fordeler seg på %d klubber', len(by_club))

    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    backup.write_text(json.dumps({
        'generated_at': TIMESTAMP,
        'note': 'current_club_id var NULL for alle disse før kjøring. '
                'Angring: sett feltet tilbake til NULL for de oppførte id-ene.',
        'mapping': {aid: cid for aid, (_, cid) in latest.items()},
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info('Sikkerhetskopi: %s', backup)

    if not args.apply:
        names = {a['id']: a['full_name'] for a in missing}
        logger.info('')
        logger.info('DRY-RUN — eksempler:')
        for aid, (d, cid) in list(latest.items())[:8]:
            logger.info('   %s -> klubb %s (fra resultat %s)', names.get(aid), cid[:8], d)
        logger.info('Kjør med --apply for å utføre.')
        return

    if not args.yes:
        print(f'\nDette setter klubb på {len(latest)} utøvere.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            logger.info('Avbrutt av bruker.')
            return

    updated = 0
    for n, (cid, aids) in enumerate(by_club.items(), 1):
        for i in range(0, len(aids), CHUNK):
            res = sb.table('athletes').update({'current_club_id': cid})\
                    .in_('id', aids[i:i + CHUNK]).execute()
            updated += len(res.data)
        if n % 200 == 0:
            logger.info('  ... %d/%d klubber behandlet', n, len(by_club))

    logger.info('')
    logger.info('Utøvere oppdatert: %d', updated)
    logger.info('Ferdig. Logg: %s', LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log')


if __name__ == '__main__':
    main()
