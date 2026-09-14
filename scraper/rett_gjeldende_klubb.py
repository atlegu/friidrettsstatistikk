"""
Rett `athletes.current_club_id` for utøvere som har byttet klubb.

BAKGRUNN
--------
Gjeldende klubb skal være klubben fra utøverens **nyeste** resultat. Importen
satte den i stedet fra det stevnet som tilfeldigvis ble behandlet først i en
kjøring, uten å se på dato:

    _update_athlete_club(athlete_id, club_id)   # klubb fra dette stevnet
    _athlete_club_updated.add(athlete_id)       # og så låst resten av kjøringen

Da sesongene 2013–2018 ble kontrollert mot kilden, stemplet det utøvere med
klubber de forlot for år siden. Sondre Guttormsen sto på Ski IL Friidrett, som
han forlot i 2018, mens broren Simen — som byttet samtidig — sto riktig.

Roten er rettet i `update_results.py`, som nå utleder klubben fra nyeste
resultat etter hver kjøring i stedet for å gjette underveis. Dette skriptet
rydder opp i det som allerede er feil.

METODE
------
Gjeldende klubb settes til den klubben utøveren har **flest resultater for i
sin siste aktive sesong**.

«Nyeste resultat vinner» ble prøvd først og forkastet. Den flyttet utøvere fra
klubben sin til en skole hvis siste start var et skolestevne
(«Austevoll IK Friidrett» -> «Austevoll Ungdomsskule»), og til «ukjent» der
siste resultat manglet klubbnavn. Et klubbskifte viser seg ved at utøveren
konkurrerer for den nye klubben gjentatte ganger, ikke én gang.

Skoler og «ukjent» er utelatt som mål. Ingen data hentes utenfra.

Arbeidet gjøres i uuid-biter, fordi en spørring over hele `results`
tidsavbrytes.

BRUK
----
    python rett_gjeldende_klubb.py                # dry-run (standard)
    python rett_gjeldende_klubb.py --apply
    python rett_gjeldende_klubb.py --apply --yes
"""

import argparse
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

# 256 biter over uuid-rommet. En sekstendel tidsavbrytes i PostgREST, som har
# kortere grense enn SQL-editoren.
BITER = [f'{i:02x}' for i in range(256)]


def grense(heks: str) -> str:
    return f'{heks}000000-0000-0000-0000-000000000000'


def finn_alle():
    """Hent alle utøvere med feil gjeldende klubb, bit for bit."""
    funn = []
    for i, h in enumerate(BITER):
        fra = grense(h)
        til = grense(BITER[i + 1]) if i + 1 < len(BITER) else 'ffffffff-ffff-ffff-ffff-ffffffffffff'
        rader = sb.rpc('finn_feil_gjeldende_klubb', {'fra': fra, 'til': til}).execute().data
        funn.extend(rader)
        if (i + 1) % 32 == 0 or i == len(BITER) - 1:
            logger.info(f'  {i + 1:3d}/{len(BITER)} biter kontrollert — {len(funn)} med feil klubb')
    return funn


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--yes', action='store_true')
    ap.add_argument('--min-resultater', type=int, default=2,
                    help='Krev minst så mange resultater for den nye klubben i '
                         'siste sesong. Standard 2: ett enkelt resultat kan være '
                         'en gjesteopptreden og flyttes ikke uten gjennomgang.')
    args = ap.parse_args()

    logger.info('Rett gjeldende klubb — modus: %s', 'APPLY' if args.apply else 'DRY-RUN')
    alle = finn_alle()
    funn = [f for f in alle if f['antall_i_sesongen'] >= args.min_resultater]
    holdt = [f for f in alle if f['antall_i_sesongen'] < args.min_resultater]

    logger.info('')
    logger.info('Utøvere med feil gjeldende klubb: %d', len(alle))
    logger.info('   rettes nå (minst %d resultater): %d', args.min_resultater, len(funn))
    logger.info('   holdt tilbake til gjennomgang: %d', len(holdt))
    if not funn:
        return

    # De vanligste feilkoblingene sier noe om hvor problemet stammer fra
    par = {}
    for f in funn:
        n = (f['klubb_na_navn'], f['klubb_riktig_navn'])
        par[n] = par.get(n, 0) + 1

    logger.info('')
    logger.info('Hyppigste overganger som ikke var registrert:')
    for (fra, til), n in sorted(par.items(), key=lambda x: -x[1])[:12]:
        logger.info('   %-34s -> %-34s %d', (fra or '—')[:34], (til or '—')[:34], n)

    backup = BACKUP_DIR / f'{SCRIPT_NAME}_{TIMESTAMP}.json'
    backup.write_text(json.dumps({'rettes': funn, 'holdt_tilbake': holdt},
                                 ensure_ascii=False, indent=2, default=str),
                      encoding='utf-8')
    logger.info('')
    logger.info('Sikkerhetskopi med begge grupper: %s', backup)

    if not args.apply:
        logger.info('')
        logger.info('DRY-RUN — eksempler:')
        for f in sorted(funn, key=lambda x: -x['antall_i_sesongen'])[:15]:
            logger.info('   %-28s %-26s -> %-26s %s (%d res.)',
                        f['navn'][:28], (f['klubb_na_navn'] or '—')[:26],
                        (f['klubb_riktig_navn'] or '—')[:26],
                        f['siste_sesong'], f['antall_i_sesongen'])
        logger.info('Kjør med --apply for å utføre.')
        return

    if not args.yes:
        print(f'\nDette endrer gjeldende klubb for {len(funn)} utøvere.')
        if input('Skriv "JA" for å fortsette: ').strip() != 'JA':
            return

    endret = 0
    for f in funn:
        sb.table('athletes').update(
            {'current_club_id': f['klubb_riktig']}
        ).eq('id', f['athlete_id']).execute()
        endret += 1
        if endret % 250 == 0:
            logger.info('  ... %d/%d', endret, len(funn))

    logger.info('Gjeldende klubb rettet for %d utøvere', endret)


if __name__ == '__main__':
    main()
