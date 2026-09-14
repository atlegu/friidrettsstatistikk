"""
Lag en gjennomgangsliste over klubber som ser ut til å være den samme.

HVORFOR
-------
Da gjeldende klubb ble rettet 14.09.2026, var de hyppigste «klubbskiftene»
ikke skifter i det hele tatt, men to skrivemåter av samme klubb:

    Idrettslaget Skjalg        -> IL Skjalg                 48 utøvere
    Kristiansands IF Friidrett -> Kristiansands IF          34
    Lye Idrettslag             -> Lye IL                    27

Det er klubbsammenslåing, og det krever skjønn. Dette skriptet foreslår
ingenting og endrer ingenting. Det lager en liste å gå gjennom.

METODE
------
Klubbnavn normaliseres ved å fjerne organisasjonsledd (IL, IF, SK, Turn,
Idrettslag, Friidrett, Friidrettsklubb …) og tegnsetting. Klubber som faller
sammen til samme kjerne, listes som kandidater.

To signaler følger med, og de er viktigere enn navnelikheten:

  * **felles utøvere** — hvor mange utøvere har resultater for begge. Høyt tall
    peker mot dubletter, ikke mot to nabolag som bytter utøvere.
  * **overlappende år** — to poster som er aktive samtidig er oftere dubletter
    enn en klubb som byttet navn i 2014.

LES LISTEN SLIK
---------------
Navnelikhet alene er ikke bevis. «Ski IL» og «Ski IL Friidrett» kan være
hovedlaget og friidrettsgruppa, som kan være to reelle enheter. Avgjørelsen er
din; skriptet gir bare underlaget.

BRUK
----
    python finn_klubbdubletter.py            # skriver rapport og CSV
"""

import csv
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
UT_DIR = Path(__file__).parent / 'opprydding'
UT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

sb: Client = create_client(os.environ['SUPABASE_URL'],
                           os.environ['SUPABASE_SERVICE_KEY'])

# Organisasjonsledd som ikke skiller to klubber fra hverandre
LEDD = [
    'friidrettsklubb', 'friidrettsklubben', 'friidrettsgruppe', 'friidrettsgruppa',
    'friidrett', 'idrettslag', 'idrettslaget', 'idrettsforening',
    'idrettsforeningen', 'idrettsklubb', 'idrettsklubben', 'sportsklubb',
    'sportsklubben', 'sportsklub', 'turnforening', 'turn', 'atletklubb',
    'skiklubb', 'ungdomslag', 'il', 'if', 'ik', 'sk', 'fik', 'tif', 'ff', 'fk',
    'bul', 'og', 'the',
]


def normaliser(navn: str) -> str:
    """Reduser et klubbnavn til kjernen, for å finne kandidater."""
    s = navn.lower()
    s = s.replace('&', ' ').replace('/', ' ').replace('-', ' ')
    s = re.sub(r'[^\wæøå ]', ' ', s)
    ord_ = [o for o in s.split() if o and o not in LEDD]
    return ' '.join(ord_)


def hent_klubber():
    rader, siste = [], '00000000-0000-0000-0000-000000000000'
    while True:
        res = (sb.table('klubb_bruk')
                 .select('id,name,city,club_type,resultater,utovere,fra_ar,til_ar')
                 .gt('id', siste).order('id').limit(1000).execute())
        if not res.data:
            return rader
        rader.extend(res.data)
        siste = res.data[-1]['id']
        if len(res.data) < 1000:
            return rader


def felles_utovere(a_id: str, b_id: str) -> int:
    """Antall utøvere med resultater for begge klubbene."""
    r = sb.rpc('felles_utovere_klubber', {'a': a_id, 'b': b_id}).execute().data
    return r[0]['antall'] if r else 0


def main():
    klubber = [k for k in hent_klubber() if k['resultater'] > 0]
    logger.info('Klubber med resultater: %d', len(klubber))

    grupper = defaultdict(list)
    for k in klubber:
        kjerne = normaliser(k['name'])
        if len(kjerne) >= 3:                 # for korte kjerner gir støy
            grupper[kjerne].append(k)

    kandidater = {k: v for k, v in grupper.items() if len(v) > 1}
    logger.info('Navnegrupper med mer enn én klubb: %d', len(kandidater))

    rader = []
    for kjerne, medlemmer in sorted(kandidater.items(),
                                    key=lambda x: -sum(m['resultater'] for m in x[1])):
        medlemmer.sort(key=lambda m: -m['resultater'])
        storste = medlemmer[0]
        for m in medlemmer[1:]:
            felles = felles_utovere(storste['id'], m['id'])
            overlapp = (storste['fra_ar'] is not None and m['fra_ar'] is not None
                        and storste['fra_ar'] <= m['til_ar']
                        and m['fra_ar'] <= storste['til_ar'])
            rader.append({
                'kjerne': kjerne,
                'klubb_stor': storste['name'], 'res_stor': storste['resultater'],
                'ar_stor': f"{storste['fra_ar']}–{storste['til_ar']}",
                'klubb_liten': m['name'], 'res_liten': m['resultater'],
                'ar_liten': f"{m['fra_ar']}–{m['til_ar']}",
                'felles_utovere': felles,
                'overlappende_ar': 'ja' if overlapp else 'nei',
                'id_stor': storste['id'], 'id_liten': m['id'],
            })

    rader.sort(key=lambda r: (-r['felles_utovere'], -r['res_liten']))

    csv_sti = UT_DIR / f'klubbdubletter_{TIMESTAMP}.csv'
    with open(csv_sti, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rader[0]))
        w.writeheader()
        w.writerows(rader)

    logger.info('')
    logger.info('Kandidatpar: %d', len(rader))
    logger.info('   med felles utøvere: %d', len([r for r in rader if r['felles_utovere'] > 0]))
    logger.info('   uten felles utøvere: %d', len([r for r in rader if r['felles_utovere'] == 0]))
    logger.info('')
    logger.info('De tjue med flest felles utøvere:')
    logger.info('   %-32s %-32s %6s %6s %s', 'KLUBB (større)', 'KLUBB (mindre)',
                'FELLES', 'RES', 'ÅR')
    for r in rader[:20]:
        logger.info('   %-32s %-32s %6d %6d %s / %s',
                    r['klubb_stor'][:32], r['klubb_liten'][:32],
                    r['felles_utovere'], r['res_liten'], r['ar_stor'], r['ar_liten'])
    logger.info('')
    logger.info('Full liste: %s', csv_sti)


if __name__ == '__main__':
    main()
