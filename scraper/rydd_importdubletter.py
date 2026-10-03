"""Fjern dublettene fra importkjoeringene 24.08-06.09.2026.

BAKGRUNN
--------
Historiske sesonger ble hentet paa nytt 24.08-06.09.2026 (401 108 rader). 292 460 av dem
hadde en eldre tvilling: samme utoever, oevelse og resultat innen fem dager i samme stevne.
Flerdagsstevner ligger i basen som én post per dag med riktig dato; importen ga alle kildens
resultater startdatoen og la dem i posten med kildens stevne-id, og avstemmingen saa bare
den posten - dag 2, 3 ... kom inn paa nytt med feil dato (Framolekene 2014: 906 rader datert
29.05). Dessuten kom rader inn paa nytt i samme post der plass eller vind var ulik.
Roten er rettet i update_results.py (soeskenposter sjekkes foer innsetting).

REGEL (funksjonen rydd_importdubletter i basen, migrations/importdubletter.sql)
-----
  En rad N lagt inn i vinduet er en dublett naar en ELDRE rad E fra en annen importdag har
  samme utoever, oevelse og resultatverdi, dato innen +-5 dager og ligger i samme stevne
  (samme post, samme navn med sted foran fjernet, eller samme sted). E beholdes (riktig dato),
  N slettes. Én-til-én per importdag: hver eldre rad forklarer hoeyst én ny rad fra samme
  kjoering, saa forsoek og finale med lik tid blir staaende. Vind og runde kopieres til E der
  de mangler (vind, runde, plass). Slettede rader lagres i opprydding_importdubletter (kan legges tilbake).
  Stevneposter som blir tomme slettes; har de kildens stevne-id, faar soeskenposten et alias
  i stevne_alias, saa importen ikke oppretter dem paa nytt.

KJOERING
--------
    python rydd_importdubletter.py              # toerrkjoering, bare tall
    python rydd_importdubletter.py --apply
    python rydd_importdubletter.py --apply --runder 2   # andre runde tar rader hvis beste
                                                        # tvilling ble brukt i foerste
Alt logges til logs/.
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOGG = Path(__file__).parent / 'logs'; LOGG.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(LOGG / f'rydd_importdubletter_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)

START = datetime(2026, 8, 24, tzinfo=timezone.utc)
SLUTT = datetime(2026, 9, 7, tzinfo=timezone.utc)
STEG = timedelta(minutes=15)
FELT = ('kandidater', 'valgt', 'slettet', 'vind_runde_plass_kopiert', 'kopiering_feilet')


def kjoer_vindu(fra, til, dry, sum_):
    """Ett vindu; deles i to om basen bruker for lang tid (gatewayen kutter etter 120 s)."""
    try:
        res = sb.rpc('rydd_importdubletter', {'p_fra': fra.isoformat(), 'p_til': til.isoformat(),
                                              'p_dry': dry}).execute().data
    except Exception as e:
        if til - fra <= timedelta(minutes=1):
            log.error('  %s - %s feilet: %s', fra, til, str(e)[:200])
            sum_['feilede_vinduer'] = sum_.get('feilede_vinduer', 0) + 1
            return
        mid = fra + (til - fra) / 2
        log.info('  %s - %s for tungt (%s), deles i to', fra, til, str(e)[:80])
        kjoer_vindu(fra, mid, dry, sum_)
        kjoer_vindu(mid, til, dry, sum_)
        return
    for f in FELT:
        sum_[f] = sum_.get(f, 0) + int(res.get(f, 0))
    if res.get('kandidater'):
        log.info('  %s  %s', fra.strftime('%Y-%m-%d %H:%M'), res)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='slett (uten flagget: bare tall)')
    ap.add_argument('--runder', type=int, default=1, help='antall runder over perioden (standard 1)')
    args = ap.parse_args()
    dry = not args.apply
    log.info('Dubletter fra importene 24.08-06.09.2026 - %s', 'TOERRKJOERING' if dry else 'SLETTER')
    totalt = {}
    for runde in range(1, args.runder + 1):
        sum_ = {}
        t = START
        while t < SLUTT:
            kjoer_vindu(t, min(t + STEG, SLUTT), dry, sum_)
            t += STEG
        log.info('Runde %d: %s', runde, sum_)
        for k, v in sum_.items():
            totalt[k] = totalt.get(k, 0) + v
        if dry or not sum_.get('slettet'):
            break
    stevner = sb.rpc('rydd_tomme_importstevner', {'p_dry': dry}).execute().data
    log.info('Tomme stevneposter: %s', stevner)
    log.info('TOTALT: %s', totalt)
    if dry:
        log.info('Toerrkjoering: tallene for valgt er et overslag (samme eldre rad kan telles i to vinduer).')


if __name__ == '__main__':
    main()
