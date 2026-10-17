"""Slett avkortede tider der den presise tiden finnes ved siden av.

BAKGRUNN
--------
Importen i januar 2026 lagret mange tider avkortet: «13:42» for 13:42.78,
«1.15» for 1:15.44 på 400 m (lest som 1,15 sekunder), «1:20:00» for
1:20:52. Senere importer la inn den presise tiden ved siden av uten å kjenne
igjen den gamle raden. Den avkortede raden gir feil i alle lister.

REGEL
-----
  Kandidater fra avkortede_dubletter() i basen: samme utøver, samme øvelse
  (kappgang_3000_m = 3000mg), innen ti dager, og den presise tiden begynner
  med den avkortede (eller «1.15» = 1:15.xx, eller «1:20:00» = 1:20:xx).
  Hver avkortet rad får ett eget presist motstykke (nærmeste dato, så samme
  stevne). To avkortede rader kan ikke bruke samme presise rad. Avkortede
  rader uten eget motstykke røres ikke. Slettede rader lagres i
  opprydding_avkortede.

KJØRING
-------
    python rydd_avkortede_tider.py            # tørrkjøring, rapport og stikkprøver
    python rydd_avkortede_tider.py --apply
"""

import argparse
import csv
import logging
import os
import random
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).parent
load_dotenv(HER / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(HER / 'logs' / f'rydd_avkortede_tider_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)


def type_av(p):
    if p['kort'].endswith(':00') and not p['presis'].startswith(p['kort'] + '.'):
        return 'avrundet til :00'
    if p['fam'] == '400m' or ('.' in p['kort'] and ':' not in p['kort']):
        return '«1.15»-format'
    if 'mg' in p['fam'] or 'kappgang' in p['fam']:
        return 'kappgang'
    return 'manglende hundredeler'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--seed', type=int, default=17)
    ap.add_argument('--maks-dager', type=int, default=3,
                    help='lengste avstand i dager mellom avkortet og presis rad som slettes (resten til manuell kontroll)')
    args = ap.parse_args()

    log.info("Henter kandidatpar fra basen ...")
    par = sb.rpc('avkortede_dubletter').execute().data
    log.info(f"{len(par)} kandidatpar")

    # Ett presist motstykke per avkortet rad: nærmeste dato, så samme stevne
    per_kort = defaultdict(list)
    for p in par:
        per_kort[p['kort_id']].append(p)
    brukt, valgt, uten = set(), [], []
    rekkefolge = sorted(per_kort, key=lambda k: len(per_kort[k]))   # de med færrest valg først
    for k in rekkefolge:
        kand = sorted(per_kort[k], key=lambda p: (abs((date.fromisoformat(p['presis_dato']) - date.fromisoformat(p['kort_dato'])).days),
                                                  p['presis_stevne'] != p['kort_stevne']))
        fri = [p for p in kand if p['presis_id'] not in brukt and p['presis_id'] not in per_kort]
        if fri:
            brukt.add(fri[0]['presis_id'])
            valgt.append(fri[0])
        else:
            uten.append(kand[0])
    for p in valgt:
        d = abs((date.fromisoformat(p['presis_dato']) - date.fromisoformat(p['kort_dato'])).days)
        p['avstand'] = 'samme dag' if d == 0 else f'{d} dager'
        p['samme_stevne'] = p['presis_stevne'] == p['kort_stevne']
        p['type'] = type_av(p)
    # Par med lang avstand kan være to ulike løp: til manuell kontroll
    manuell = [p for p in valgt if p['avstand'] != 'samme dag' and int(p['avstand'].split()[0]) > args.maks_dager]
    valgt = [p for p in valgt if p not in manuell]

    navn = {}
    ids = list({p['athlete_id'] for p in valgt + uten + manuell})
    for i in range(0, len(ids), 200):
        for a in sb.table('athletes').select('id,full_name,birth_year').in_('id', ids[i:i + 200]).execute().data:
            navn[a['id']] = f"{a['full_name']} ({a['birth_year']})"

    ut = HER / 'opprydding' / f'avkortede_tider_{TS}.csv'
    with open(ut, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['tiltak', 'type', 'utøver', 'øvelse', 'avkortet', 'presis', 'dato avkortet', 'dato presis',
                    'avstand', 'samme stevne', 'kort_id', 'presis_id'])
        for p in valgt:
            w.writerow(['slett', p['type'], navn.get(p['athlete_id']), p['fam'], p['kort'], p['presis'], p['kort_dato'],
                        p['presis_dato'], p['avstand'], 'ja' if p['samme_stevne'] else 'nei', p['kort_id'], p['presis_id']])
        for p in manuell:
            w.writerow([f'manuell kontroll (over {args.maks_dager} dager)', p['type'], navn.get(p['athlete_id']), p['fam'], p['kort'],
                        p['presis'], p['kort_dato'], p['presis_dato'], p['avstand'], 'ja' if p['samme_stevne'] else 'nei',
                        p['kort_id'], p['presis_id']])
        for p in uten:
            w.writerow(['behold (presis rad brukt av annen avkortet rad)', type_av(p), navn.get(p['athlete_id']), p['fam'],
                        p['kort'], p['presis'], p['kort_dato'], p['presis_dato'], '', '', p['kort_id'], p['presis_id']])

    log.info(f"Avkortede rader: {len(per_kort)}. Slettes: {len(valgt)}. Manuell kontroll: {len(manuell)}. "
             f"Beholdes (uten eget motstykke): {len(uten)}")
    log.info(f"Rapport: {ut}")
    for k, v in Counter(p['type'] for p in valgt).most_common():
        log.info(f"   {k}: {v}")
    log.info(f"   samme dag: {sum(p['avstand'] == 'samme dag' for p in valgt)}, "
             f"annen dato: {sum(p['avstand'] != 'samme dag' for p in valgt)}, "
             f"annet stevne: {sum(not p['samme_stevne'] for p in valgt)}")

    if not args.apply:
        rnd = random.Random(args.seed)
        grupper = [('Samme dag, samme stevne', [p for p in valgt if p['avstand'] == 'samme dag' and p['samme_stevne']]),
                   ('Annen dato (mesterskap e.l.)', [p for p in valgt if p['avstand'] != 'samme dag']),
                   ('400 m «1.15»-format', [p for p in valgt if p['type'] == '«1.15»-format']),
                   ('Kappgang', [p for p in valgt if p['type'] == 'kappgang']),
                   ('Avrundet til :00', [p for p in valgt if p['type'] == 'avrundet til :00'])]
        for tittel, g in grupper:
            log.info(f"STIKKPRØVE {tittel} ({len(g)}):")
            for p in rnd.sample(g, min(6, len(g))):
                log.info(f"   {navn.get(p['athlete_id'])} | {p['fam']} | slett «{p['kort']}» {p['kort_dato']} | "
                         f"behold {p['presis']} {p['presis_dato']} | {'samme stevne' if p['samme_stevne'] else 'annet stevne'}")
        log.info("DRY-RUN. Kjør med --apply.")
        return

    slettet = 0
    for i in range(0, len(valgt), 200):
        bit = valgt[i:i + 200]
        rader = {r['id']: r for r in sb.table('results').select('*').in_('id', [p['kort_id'] for p in bit]).execute().data}
        sb.table('opprydding_avkortede').upsert([{'result_id': p['kort_id'], 'rad': rader[p['kort_id']], 'presis_id': p['presis_id']}
                                                 for p in bit if p['kort_id'] in rader]).execute()
        sb.table('results').delete().in_('id', [p['kort_id'] for p in bit if p['kort_id'] in rader]).execute()
        slettet += len([p for p in bit if p['kort_id'] in rader])
    log.info(f"Ferdig: {slettet} avkortede tider slettet. Reserve i opprydding_avkortede.")


if __name__ == '__main__':
    main()
