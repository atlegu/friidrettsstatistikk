"""
Slå sammen klubbene du har merket i gjennomgangslisten.

ARBEIDSFLYT
-----------
1. Åpne CSV-en fra `finn_klubbdubletter.py` i Excel eller Numbers:

       scraper/opprydding/klubbdubletter_<tidspunkt>.csv

2. Legg til en kolonne helt til høyre med overskriften **handling**.

3. Skriv én av disse i hver rad du har tatt stilling til:

       ja        slå sammen. Den mindre posten forsvinner, resultatene
                 flyttes til den større.
       ja-motsatt  slå sammen, men behold den MINDRE posten som den
                 gjeldende. Brukes når den lille har riktig navn.
       nei       ikke slå sammen. La begge stå.
       (tom)     ikke bestemt ennå. Hoppes over.

4. Lagre som CSV og kjør:

       python slaa_sammen_gjennomgatte.py opprydding/filen.csv           # dry-run
       python slaa_sammen_gjennomgatte.py opprydding/filen.csv --apply

Du trenger ikke fylle ut alle radene. Kjør så mange ganger du vil — rader uten
`handling` røres ikke, og rader som allerede er slått sammen hoppes over.

HVA SOM SKJER
-------------
For hvert par som er merket:

  * `results.club_id` flyttes fra den tapende til den vinnende klubben
  * `athletes.current_club_id` flyttes tilsvarende
  * den tapende klubbraden slettes

Bare disse to kolonnene peker på klubber. Alt logges, og hele planen lagres
som sikkerhetskopi før noe endres.
"""

import argparse
import csv
import json
import logging
import os
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
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(LOG_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.log',
                                  encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

sb: Client = create_client(os.environ['SUPABASE_URL'],
                           os.environ['SUPABASE_SERVICE_KEY'])

JA = {'ja', 'j', 'x', 'slå sammen', 'sla sammen', 'merge'}
JA_MOTSATT = {'ja-motsatt', 'motsatt', 'ja motsatt', 'behold liten'}
NEI = {'nei', 'n', 'behold', 'la stå', 'la sta'}


def les_plan(sti: Path):
    """Les gjennomgått CSV og gjør den om til en liste med sammenslåinger."""
    with open(sti, encoding='utf-8-sig') as fh:
        rader = list(csv.DictReader(fh))

    if not rader or 'handling' not in rader[0]:
        raise SystemExit(
            'Fant ingen kolonne «handling» i CSV-en.\n'
            'Legg til en kolonne med den overskriften og skriv ja/nei i radene '
            'du har tatt stilling til. Se toppen av dette skriptet.')

    plan, nei, ubesluttet, ugyldig = [], 0, 0, []
    for i, r in enumerate(rader, start=2):
        h = (r.get('handling') or '').strip().lower()
        if not h:
            ubesluttet += 1
            continue
        if h in NEI:
            nei += 1
            continue
        if h in JA:
            vinner, taper = 'stor', 'liten'
        elif h in JA_MOTSATT:
            vinner, taper = 'liten', 'stor'
        else:
            ugyldig.append((i, r.get('handling')))
            continue
        plan.append({
            'vinner_id': r[f'id_{vinner}'], 'vinner_navn': r[f'klubb_{vinner}'],
            'taper_id': r[f'id_{taper}'], 'taper_navn': r[f'klubb_{taper}'],
            'res_taper': int(r[f'res_{taper}']),
            'felles_utovere': int(r['felles_utovere']),
        })
    return plan, nei, ubesluttet, ugyldig


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('csv', type=Path, help='Gjennomgått CSV med kolonnen «handling»')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--yes', action='store_true')
    args = ap.parse_args()

    plan, nei, ubesluttet, ugyldig = les_plan(args.csv)

    logger.info('Gjennomgått liste: %s', args.csv)
    logger.info('   merket for sammenslåing : %d', len(plan))
    logger.info('   merket «nei»            : %d', nei)
    logger.info('   ikke besluttet          : %d', ubesluttet)
    for linje, verdi in ugyldig:
        logger.warning('   linje %d: forstår ikke «%s» — hoppet over', linje, verdi)

    if not plan:
        logger.info('Ingenting å gjøre.')
        return

    # Samme klubb kan stå i flere par. Å slette den to ganger går galt.
    sett = set()
    trygg = []
    for p in plan:
        if p['taper_id'] in sett or p['vinner_id'] in sett:
            logger.warning('   %s er allerede med i en annen sammenslåing — '
                           'ta den i neste kjøring', p['taper_navn'])
            continue
        sett.add(p['taper_id'])
        trygg.append(p)
    plan = trygg

    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    backup.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info('Sikkerhetskopi av planen: %s', backup)

    logger.info('')
    for p in plan:
        logger.info('   %-34s <- %-34s (%d res., %d felles utøvere)',
                    p['vinner_navn'][:34], p['taper_navn'][:34],
                    p['res_taper'], p['felles_utovere'])

    if not args.apply:
        logger.info('')
        logger.info('DRY-RUN. Kjør med --apply for å utføre.')
        return

    if not args.yes:
        print(f'\nDette slår sammen {len(plan)} klubbpar og sletter '
              f'{len(plan)} klubbrader.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            return

    for n, p in enumerate(plan, start=1):
        r = sb.table('results').update({'club_id': p['vinner_id']}) \
              .eq('club_id', p['taper_id']).execute()
        a = sb.table('athletes').update({'current_club_id': p['vinner_id']}) \
              .eq('current_club_id', p['taper_id']).execute()
        sb.table('clubs').delete().eq('id', p['taper_id']).execute()
        logger.info('%2d/%d  %s <- %s  (%d resultater, %d utøvere flyttet)',
                    n, len(plan), p['vinner_navn'], p['taper_navn'],
                    len(r.data or []), len(a.data or []))

    logger.info('')
    logger.info('Ferdig. %d klubbpar slått sammen.', len(plan))
    logger.info('Husk å oppdatere forsidetellerne:')
    logger.info('   python -c "import update_results as u; u.oppdater_forsidetellere()"')


if __name__ == '__main__':
    main()
