"""
Rydd utøvernavn: komma i stedet for punktum, klubbnavn og nasjonalitet som
har havnet inne i navnestrengen.

KATEGORIER
----------
A. «Hedda A, Grønnern»          -> «Hedda A. Grønnern»
   Kilden skriver komma der det skal stå punktum etter en initial. Gjelder
   også flere initialer: «Sigmund A,K Forberg», «Synne I, B, Lacroise».

B. «Helle Haukås, Eidsvåg IL»   -> «Helle Haukås»
   Klubbnavnet har lekket inn i navnet. Fjernes bare når teksten etter komma
   er et klubbnavn som faktisk finnes i basen — ellers kan vi kappe et ekte
   etternavn.

C. «Vincent Scillitani (Italia)» -> navn «Vincent Scillitani», nationality ITA
   «Jonas Legernes, SWE»         -> navn «Jonas Legernes», nationality SWE
   Nasjonalitet hører hjemme i `athletes.nationality`, ikke i navnet. Da blir
   den også brukbar til flagging av utenlandske utøvere i norske klubber,
   jf. kravspekkens §7.

RØRES IKKE
----------
Pikenavn i parentes — «Toril Lauritsen (Nyborg)», «Per Linge (Syversen)».
Det er reell informasjon om navneendring, jf. kravspekkens §9, og skal
bevares. Presentasjonen av dem er et frontend-spørsmål, ikke et datafeil.

BRUK
----
    python rydd_utovernavn.py                # dry-run (standard)
    python rydd_utovernavn.py --apply
    python rydd_utovernavn.py --apply --yes
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
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log',
                                  encoding='utf-8')])
logger = logging.getLogger(__name__)

# Landnavn kilden skriver ut i klartekst
LAND = {
    'italia': 'ITA', 'sverige': 'SWE', 'danmark': 'DEN', 'finland': 'FIN',
    'usa': 'USA', 'england': 'GBR', 'tyskland': 'GER', 'frankrike': 'FRA',
    'polen': 'POL', 'nederland': 'NED', 'belgia': 'BEL', 'spania': 'ESP',
    'island': 'ISL', 'estland': 'EST', 'latvia': 'LAT', 'litauen': 'LTU',
}

INITIAL_KOMMA = re.compile(r'(?:(?<=\s)|(?<=^)|(?<=\.))([A-ZÆØÅ])\s*,\s*')
NASJ_PARENTES = re.compile(r'\s*\(([A-ZÆØÅ]{3})\)\s*$')
NASJ_KOMMA = re.compile(r'\s*,\s*([A-ZÆØÅ]{3})\s*$')
LAND_PARENTES = re.compile(r'\s*\(([A-Za-zÆØÅæøå]{4,})\)\s*$')


def rydd(navn: str, klubbnavn: set):
    """Returnerer (nytt_navn, nasjonalitet, [begrunnelser])."""
    original, nasj, hvorfor = navn, None, []

    # C1: nasjonalitet som trebokstavskode
    m = NASJ_PARENTES.search(navn) or NASJ_KOMMA.search(navn)
    if m and m.group(1) != 'NOR':
        nasj = m.group(1)
        navn = navn[:m.start()].strip()
        hvorfor.append(f'nasjonalitet {nasj}')
    elif m:
        navn = navn[:m.start()].strip()
        hvorfor.append('fjernet (NOR)')

    # C2: land skrevet ut. Pikenavn i parentes må ikke rammes, så bare ord
    # som står i landlisten godtas.
    m = LAND_PARENTES.search(navn)
    if m and m.group(1).lower() in LAND:
        nasj = LAND[m.group(1).lower()]
        navn = navn[:m.start()].strip()
        hvorfor.append(f'land {m.group(1)} -> {nasj}')

    # B: klubbnavn etter komma
    if ',' in navn:
        hode, hale = navn.rsplit(',', 1)
        if hale.strip() in klubbnavn:
            navn = hode.strip()
            hvorfor.append(f'fjernet klubb «{hale.strip()}»')

    # A: initial med komma i stedet for punktum
    ny = navn
    for _ in range(4):                      # «Synne I, B, Lacroise» krever flere runder
        neste = INITIAL_KOMMA.sub(r'\1. ', ny)
        if neste == ny:
            break
        ny = neste
    if ny != navn:
        navn = ny
        hvorfor.append('komma etter initial -> punktum')

    navn = re.sub(r'\s+', ' ', navn).strip()
    return (navn if navn != original or nasj else None), nasj, hvorfor


def fetch_all(sb: Client, tabell: str, kolonner: str, chunk: int = 1000):
    rader, siste = [], '00000000-0000-0000-0000-000000000000'
    while True:
        res = (sb.table(tabell).select(kolonner)
                 .gt('id', siste).order('id').limit(chunk).execute())
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
    logger.info('Rydd utøvernavn — modus: %s', 'APPLY' if args.apply else 'DRY-RUN')

    klubbnavn = {c['name'].strip() for c in fetch_all(sb, 'clubs', 'id,name')
                 if c['name']}
    logger.info('Klubbnavn lastet: %d', len(klubbnavn))

    utovere = [a for a in fetch_all(sb, 'athletes', 'id,full_name,first_name,last_name,nationality')
               if a['full_name'] and re.search(r'[,()]', a['full_name'])]
    logger.info('Utøvere med komma eller parentes i navnet: %d', len(utovere))

    plan, teller = [], defaultdict(int)
    for a in utovere:
        nytt, nasj, hvorfor = rydd(a['full_name'], klubbnavn)
        if not hvorfor:
            continue
        for h in hvorfor:
            teller[h.split(' ')[0] if h.startswith(('nasjonalitet', 'land'))
                   else h.split('«')[0].strip()] += 1
        plan.append({'id': a['id'], 'fra': a['full_name'], 'til': nytt or a['full_name'],
                     'nasjonalitet': nasj, 'hvorfor': hvorfor})

    logger.info('')
    logger.info('Navn som endres: %d', len(plan))
    for h, n in sorted(teller.items(), key=lambda x: -x[1]):
        logger.info('   %-34s %d', h, n)

    urort = [a['full_name'] for a in utovere
             if not rydd(a['full_name'], klubbnavn)[2]]
    logger.info('')
    logger.info('Røres ikke (pikenavn o.l.): %d', len(urort))
    for n in urort[:10]:
        logger.info('   %s', n)

    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    backup.write_text(json.dumps({'generated_at': TIMESTAMP, 'plan': plan,
                                  'urort': urort}, ensure_ascii=False, indent=2),
                      encoding='utf-8')
    logger.info('Sikkerhetskopi: %s', backup)

    if not args.apply:
        logger.info('')
        logger.info('DRY-RUN — eksempler:')
        for p in plan[:15]:
            nasj = f'  [nasjonalitet {p["nasjonalitet"]}]' if p['nasjonalitet'] else ''
            logger.info('   %-46s -> %s%s', p['fra'][:46], p['til'], nasj)
        logger.info('Kjør med --apply for å utføre.')
        return

    if not args.yes:
        print(f'\nDette endrer {len(plan)} utøvernavn.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            return

    endret = 0
    for p in plan:
        # full_name er en generert kolonne: (first_name || ' ' || last_name).
        # Den kan ikke settes direkte — vi setter delene, så følger den etter.
        deler = p['til'].split()
        oppd = {'first_name': deler[0] if deler else '',
                'last_name': ' '.join(deler[1:]) if len(deler) > 1 else ''}
        if p['nasjonalitet']:
            oppd['nationality'] = p['nasjonalitet']
        sb.table('athletes').update(oppd).eq('id', p['id']).execute()
        endret += 1
        if endret % 50 == 0:
            logger.info('  ... %d/%d', endret, len(plan))

    logger.info('Navn ryddet: %d', endret)


if __name__ == '__main__':
    main()
