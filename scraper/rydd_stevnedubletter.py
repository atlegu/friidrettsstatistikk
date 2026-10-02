"""Slaa sammen stevneposter som er samme stevne.

BAKGRUNN
--------
Importkjoeringene i januar 2026 la det samme stevnet inn to ganger: én post
med sted foran navnet («Bærum, Tyrvinglekene») og én uten («Tyrvinglekene»).
Begge fikk resultater, og mange resultater ligger derfor dobbelt - synlig
paa utoeversidene som to like rader fra to «stevner» samme dag. I tillegg
slo importen sammen stevner med samme navn samme dag («Treningsstevne» i
to byer) til én post. 18.09.2026: 4 925 stevnepar med felles resultater,
om lag 196 000 dobbeltrader.

Roten er rettet i update_results.py (stevnet finnes igjen paa kildens
stevne-id, og sted lagres). Dette skriptet rydder det som ligger der.

REGEL
-----
  Grunnlaget er tabellen opprydding_stevnepar: par av stevner med minst ett
  felles resultat (samme utoever, oevelse, dato og resultatverdi), pluss
  par samme dag der det ene navnet er det andre med sted foran («Fana,
  Fanalekene 2026» / «Fanalekene 2026») selv uten felles resultater - de
  to delene av samme stevne.

  Bare par med samme startdato roeres. Par der begge postene har kildens
  stevne-id roeres ikke (kilden selv lister resultatet to steder).

  Behold: posten med kildens stevne-id. Har ingen den, beholdes posten med
  sted i navnet, og ved likt navn den stoerste. Par med ulike navn og uten
  kilde-id roeres ikke.

  Tvillingene i den andre posten slettes (vind kopieres foerst dit den
  mangler). Resten av radene flyttes over BARE naar navnene er samme
  stevne (likt navn, eller sted + navn) og posten ikke inngaar i flere par
  - «Treningsstevne» samme dag som baade «Bømlo, Treningsstevne» og
  «Fredrikstad, Treningsstevne» kan vi ikke fordele, saa radene blir
  staaende under den gamle posten. Tom post slettes.

KJOERING
--------
    python rydd_stevnedubletter.py            # toerrkjoering, bare tall
    python rydd_stevnedubletter.py --apply
    python rydd_stevnedubletter.py --apply --fra 2024-01-01   # bare nyere
Alt logges til logs/, og vedtak og resultat skrives tilbake i
opprydding_stevnepar (kolonnene behold, fjern, vedtak, utfort, resultat).
"""

import argparse
import json
import logging
import os
import sys
from collections import Counter, defaultdict
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
                              logging.FileHandler(LOGG / f'rydd_stevnedubletter_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)


def hent_par(fra):
    """Hele tabellen, side for side (PostgREST gir aldri mer enn 1 000)."""
    rader, side = [], 0
    while True:
        q = sb.table('opprydding_stevnepar').select('*').order('m1').order('m2').range(side * 1000, side * 1000 + 999)
        if fra:
            q = q.gte('m1_dato', fra)
        d = q.execute().data
        rader.extend(d)
        if len(d) < 1000:
            return rader
        side += 1


def vedta(p, antall_par):
    """Returnerer (behold, fjern, flytt, vedtak). behold=None betyr hopp over."""
    if p['m1_dato'] != p['m2_dato']:
        return None, None, False, 'ulik dato, hopp over'
    e1, e2 = p['m1_ext'] is not None, p['m2_ext'] is not None
    if e1 and e2:
        return None, None, False, 'begge har kilde-id, hopp over'
    if e1 or e2:
        behold, fjern = (p['m1'], p['m2']) if e1 else (p['m2'], p['m1'])
        grunn = 'kilde-id'
    elif p['relasjon'] == 'by, navn':
        m1_har_sted = p['m1_navn'].endswith(', ' + p['m2_navn'])
        behold, fjern = (p['m1'], p['m2']) if m1_har_sted else (p['m2'], p['m1'])
        grunn = 'sted i navnet'
    elif p['relasjon'] == 'likt navn':
        behold, fjern = (p['m1'], p['m2']) if p['m1_res'] >= p['m2_res'] else (p['m2'], p['m1'])
        grunn = 'stoerst'
    else:
        return None, None, False, 'ulike navn uten kilde-id, manuelt'
    if p['relasjon'] == 'ulikt navn':
        flytt, hvorfor = False, 'resten blir staaende (ulike navn)'
    elif antall_par[fjern] > 1:
        flytt, hvorfor = False, 'resten blir staaende (flere par)'
    else:
        flytt, hvorfor = True, 'flytt resten'
    return behold, fjern, flytt, f'behold {grunn}; {hvorfor}'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='utfoer (ellers toerrkjoering)')
    ap.add_argument('--fra', help='bare par med startdato fra og med (ÅÅÅÅ-MM-DD)')
    a = ap.parse_args()

    par = hent_par(a.fra)
    par = [p for p in par if p['utfort'] is None]
    log.info('%d par aa vurdere%s', len(par), f' (fra {a.fra})' if a.fra else '')

    antall_par = Counter()
    for p in par:
        antall_par[p['m1']] += 1; antall_par[p['m2']] += 1

    plan = []
    oppsummering = defaultdict(lambda: [0, 0, 0])   # vedtak -> [par, slettes, flyttes]
    for p in par:
        behold, fjern, flytt, vedtak = vedta(p, antall_par)
        fjern_res = p['m1_res'] if fjern == p['m1'] else p['m2_res']
        o = oppsummering[vedtak]
        o[0] += 1
        if behold:
            o[1] += p['dubletter']
            if flytt:
                o[2] += fjern_res - p['dubletter']
        plan.append((p, behold, fjern, flytt, vedtak))

    log.info('PLAN')
    for vedtak, (n, slett, flytt) in sorted(oppsummering.items(), key=lambda x: -x[1][1]):
        log.info('  %-55s %5d par  %7d slettes  %7d flyttes', vedtak, n, slett, flytt)
    tot_slett = sum(v[1] for v in oppsummering.values())
    tot_flytt = sum(v[2] for v in oppsummering.values())
    log.info('  SUM: %d dobbeltrader slettes, %d rader flyttes', tot_slett, tot_flytt)

    if not a.apply:
        log.info('Toerrkjoering. Kjoer med --apply for aa utfoere.')
        return

    utfort = Counter()
    sum_res = Counter()
    for i, (p, behold, fjern, flytt, vedtak) in enumerate(plan, 1):
        if behold is None:
            sb.table('opprydding_stevnepar').update({'vedtak': vedtak}).eq('m1', p['m1']).eq('m2', p['m2']).execute()
            continue
        # Den andre posten kan alt vaere slettet av et tidligere par (kjede)
        try:
            res = sb.rpc('rydd_stevnepar', {'p_behold': behold, 'p_fjern': fjern,
                                            'p_flytt': flytt, 'p_dry': False}).execute().data
        except Exception as e:  # noqa: BLE001
            log.error('  FEIL %s / %s: %s', p['m1_navn'], p['m2_navn'], e)
            utfort['feil'] += 1
            sb.table('opprydding_stevnepar').update({'behold': behold, 'fjern': fjern, 'vedtak': vedtak,
                                                     'resultat': {'feil': str(e)[:500]}}).eq('m1', p['m1']).eq('m2', p['m2']).execute()
            continue
        for k, v in res.items():
            if isinstance(v, int):
                sum_res[k] += v
        utfort['ok'] += 1
        sb.table('opprydding_stevnepar').update({
            'behold': behold, 'fjern': fjern, 'vedtak': vedtak,
            'utfort': datetime.now(timezone.utc).isoformat(), 'resultat': res,
        }).eq('m1', p['m1']).eq('m2', p['m2']).execute()
        if i % 100 == 0 or res.get('ikke_flyttet') or res.get('vind_feil'):
            log.info('  %4d/%d %s | %s -> %s', i, len(plan), p['m1_dato'], p['m1_navn'], json.dumps(res))

    log.info('FERDIG: %d par utfoert, %d feil', utfort['ok'], utfort['feil'])
    log.info('  %s', json.dumps(dict(sum_res), ensure_ascii=False))
    log.info('Oppdaterer forsidetallene …')
    try:
        sb.rpc('refresh_plattform_statistikk').execute()
    except Exception as e:  # noqa: BLE001
        log.warning('  refresh_plattform_statistikk: %s', e)


if __name__ == '__main__':
    main()
