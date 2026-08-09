"""
Slå sammen dublette klubber som bare skiller seg på tegnsetting, mellomrom
eller store/små bokstaver.

Eksempler fra basen:
    "IL i BUL Tromsø" / "IL i BUL, Tromsø" / "IL i BUL,Tromsø" / "IL i BUL-Tromsø"
    "Ullensaker/Kisa IL" / "Ullensaker-Kisa IL"
    "Svorkmo N.O.I." / "Svorkmo NOI"

METODE
------
Klubber grupperes på en nøkkel der alt annet enn bokstaver og tall er fjernet
og teksten er gjort om til små bokstaver. Grupper med mer enn én klubb slås
sammen til én.

  * Hvilken RAD som beholdes avgjøres av antall resultater — den største vinner,
    slik at færrest mulig rader må flyttes.
  * Hvilket NAVN som beholdes avgjøres av en kvalitetsscore, fordi den største
    varianten ikke alltid har riktig skrivemåte ("Leksvik Il" har flere
    resultater enn "Leksvik IL", men sistnevnte er korrekt).

Kun `results.club_id` og `athletes.current_club_id` peker på klubber.
`club_memberships` er tom og `meets.organizer_club_id` er ubrukt per 2026-08-09.

BRUK
----
    python merge_duplicate_clubs.py                # dry-run (standard)
    python merge_duplicate_clubs.py --apply        # utfører sammenslåingen
    python merge_duplicate_clubs.py --apply --yes  # uten bekreftelse
"""

import argparse
import json
import logging
import os
import re
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

# Entydige norske klubbtype-forkortelser. Brukes KUN til å rette
# bokstavstørrelse ("Leksvik Il" -> "Leksvik IL"). Bevisst konservativ liste:
# ord som også kan være stedsnavn eller egennavn holdes utenfor.
ABBREVIATIONS = {
    'IL', 'IF', 'IK', 'SK', 'FIK', 'TIF', 'BIL', 'AIL', 'TIL', 'FIL', 'SIL',
    'UIL', 'IBK', 'BUL', 'TF', 'FK', 'AK', 'BK', 'IFK', 'NTNUI', 'OSI', 'KFUM',
}


def norm_key(name: str) -> str:
    """Nøkkel som ignorerer tegnsetting, mellomrom og bokstavstørrelse."""
    return re.sub(r'[^0-9a-zA-ZæøåÆØÅ]', '', name or '').lower()


def fix_abbrev_case(name: str) -> str:
    """Rett bokstavstørrelse på kjente klubbforkortelser.

    Endrer ALDRI tegnsetting eller ordinndeling — kun store/små bokstaver på
    ord som utvetydig er en klubbtype. Vi finner ikke opp nye skrivemåter.
    """
    return re.sub(
        r'\b[A-Za-zÆØÅæøå]+\b',
        lambda m: m.group(0).upper() if m.group(0).upper() in ABBREVIATIONS else m.group(0),
        name,
    )


def fetch_all(sb: Client, table: str, columns: str, chunk: int = 1000):
    rows, start = [], 0
    while True:
        res = sb.table(table).select(columns).range(start, start + chunk - 1).execute()
        rows.extend(res.data)
        if len(res.data) < chunk:
            return rows
        start += chunk


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='Utfør sammenslåingen.')
    ap.add_argument('--yes', action='store_true', help='Hopp over bekreftelse.')
    args = ap.parse_args()

    url, key = os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY')
    if not url or not key:
        logger.error('Mangler SUPABASE_URL / SUPABASE_SERVICE_KEY i .env')
        sys.exit(1)
    sb = create_client(url, key)

    logger.info('=' * 72)
    logger.info('Sammenslåing av dublette klubber — modus: %s',
                'APPLY' if args.apply else 'DRY-RUN')
    logger.info('=' * 72)

    clubs = fetch_all(sb, 'clubs', 'id,name,city,county,club_type')
    logger.info('Klubber i basen: %d', len(clubs))

    groups = defaultdict(list)
    for c in clubs:
        groups[norm_key(c['name'])].append(c)
    dupes = {k: v for k, v in groups.items() if k and len(v) > 1}
    logger.info('Dublettgrupper funnet: %d', len(dupes))

    # Tell kun for klubbene som faktisk er i en dublettgruppe.
    def count(table: str, col: str, club_id: str) -> int:
        return sb.table(table).select('id', count='exact')\
                 .eq(col, club_id).limit(1).execute().count or 0

    plan = []
    for k, members in dupes.items():
        for m in members:
            m['n_res'] = count('results', 'club_id', m['id'])
            m['n_ath'] = count('athletes', 'current_club_id', m['id'])

        # Rad som beholdes: flest resultater (færrest rader å flytte).
        target = max(members, key=lambda m: (m['n_res'], m['n_ath']))
        # Navn: samme variant som beholdes, kun med rettet forkortelseskasus.
        # Vi velger aldri en annen skrivemåte enn den mest brukte.
        best_name = fix_abbrev_case(target['name'])

        plan.append({
            'key': k,
            'target_id': target['id'],
            'target_name_old': target['name'],
            'target_name_new': best_name,
            'losers': [m for m in members if m['id'] != target['id']],
            'move_res': sum(m['n_res'] for m in members if m['id'] != target['id']),
            'move_ath': sum(m['n_ath'] for m in members if m['id'] != target['id']),
        })

    plan.sort(key=lambda p: -(p['move_res']))
    tot_del = sum(len(p['losers']) for p in plan)
    tot_res = sum(p['move_res'] for p in plan)
    tot_ath = sum(p['move_ath'] for p in plan)

    logger.info('Dublettgrupper:            %d', len(plan))
    logger.info('Klubber som slås sammen:   %d', tot_del)
    logger.info('Resultater som flyttes:    %d', tot_res)
    logger.info('Utøvere som flyttes:       %d', tot_ath)
    logger.info('')

    for p in plan:
        rename = '' if p['target_name_new'] == p['target_name_old'] \
                 else f"   (navn endres: «{p['target_name_old']}» -> «{p['target_name_new']}»)"
        logger.info('BEHOLD «%s»%s', p['target_name_new'], rename)
        for l in p['losers']:
            logger.info('   slås inn: «%s» [%d res, %d utø]', l['name'], l['n_res'], l['n_ath'])

    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    backup.write_text(json.dumps({'generated_at': TIMESTAMP, 'plan': plan},
                                 ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info('')
    logger.info('Sikkerhetskopi av planen: %s', backup)

    if not args.apply:
        logger.info('DRY-RUN — ingenting er endret. Kjør med --apply for å utføre.')
        return

    if not args.yes:
        print(f'\nDette slår sammen {tot_del} klubber og flytter {tot_res} resultater.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            logger.info('Avbrutt av bruker.')
            return

    moved_res = moved_ath = deleted = renamed = 0
    for p in plan:
        for l in p['losers']:
            if l['n_res']:
                r = sb.table('results').update({'club_id': p['target_id']})\
                      .eq('club_id', l['id']).execute()
                moved_res += len(r.data)
            if l['n_ath']:
                a = sb.table('athletes').update({'current_club_id': p['target_id']})\
                      .eq('current_club_id', l['id']).execute()
                moved_ath += len(a.data)
            sb.table('clubs').delete().eq('id', l['id']).execute()
            deleted += 1
        if p['target_name_new'] != p['target_name_old']:
            sb.table('clubs').update({'name': p['target_name_new']})\
              .eq('id', p['target_id']).execute()
            renamed += 1

    logger.info('')
    logger.info('Resultater flyttet:      %d', moved_res)
    logger.info('Utøvere flyttet:         %d', moved_ath)
    logger.info('Klubber slettet:         %d', deleted)
    logger.info('Klubbnavn korrigert:     %d', renamed)
    logger.info('Ferdig. Logg: %s', LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log')


if __name__ == '__main__':
    main()
