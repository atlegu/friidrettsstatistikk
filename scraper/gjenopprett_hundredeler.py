"""Hent tilbake hundredelene for tider som står som «1.02» (400 m og 400 m hekk).

BAKGRUNN
--------
Kilden (minfriidrettsstatistikk.info) skriver tider over ett minutt som
«1,01,40». Importen i januar 2026 leste dette som «1.01» og mistet siste
ledd. Verdien i basen ble 1:01.00 og visningen «1.01» (ser ut som 1,01 s).
De fleste fikk senere en presis tvilling og er ryddet (rydd_avkortede_tider.py).
De som er igjen, har ingen tvilling: hundredelene må hentes fra kilden.

HVA SKRIPTET GJØR
-----------------
  For hver utøver med slike rader: hent utøversiden fra kilden (POST
  UtoverStatistikk.php, athlete=<external_id>, type=RES; 1,5 s pause; sidene
  mellomlagres i logs/kilde_utover/), finn samme øvelse og dato med tid
  «M,SS,…» som stemmer med minuttene og sekundene i basen.
    - Kilden har hundredeler/tideler: tiden rettes til «1:01.40» / «1:01.4»
      (tideler = håndtid, is_manual_time settes).
    - Kilden har bare hele sekunder: visningen rettes til «1:01» (samme verdi).
    - Finnes den presise tiden alt hos utøveren innen ti dager: raden er en
      dublett og slettes.
    - Ikke funnet i kilden eller tvetydig: bare i rapporten.
  Endrede og slettede rader lagres i opprydding_avkortede.

KJØRING
-------
    python gjenopprett_hundredeler.py            # tørrkjøring, rapport
    python gjenopprett_hundredeler.py --apply
"""

import argparse
import csv
import logging
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).parent
load_dotenv(HER / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(HER / 'logs' / f'gjenopprett_hundredeler_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)

KILDE = 'https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php'
LAGER = HER / 'logs' / 'kilde_utover'
OVELSE = {'400m': '400 meter', '400mh_76_2cm': '400 meter hekk (76,2cm)', '400mh_91_4cm': '400 meter hekk (91,4cm)',
          '400mh_84cm': '400 meter hekk (84,0cm)', '400mh_68cm': '400 meter hekk (68,0cm)'}
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) friidrettsresultater.no/1.0'})


def hent_side(ext_id):
    fil = LAGER / f'{ext_id}.htm'
    if fil.exists():
        return fil.read_text(encoding='utf-8')
    time.sleep(1.5)
    r = session.post(KILDE, data={'athlete': ext_id, 'type': 'RES'}, timeout=30)
    r.raise_for_status()
    r.encoding = 'utf-8'
    LAGER.mkdir(parents=True, exist_ok=True)
    fil.write_text(r.text, encoding='utf-8')
    return r.text


def kilderader(html):
    """[(øvelse, dato 'dd.mm.yy', tid)] fra utøversiden."""
    s = BeautifulSoup(html, 'html.parser')
    ut, ov = [], None
    for el in s.find_all(['h3', 'table']):
        if el.name == 'h3':
            t = el.get_text(strip=True)
            if t and not t.startswith('Født') and t not in ('UTENDØRS', 'INNENDØRS', 'Ikke godkjente resultater'):
                ov = t
            continue
        if not ov:
            continue
        for tr in el.find_all('tr'):
            c = [x.get_text(' ', strip=True) for x in tr.find_all('td')]
            dato = next((x for x in c if re.fullmatch(r'\d{2}\.\d{2}\.\d{2}', x)), None)
            if dato and len(c) > 1:
                ut.append((ov, dato, c[1].split('(')[0].strip()))
    return ut


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    events = {e['id']: e['code'] for e in sb.table('events').select('id,code').execute().data}
    rader = [r for r in sb.rpc('rader_med_punktum_minutter').execute().data if events[r['event_id']] in OVELSE]
    utovere = {}
    ids = list({r['athlete_id'] for r in rader})
    for i in range(0, len(ids), 200):
        for a in sb.table('athletes').select('id,full_name,external_id').in_('id', ids[i:i + 200]).execute().data:
            utovere[a['id']] = a
    log.info(f"{len(rader)} rader med «1.02»-format hos {len(ids)} utøvere")

    per_utover = defaultdict(list)
    for r in rader:
        per_utover[r['athlete_id']].append(r)
    tiltak = []
    for n, (aid, mine) in enumerate(per_utover.items(), 1):
        a = utovere[aid]
        try:
            kilde = kilderader(hent_side(a['external_id']))
        except Exception as e:
            for r in mine:
                tiltak.append({**r, 'navn': a['full_name'], 'tiltak': f'kilden utilgjengelig ({e.__class__.__name__})'})
            continue
        if n % 50 == 0:
            log.info(f"   {n}/{len(per_utover)} utøvere")
        # Grupper per øvelse og dag: flere løp samme dag fordeles i stigende rekkefølge
        gruppe = defaultdict(list)
        for r in mine:
            gruppe[(events[r['event_id']], r['date'])].append(r)
        for (kode, dag), rr in gruppe.items():
            dd = date.fromisoformat(dag).strftime('%d.%m.%y')
            treff = sorted([t for (ov, d, t) in kilde if d == dd and ov == OVELSE[kode]
                            and re.fullmatch(r'\d+,\d\d(,\d{1,2})?', t)
                            and any(t.startswith(r['performance'].replace('.', ',') + ',') or t == r['performance'].replace('.', ',')
                                    for r in rr)])
            rr = sorted(rr, key=lambda r: r['id'])
            if len(treff) != len(rr):
                for r in rr:
                    tiltak.append({**r, 'navn': a['full_name'], 'kode': kode,
                                   'tiltak': 'ikke funnet i kilden' if not treff else f'tvetydig ({len(treff)} i kilden, {len(rr)} i basen)',
                                   'kilde': ' / '.join(treff)})
                continue
            for r, t in zip(rr, treff):
                deler = t.split(',')
                ny = f'{deler[0]}:{deler[1]}' + (f'.{deler[2]}' if len(deler) == 3 else '')
                manuell = len(deler) == 3 and len(deler[2]) == 1
                tiltak.append({**r, 'navn': a['full_name'], 'kode': kode, 'kilde': t, 'ny': ny, 'manuell': manuell,
                               'tiltak': 'rett til hundredeler' if len(deler) == 3 and len(deler[2]) == 2
                               else 'rett til tideler (håndtid)' if manuell else 'kilden har hele sekunder: vis som M:SS'})

    # Finnes den presise tiden alt hos utøveren innen ti dager: dublett
    for t in tiltak:
        if t.get('ny') and '.' in t['ny']:
            d = date.fromisoformat(t['date'])
            har = sb.table('results').select('id,date').eq('athlete_id', t['athlete_id']).eq('event_id', t['event_id']) \
                .eq('performance', t['ny']).gte('date', (d - timedelta(days=10)).isoformat()) \
                .lte('date', (d + timedelta(days=10)).isoformat()).neq('id', t['id']).execute().data
            if har:
                t['tiltak'] = 'slett (presis tid finnes alt)'
                t['merknad'] = har[0]['date']

    ut = HER / 'opprydding' / f'hundredeler_{TS}.csv'
    with open(ut, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['tiltak', 'navn', 'kode', 'date', 'performance', 'kilde', 'ny', 'merknad', 'id'],
                           extrasaction='ignore', delimiter=';')
        w.writeheader()
        w.writerows(tiltak)
    for k, v in Counter(t['tiltak'] for t in tiltak).most_common():
        log.info(f"   {k}: {v}")
    log.info(f"Rapport: {ut}")
    if not args.apply:
        for k in ('rett til hundredeler', 'rett til tideler (håndtid)', 'kilden har hele sekunder: vis som M:SS',
                  'slett (presis tid finnes alt)'):
            for t in [x for x in tiltak if x['tiltak'] == k][:4]:
                log.info(f"   EKS {k}: {t['navn']} {t['kode']} {t['date']}: «{t['performance']}» -> kilde «{t.get('kilde')}» -> {t.get('ny')}")
        log.info("DRY-RUN. Kjør med --apply.")
        return

    rettet = slettet = 0
    for t in tiltak:
        if not (t['tiltak'].startswith('rett') or t['tiltak'].startswith('kilden har') or t['tiltak'].startswith('slett')):
            continue
        rad = sb.table('results').select('*').eq('id', t['id']).execute().data
        if not rad:
            continue
        sb.table('opprydding_avkortede').upsert({'result_id': t['id'], 'rad': rad[0], 'presis_id': None}).execute()
        if t['tiltak'].startswith('slett'):
            sb.table('results').delete().eq('id', t['id']).execute()
            slettet += 1
        else:
            endring = {'performance': t['ny']}
            if t.get('manuell'):
                endring['is_manual_time'] = True
            sb.table('results').update(endring).eq('id', t['id']).execute()
            rettet += 1
    log.info(f"Ferdig: {rettet} rettet, {slettet} slettet. Gamle rader i opprydding_avkortede.")


if __name__ == '__main__':
    main()
