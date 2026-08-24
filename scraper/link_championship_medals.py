"""
Koble NM-medaljer til utøvere i `athletes`.

BAKGRUNN
--------
`championship_medals` har navnet på medaljøren som tekst, og en `athlete_id`
som skal peke til utøveren. Per 2026-08-24 manglet koblingen på 5 102 av
13 609 medaljer. Uten den vises ikke medaljene på utøverprofilen.

METODE
------
Navn normaliseres (små bokstaver, aksenter foldet, tegnsetting fjernet) og
slås opp mot utøverne. Et treff godtas bare når det er **entydig**, og når
utøveren plausibelt kan ha tatt medaljen:

  * kjønn må stemme der begge kilder har det
  * utøveren må ha resultater innenfor ±5 år av mesterskapsåret,
    ELLER et fødselsår som gir alder mellom 15 og 55 i mesterskapsåret

Er det flere kandidater igjen etter dette, kobles ingen. To personer med
samme navn er vanlig nok i norsk friidrett til at gjetting ikke forsvares —
en feilkoblet medalje er verre enn en ukoblet.

Medaljer fra før 1970 har sjelden en utøverpost å koble til i det hele tatt;
resultatdataene starter i praksis senere. Det er forventet, ikke en feil.

BRUK
----
    python link_championship_medals.py                # dry-run (standard)
    python link_championship_medals.py --apply
    python link_championship_medals.py --apply --yes
"""

import argparse
import json
import logging
import os
import re
import sys
import time
import unicodedata
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
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log',
                                  encoding='utf-8')])
logger = logging.getLogger(__name__)

AAR_SLINGRING = 5      # resultater innenfor ±5 år av mesterskapet
ALDER_MIN, ALDER_MAX = 15, 55


def normaliser(navn: str) -> str:
    """Små bokstaver, aksenter foldet, alt annet enn bokstaver og tall vekk."""
    s = navn or ''
    ut = []
    for tegn in unicodedata.normalize('NFD', s.lower()):
        if tegn in 'æøå' or unicodedata.category(tegn) != 'Mn':
            ut.append(tegn)
    return re.sub(r'[^0-9a-zæøå]+', ' ', ''.join(ut)).strip()


def fetch_all(sb: Client, tabell: str, kolonner: str, chunk: int = 1000, retries: int = 4):
    """Nøkkelbasert paginering — `.range()` uten sortering mister rader."""
    rader, siste = [], '00000000-0000-0000-0000-000000000000'
    while True:
        for forsok in range(retries):
            try:
                res = (sb.table(tabell).select(kolonner)
                         .gt('id', siste).order('id').limit(chunk).execute())
                break
            except Exception:
                if forsok == retries - 1:
                    raise
                time.sleep(2 * (forsok + 1))
        if not res.data:
            return rader
        rader.extend(res.data)
        siste = res.data[-1]['id']
        if len(res.data) < chunk:
            return rader


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--yes', action='store_true')
    args = ap.parse_args()

    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
    logger.info('=' * 72)
    logger.info('Koble NM-medaljer til utøvere — modus: %s',
                'APPLY' if args.apply else 'DRY-RUN')
    logger.info('=' * 72)

    medaljer = [m for m in fetch_all(sb, 'championship_medals',
                                     'id,athlete_id,athlete_name,year,gender,event_name,medal')
                if not m['athlete_id']]
    logger.info('Medaljer uten kobling: %d', len(medaljer))

    utovere = fetch_all(sb, 'athletes', 'id,full_name,birth_year,gender')
    per_navn = defaultdict(list)
    for a in utovere:
        per_navn[normaliser(a['full_name'])].append(a)
    logger.info('Utøvere i basen: %d', len(utovere))

    # Årsspenn for resultatene til hver utøver
    spenn = {}
    for r in fetch_all(sb, 'results', 'id,athlete_id,date'):
        if not r['date']:
            continue
        y = int(r['date'][:4])
        lo, hi = spenn.get(r['athlete_id'], (y, y))
        spenn[r['athlete_id']] = (min(lo, y), max(hi, y))
    logger.info('Utøvere med resultater: %d', len(spenn))

    def plausibel(a, ar):
        if a['id'] in spenn:
            lo, hi = spenn[a['id']]
            if lo - AAR_SLINGRING <= ar <= hi + AAR_SLINGRING:
                return True
        by = a.get('birth_year')
        if by and ALDER_MIN <= ar - by <= ALDER_MAX:
            return True
        return False

    plan, arsak = [], defaultdict(int)
    for m in medaljer:
        kandidater = per_navn.get(normaliser(m['athlete_name']), [])
        if not kandidater:
            arsak['ingen utøver med det navnet'] += 1
            continue
        if m.get('gender'):
            med_kjonn = [a for a in kandidater
                         if not a.get('gender') or a['gender'] == m['gender']]
            if med_kjonn:
                kandidater = med_kjonn
        aktuelle = [a for a in kandidater if plausibel(a, m['year'])]
        if not aktuelle:
            arsak['ingen kandidat passer i tid'] += 1
            continue
        if len(aktuelle) > 1:
            arsak['flere kandidater — ikke entydig'] += 1
            continue
        plan.append((m, aktuelle[0]))

    logger.info('')
    logger.info('Kan kobles entydig: %d', len(plan))
    for a, n in sorted(arsak.items(), key=lambda x: -x[1]):
        logger.info('  Ikke koblet — %-32s %d', a, n)

    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    backup.write_text(json.dumps(
        {'generated_at': TIMESTAMP,
         'note': 'athlete_id var NULL for alle disse. Angring: sett tilbake til NULL.',
         'kobling': [{'medalje_id': m['id'], 'navn': m['athlete_name'],
                      'ar': m['year'], 'ovelse': m['event_name'],
                      'athlete_id': a['id']} for m, a in plan]},
        ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info('Sikkerhetskopi: %s', backup)

    if not args.apply:
        logger.info('')
        logger.info('DRY-RUN — eksempler:')
        for m, a in plan[:10]:
            logger.info('   %s (%s, %s) -> %s',
                        m['athlete_name'], m['year'], m['event_name'], a['full_name'])
        logger.info('Kjør med --apply for å utføre.')
        return

    if not args.yes:
        print(f'\nDette kobler {len(plan)} medaljer til utøvere.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            logger.info('Avbrutt av bruker.')
            return

    # Grupper på utøver, så én oppdatering dekker flere medaljer
    per_utover = defaultdict(list)
    for m, a in plan:
        per_utover[a['id']].append(m['id'])

    oppdatert = 0
    for n, (aid, medalje_ider) in enumerate(per_utover.items(), 1):
        for i in range(0, len(medalje_ider), 100):
            res = sb.table('championship_medals').update({'athlete_id': aid})\
                    .in_('id', medalje_ider[i:i + 100]).execute()
            oppdatert += len(res.data)
        if n % 250 == 0:
            logger.info('  ... %d/%d utøvere behandlet', n, len(per_utover))

    logger.info('')
    logger.info('Medaljer koblet: %d (fordelt på %d utøvere)', oppdatert, len(per_utover))
    logger.info('Ferdig. Logg: %s', LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log')


if __name__ == '__main__':
    main()
