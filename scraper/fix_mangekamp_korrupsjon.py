"""
Reparer mangekamp-korrupsjon: utøvernavn, klubb og delresultater slått sammen
til ett felt ved import.

BAKGRUNN
--------
Ved import av mangekampstevner har parseren feilet og lagt hele strengen
"Navn, Klubb<delresultater>" inn i athletes.full_name, mens halen av strengen
er blitt opprettet som en egen "klubb". Eksempel:

    full_name : "Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4"
    klubb     : "61"

Resultatet er 660 falske utøverposter (hver med nøyaktig ett resultat) og
133 falske klubber. Det ekte navnet og den ekte klubben ligger inne i den
korrupte strengen og kan gjenvinnes.

HVA SKRIPTET GJØR
-----------------
1. Finner alle utøvere der full_name inneholder siffer.
2. Trekker ut ekte navn, ekte klubb og eventuell nasjonalitet.
3. Slår opp den ekte utøveren (navn + fødselsår) og den ekte klubben.
4. Flytter resultatet over til riktig utøver og klubb.
5. Sletter den falske utøverposten og etterlatte falske klubber.

Alt som ikke kan matches entydig blir stående urørt og rapportert.

BRUK
----
    python fix_mangekamp_korrupsjon.py                # dry-run (standard)
    python fix_mangekamp_korrupsjon.py --apply        # utfører endringene
    python fix_mangekamp_korrupsjon.py --apply --yes  # uten bekreftelse
"""

import argparse
import json
import logging
import os
import re
import sys
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


# --- Uttrekk fra korrupt streng -------------------------------------------

# Halen som skal av klubbnavnet: statuskoder og skilletegn som er blitt hengende
# igjen etter at delresultatene ble kuttet vekk.
CLUB_TAIL = re.compile(r'(DNF|DNS|DQ|NM|\(|\)|-|,|\.|\s)+$')
NATIONALITY = re.compile(r'\(([A-Z]{3})\)\s*$')


def split_corrupt(full_name: str):
    """Del "Navn(NAT), Klubb<søppel>" i (navn, nasjonalitet, klubb)."""
    if ',' not in full_name:
        return None, None, None

    head, tail = full_name.split(',', 1)
    name = head.strip()

    nationality = None
    m = NATIONALITY.search(name)
    if m:
        nationality = m.group(1)
        name = NATIONALITY.sub('', name).strip()

    # Klubben slutter der delresultatene begynner (første siffer).
    club = re.sub(r'[0-9].*$', '', tail).strip()
    club = CLUB_TAIL.sub('', club).strip()

    return (name or None), nationality, (club or None)


# --- Databaseoppslag ------------------------------------------------------

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
    ap.add_argument('--apply', action='store_true',
                    help='Utfør endringene. Uten dette flagget kjøres kun dry-run.')
    ap.add_argument('--yes', action='store_true',
                    help='Hopp over interaktiv bekreftelse.')
    args = ap.parse_args()

    url, key = os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY')
    if not url or not key:
        logger.error('Mangler SUPABASE_URL / SUPABASE_SERVICE_KEY i .env')
        sys.exit(1)
    sb = create_client(url, key)

    mode = 'APPLY' if args.apply else 'DRY-RUN'
    logger.info('=' * 72)
    logger.info('Mangekamp-reparasjon — modus: %s', mode)
    logger.info('=' * 72)

    # 1. Hent korrupte utøvere
    corrupt = [a for a in fetch_all(sb, 'athletes', 'id,full_name,birth_year,gender,nationality')
               if a['full_name'] and re.search(r'[0-9]', a['full_name'])]
    logger.info('Korrupte utøverposter funnet: %d', len(corrupt))

    # 2. Oppslagstabeller over ekte utøvere og klubber
    all_ath = fetch_all(sb, 'athletes', 'id,full_name,birth_year')
    corrupt_ids = {a['id'] for a in corrupt}

    by_name = {}
    for a in all_ath:
        if a['id'] in corrupt_ids or not a['full_name']:
            continue
        by_name.setdefault(a['full_name'].strip(), []).append(a)

    clubs = fetch_all(sb, 'clubs', 'id,name')
    club_by_name = {c['name'].strip(): c['id'] for c in clubs if c['name']}
    club_by_lower = {c['name'].strip().lower(): c['id'] for c in clubs if c['name']}

    # 3. Klassifiser hver korrupt post
    plan, unresolved = [], []
    for a in corrupt:
        name, nat, club = split_corrupt(a['full_name'])
        if not name:
            unresolved.append((a, 'kunne ikke dele strengen'))
            continue

        cands = by_name.get(name, [])
        exact = [c for c in cands
                 if c['birth_year'] == a['birth_year'] or c['birth_year'] is None]
        if len(exact) != 1:
            unresolved.append((a, f'{len(exact)} kandidater for «{name}»'))
            continue

        club_id = club_by_name.get(club) or club_by_lower.get((club or '').lower())
        plan.append({
            'junk_athlete_id': a['id'],
            'junk_full_name': a['full_name'],
            'real_athlete_id': exact[0]['id'],
            'real_name': name,
            'nationality': nat,
            'club_text': club,
            'club_id': club_id,
        })

    resolved_club = sum(1 for p in plan if p['club_id'])
    logger.info('Kan repareres entydig:      %d', len(plan))
    logger.info('  — med gjenfunnet klubb:   %d', resolved_club)
    logger.info('  — uten klubbtreff:        %d  (klubb settes NULL)', len(plan) - resolved_club)
    logger.info('Kan ikke repareres:         %d', len(unresolved))

    for a, why in unresolved:
        logger.warning('  UAVKLART: %s  [%s]', a['full_name'][:70], why)

    # 4. Sikkerhetskopi av alt som berøres
    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    junk_club_ids = [c['id'] for c in clubs if c['name'] and re.match(r'^[0-9]', c['name'])]
    affected_results = []
    for i in range(0, len(corrupt), 100):
        ids = [a['id'] for a in corrupt[i:i + 100]]
        affected_results.extend(
            sb.table('results').select('*').in_('athlete_id', ids).execute().data)

    backup.write_text(json.dumps({
        'generated_at': TIMESTAMP,
        'corrupt_athletes': corrupt,
        'affected_results': affected_results,
        'junk_clubs': [c for c in clubs if c['id'] in set(junk_club_ids)],
        'plan': plan,
        'unresolved': [{'athlete': a, 'reason': w} for a, w in unresolved],
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info('Sikkerhetskopi skrevet: %s (%d resultater)', backup, len(affected_results))

    if not args.apply:
        logger.info('')
        logger.info('DRY-RUN — ingenting er endret. Eksempler på planlagte endringer:')
        for p in plan[:10]:
            logger.info('  «%s»', p['junk_full_name'][:60])
            logger.info('      -> utøver: %s | klubb: %s',
                        p['real_name'], p['club_text'] or '(ingen)')
        logger.info('')
        logger.info('Kjør med --apply for å utføre.')
        return

    if not args.yes:
        print(f'\nDette flytter {len(plan)} resultater, sletter {len(plan)} falske '
              f'utøverposter og rydder {len(junk_club_ids)} falske klubber.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            logger.info('Avbrutt av bruker.')
            return

    # 5. Flytt resultater, slett falske poster
    moved = deleted_ath = 0
    for p in plan:
        upd = {'athlete_id': p['real_athlete_id'], 'club_id': p['club_id']}
        r = sb.table('results').update(upd).eq('athlete_id', p['junk_athlete_id']).execute()
        moved += len(r.data)
        sb.table('athletes').delete().eq('id', p['junk_athlete_id']).execute()
        deleted_ath += 1
        if deleted_ath % 100 == 0:
            logger.info('  ... %d/%d behandlet', deleted_ath, len(plan))

    logger.info('Resultater flyttet: %d', moved)
    logger.info('Falske utøvere slettet: %d', deleted_ath)

    # 6. Slett falske klubber som nå er tomme
    deleted_clubs = 0
    for cid in junk_club_ids:
        still = sb.table('results').select('id', count='exact').eq('club_id', cid)\
                  .limit(1).execute()
        refs = sb.table('athletes').select('id', count='exact')\
                 .eq('current_club_id', cid).limit(1).execute()
        if (still.count or 0) == 0 and (refs.count or 0) == 0:
            sb.table('clubs').delete().eq('id', cid).execute()
            deleted_clubs += 1
        else:
            logger.warning('  Beholder klubb %s — fortsatt %s resultater, %s utøvere',
                           cid, still.count, refs.count)
    logger.info('Falske klubber slettet: %d av %d', deleted_clubs, len(junk_club_ids))
    logger.info('Ferdig. Logg: %s', LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log')


if __name__ == '__main__':
    main()
