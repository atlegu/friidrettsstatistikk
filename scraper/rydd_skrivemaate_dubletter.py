"""Slett rader som er samme resultat skrevet på en annen måte («61.4» / «1:01.40»).

BAKGRUNN
--------
To importer i januar 2026 la inn samme løp med ulik skrivemåte, ofte med ulikt
håndtidsflagg. Samme utøver, øvelse, dato og verdi (performance_value), men
ulik tekst. Den ene raden er en kopi.

REGEL
-----
  Grupper fra skrivemaate_dubletter() i basen. Én rad beholdes:
    1. flest desimaler (hundredeler foran tideler foran hele sekunder)
    2. riktig format: «M:SS.xx» for tider over ett minutt, sekunder under
    3. mest informasjon (plassering, runde, vind)
    4. eldst
  Gruppen røres ikke hvis radene kan være to løp: ulike runder, ulik
  plassering uten runde, eller ulik vind.
  Slettede rader lagres i opprydding_avkortede (presis_id = raden som beholdes).

KJØRING
-------
    python rydd_skrivemaate_dubletter.py            # tørrkjøring, rapport og stikkprøver
    python rydd_skrivemaate_dubletter.py --apply
"""

import argparse
import csv
import logging
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

import gjenopprett_hundredeler as kilde

HER = Path(__file__).parent
load_dotenv(HER / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(HER / 'logs' / f'rydd_skrivemaate_dubletter_{TS}.log', encoding='utf-8')],
                    force=True)
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)


def desimaler(p):
    return len(p.rsplit('.', 1)[1]) if '.' in p else 0


def rangering(r):
    # «585.00» (sekunder over 100) er feil format, uansett desimaler
    if re.fullmatch(r'\d{3,}\.\d+', r['performance']):
        return (9, True, 0, r['lagt'])
    riktig_format = (':' in r['performance']) == (r['pv'] >= 6000)
    info = sum(r[k] is not None for k in ('place', 'round', 'wind'))
    return (-desimaler(r['performance']), not riktig_format, -info, r['lagt'])


def to_lop(rader):
    """Kan radene være ulike løp samme dag?"""
    runder = {r['round'] for r in rader if r['round']}
    if len(runder) > 1:
        return 'ulike runder'
    plasser = {r['place'] for r in rader if r['place'] is not None}
    if len(plasser) > 1 and not runder:
        return 'ulik plassering'
    vind = {round(float(r['wind']), 1) for r in rader if r['wind'] is not None}
    if len(vind) > 1:
        return 'ulik vind'
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--seed', type=int, default=17)
    args = ap.parse_args()

    rader = sb.rpc('skrivemaate_dubletter').execute().data
    grupper = defaultdict(list)
    for r in rader:
        grupper[(r['athlete_id'], r['event_id'], r['date'], r['pv'])].append(r)
    log.info(f"{len(grupper)} grupper, {len(rader)} rader")

    navn = {}
    ids = list({k[0] for k in grupper})
    for i in range(0, len(ids), 200):
        for a in sb.table('athletes').select('id,full_name,birth_year').in_('id', ids[i:i + 200]).execute().data:
            navn[a['id']] = f"{a['full_name']} ({a['birth_year']})"

    ev_navn = {e['id']: e['name'] for e in sb.table('events').select('id,name').execute().data}
    ext = {}
    for i in range(0, len(ids), 200):
        for a in sb.table('athletes').select('id,external_id').in_('id', ids[i:i + 200]).execute().data:
            ext[a['id']] = a['external_id']

    def kildens_desimaler(rr):
        """Antall desimaler kilden oppgir for løpet («2,02,1» = 1, «2,02,10» = 2), eller None."""
        e = ext.get(rr[0]['athlete_id'])
        if not e:
            return None
        try:
            linjer = kilde.kilderader(kilde.hent_side(e))
        except Exception:
            return None
        dd = datetime.fromisoformat(rr[0]['date']).strftime('%d.%m.%y')
        sek = rr[0]['pv'] / 100
        funn = set()
        for ov, d, t in linjer:
            if d != dd or ov != ev_navn[rr[0]['event_id']]:
                continue
            deler = t.replace('+', '').split(',')
            try:
                tall = [int(x) for x in deler]
            except ValueError:
                continue
            if len(deler) == 3:
                verdi = tall[0] * 60 + tall[1] + tall[2] / 10 ** len(deler[2])
            elif len(deler) == 2:
                verdi = tall[0] + tall[1] / 10 ** len(deler[1])
            else:
                continue
            if abs(verdi - sek) < 0.005:
                funn.add(len(deler[-1]))
        return funn.pop() if len(funn) == 1 else None

    slett, holdt = [], []
    for n, (k, rr) in enumerate(grupper.items(), 1):
        grunn = to_lop(rr)
        if grunn:
            holdt.append((grunn, rr))
            continue
        des = {desimaler(r['performance']) for r in rr if not re.fullmatch(r'\d{3,}\.\d+', r['performance'])}
        if des == {1, 2}:
            # Tideler mot hundredeler: kilden avgjør om løpet var håndtidtatt
            fasit = kildens_desimaler(rr)
            if fasit is None:
                holdt.append(('kilden avgjør ikke tideler/hundredeler', rr))
                continue
            rr = sorted(rr, key=lambda r: (desimaler(r['performance']) != fasit, rangering(r)))
        else:
            rr = sorted(rr, key=rangering)
        for r in rr[1:]:
            slett.append((r, rr[0]))
        if n % 200 == 0:
            log.info(f"   {n}/{len(grupper)} grupper")

    def monster(r, beholdt):
        a, b = r['performance'], beholdt['performance']
        if re.fullmatch(r'\d{3,}\.\d+', a):
            return 'sekunder over 100 mot minuttformat'
        if desimaler(a) != desimaler(b):
            return f'slett {desimaler(a)} desimal(er), behold {desimaler(b)} (kilden)'
        return 'samme presisjon, annet format'

    ut = HER / 'opprydding' / f'skrivemaate_dubletter_{TS}.csv'
    with open(ut, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['tiltak', 'utøver', 'øvelse', 'dato', 'slett', 'manuell (slett)', 'behold', 'manuell (behold)', 'samme stevne', 'id', 'behold_id'])
        for r, b in slett:
            w.writerow(['slett', navn.get(r['athlete_id']), r['kode'], r['date'], r['performance'], r['manuell'], b['performance'],
                        b['manuell'], 'ja' if r['meet_id'] == b['meet_id'] else 'nei', r['id'], b['id']])
        for grunn, rr in holdt:
            w.writerow([f'behold alle ({grunn})', navn.get(rr[0]['athlete_id']), rr[0]['kode'], rr[0]['date'],
                        ' / '.join(f"{r['performance']} {r['round'] or ''} pl {r['place']} v {r['wind']}" for r in rr), '', '', '', '', '', ''])

    log.info(f"Slettes: {len(slett)} rader. Holdt utenfor (kan være to løp): {len(holdt)} grupper. Rapport: {ut}")
    for k, v in Counter(monster(r, b) for r, b in slett).most_common():
        log.info(f"   {k}: {v}")
    for k, v in Counter(g for g, _ in holdt).most_common():
        log.info(f"   holdt utenfor, {k}: {v}")
    log.info(f"   annet stevne: {sum(r['meet_id'] != b['meet_id'] for r, b in slett)}, "
             f"håndtidsflagg ulikt: {sum(bool(r['manuell']) != bool(b['manuell']) for r, b in slett)}")

    if not args.apply:
        rnd = random.Random(args.seed)
        for tittel, g in [('Kilden: hundredeler (slett tidelsraden)', [x for x in slett if monster(*x).startswith('slett 1')]),
                          ('Kilden: tideler (slett hundredelsraden)', [x for x in slett if monster(*x).startswith('slett 2')]),
                          ('Samme presisjon, annet format', [x for x in slett if monster(*x) == 'samme presisjon, annet format']),
                          ('Annet stevne', [x for x in slett if x[0]['meet_id'] != x[1]['meet_id']]),
                          ('Andre', [x for x in slett if not monster(*x).startswith(('slett 1', 'slett 2', 'samme'))])]:
            log.info(f"STIKKPRØVE {tittel} ({len(g)}):")
            for r, b in rnd.sample(g, min(6, len(g))):
                log.info(f"   {navn.get(r['athlete_id'])} | {r['kode']} {r['date']} | slett «{r['performance']}»"
                         f"{' (håndtid)' if r['manuell'] else ''} | behold {b['performance']}{' (håndtid)' if b['manuell'] else ''}")
        log.info("STIKKPRØVE holdt utenfor:")
        for grunn, rr in rnd.sample(holdt, min(6, len(holdt))):
            log.info(f"   {grunn}: {navn.get(rr[0]['athlete_id'])} {rr[0]['kode']} {rr[0]['date']}: "
                     + ' / '.join(f"{r['performance']} ({r['round'] or '-'}, pl {r['place']}, v {r['wind']})" for r in rr))
        log.info("DRY-RUN. Kjør med --apply.")
        return

    slettet = 0
    for i in range(0, len(slett), 200):
        bit = slett[i:i + 200]
        fulle = {r['id']: r for r in sb.table('results').select('*').in_('id', [r['id'] for r, _ in bit]).execute().data}
        sb.table('opprydding_avkortede').upsert([{'result_id': r['id'], 'rad': fulle[r['id']], 'presis_id': b['id']}
                                                 for r, b in bit if r['id'] in fulle]).execute()
        sb.table('results').delete().in_('id', [r['id'] for r, _ in bit if r['id'] in fulle]).execute()
        slettet += sum(1 for r, _ in bit if r['id'] in fulle)
    # Raden som beholdes får håndtidsflagg etter presisjonen (bare løp under 800 m)
    kat = {e['id']: (e['code'], e['category']) for e in sb.table('events').select('id,code,category').execute().data}
    flagg = 0
    for b in {b['id']: b for _, b in slett}.values():
        kode, k = kat[b['event_id']]
        m = re.match(r'^(\d+)m', kode)
        if k in ('sprint', 'hurdles') and m and int(m.group(1)) < 800:
            skal = desimaler(b['performance']) == 1
            if bool(b['manuell']) != skal:
                sb.table('results').update({'is_manual_time': skal}).eq('id', b['id']).execute()
                flagg += 1
    log.info(f"Ferdig: {slettet} kopier slettet, håndtidsflagg rettet på {flagg} beholdte rader. "
             f"Reserve i opprydding_avkortede.")


if __name__ == '__main__':
    main()
