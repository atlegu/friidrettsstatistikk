"""Fjern dubletter som bare skiller seg paa vind.

BAKGRUNN
--------
Den unike indeksen results_innhold_unik omfatter wind. Naar et stevne ble
hentet paa nytt etter at kilden hadde rettet en vindverdi, slapp den nye
raden inn ved siden av den gamle: samme utoever, oevelse, stevne, resultat og
plass - to ulike vindverdier. 187 slike par fantes 15.09.2026, fra 136
stevner 1983-2026, alle opprettet under gjenkjoeringene i 2026.

Importen avstemmer naa mot kilden foer den legger inn (se _avstem_stevne i
update_results.py), saa nye par oppstaar ikke. Dette skriptet rydder de
gamle.

REGEL, per gruppe
-----------------
  1. (fjernet)
  2. Har én rad vind og de andre ikke: radene uten vind slettes.
     Kilden maalte vinden; raden uten er den gamle.
  3. Ellers lar vi gruppen staa og lister den. Det gjelder par der begge
     har vind og ingen er avstemt (typisk foer 2011, som ikke finnes i
     kilden) - de maa vurderes for haand.

KJOERING
--------
    python rydd_innholdsdubletter.py            # toerrkjoering
    python rydd_innholdsdubletter.py --apply
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOGG = Path(__file__).parent / 'logs'; LOGG.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(LOGG / f'rydd_innholdsdubletter_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)


def hent_grupper():
    """Ferske grupper, per oevelse (hele tabellen paa én gang roek paa gatewayen)."""
    alle = []
    for e in sb.table('events').select('id,code').execute().data:
        for forsok in (1, 2, 3):
            try:
                alle.extend(sb.rpc('test_innholdsdubletter', {'p_event_id': e['id']}).execute().data)
                break
            except Exception as x:
                log.warning(f"{e['code']}: forsoek {forsok}: {str(x)[:100]}"); time.sleep(5)
    return alle


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    grupper = hent_grupper()
    log.info(f"{len(grupper)} dublettgrupper")

    slett, behold_for_haand = [], []
    for g in grupper:
        rader = list(zip(g['ids'], g['winds'], g['verifieds'], g['created_ats']))
        # Regelen «slett den som er verified=false» er tatt bort: flagget er
        # for stoeyete til aa slette paa. To rader med hver sin maalte vind kan
        # dessuten vaere forsoek og finale med samme tid - ekte resultater.
        med_vind = [r for r in rader if r[1] is not None]
        uten_vind = [r for r in rader if r[1] is None]
        if len(med_vind) == 1 and uten_vind:
            for r in uten_vind:
                slett.append((r[0], 'uten vind, kilden har vind', g))
            continue
        behold_for_haand.append(g)

    log.info(f"   slettes: {len(slett)}")
    log.info(f"   maa vurderes for haand: {len(behold_for_haand)}")

    ut = Path(__file__).parent / 'opprydding' / f'innholdsdubletter_plan_{TS}.json'
    json.dump({'slett': [{'id': i, 'grunn': gr, 'gruppe': g} for i, gr, g in slett],
               'for_haand': behold_for_haand}, open(ut, 'w'), indent=1)
    log.info(f"Plan lagret: {ut}")

    for g in behold_for_haand[:15]:
        log.info(f"   for haand: {g['performance']} pl.{g['place']} vind {g['winds']} verified {g['verifieds']}")

    if not args.apply:
        log.info("DRY-RUN. Kjoer med --apply for aa slette.")
        return
    n = 0
    for i, gr, g in slett:
        sb.table('results').delete().eq('id', i).execute(); n += 1
    log.info(f"Slettet {n} rader.")
    log.info("Husk: python -c \"import update_results as u; u.oppdater_forsidetellere()\"")


if __name__ == '__main__':
    main()
