"""NM-medaljer fra kildens resultatside.

BAKGRUNN
--------
Tabellen championship_medals ble fylt fra friidrett.no sine medaljesider
(én gang, februar 2026). De sidene finnes ikke lenger, og NM 2026 manglet.
Kilden (minfriidrettsstatistikk) har hele stevnet med runde i
plasseringskolonnen: «1-h2» forsoeksheat, «1-hsf1» semifinale, «1-fi»
finale, «1-kv1» kvalifisering, og bare «1» der oevelsen har én runde.

REGEL (Atle, 18.09.2026)
------------------------
  Medaljer bare fra finaler. Har oevelsen en finale («-fi»), er det plass
  1-3 der. Har den bare heat (A- og B-heat, typisk 5000 m og 10 000 m),
  er det plass 1-3 i A-heatet - det heatet med best vinnertid. Har den én
  runde, er det plass 1-3 der. Bare klassene «Menn Senior» og «Kvinner
  Senior»; para- og veteranklasser er egne mesterskap.

  Innendoers loepes 400 m som tidsheat uten finale: sprint (til og med
  400 m) uten finale rangeres paa tid over alle heatene. Loep fra 800 m og
  opp uten finale foelger A-heat-regelen. Der samme utoever staar i flere
  heat uten at kilden merker en finale (200 m innendoers 2026), kan vi
  ikke vite hvilket heat som var finalen: hoppes over og logges. Hopp uten
  tilloep tas ikke med, som i medaljetabellen ellers.

  Utoever-id kobles som i link_championship_medals.py: entydig navnetreff,
  helst med foedselsaar fra kilden.

KJOERING
--------
    python nm_medaljer_fra_kilden.py --stevne 10009180 --type NM_outdoor --aar 2026
    python nm_medaljer_fra_kilden.py --stevne 10008534 --type NM_indoor  --aar 2026 --apply
Toerrkjoering er standard. Medaljer som alt ligger inne for aar/type/
oevelse/kjoenn/medalje roeres ikke.
"""

import argparse
import logging
import os
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, str(Path(__file__).parent))
import update_results as u  # noqa: E402  (fetch_page, BASE_URL, parse_result_wind, parse_runde)

load_dotenv(Path(__file__).parent / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOGG = Path(__file__).parent / 'logs'; LOGG.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(LOGG / f'nm_medaljer_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('update_results').setLevel(logging.WARNING)
log = logging.getLogger(__name__)

KLASSER = {'menn senior': 'M', 'kvinner senior': 'F'}
MEDALJE = {1: 'gold', 2: 'silver', 3: 'bronze'}


def medaljenavn(ovelse: str) -> str:
    """Kildens oevelsesnavn til stilen i championship_medals («100m hekk», «Kule»)."""
    o = ovelse.strip()
    m = re.match(r'^(\d+)\s*meter\s*hekk', o, re.I)
    if m: return f'{m.group(1)}m hekk'
    m = re.match(r'^(\d+)\s*meter\s*hinder', o, re.I)
    if m: return f'{m.group(1)}m hinder'
    m = re.match(r'^Kappgang\s*(\d+)\s*meter', o, re.I)
    if m: return f'{int(m.group(1)) // 1000} km kappgang'
    m = re.match(r'^(\d+)\s*meter$', o, re.I)
    if m:
        n = int(m.group(1))
        return f'{n // 1000} {n % 1000:03d}m' if n >= 10000 else f'{n}m'
    for stamme in ('Kule', 'Diskos', 'Slegge', 'Spyd', 'Vektkast'):
        if o.lower().startswith(stamme.lower()):
            return stamme
    return o


def tid_som_tall(res: str):
    """Sekunder, til aa sammenligne heatvinnere. None for felt.
    Kilden skriver 4,02,75 for 4:02,75; etter kommabytte er det 4.02.75."""
    t = res.replace(',', '.')
    deler = t.split(':') if ':' in t else (t.rsplit('.', 1) if t.count('.') == 2 else [t])
    if len(deler) == 2 and '.' in deler[0]:
        deler = deler[0].split('.') + [deler[1]]
        deler = [deler[0], deler[1] + '.' + deler[2]]
    try:
        s = 0.0
        for d in deler:
            s = s * 60 + float(d)
        return s
    except ValueError:
        return None


def normaliser(navn: str) -> str:
    ut = []
    for tegn in unicodedata.normalize('NFD', (navn or '').lower()):
        if tegn in 'æøå' or unicodedata.category(tegn) != 'Mn':
            ut.append(tegn)
    return re.sub(r'[^0-9a-zæøå]+', ' ', ''.join(ut)).strip()


def hent_kilde(ext_id: int):
    html = u.fetch_page(f"{u.BASE_URL}/StevneResultater.php", method='POST', data={'competition': ext_id})
    if not html:
        raise SystemExit('Fikk ikke hentet kildesiden')
    soup = BeautifulSoup(html, 'html.parser')
    rader = defaultdict(list)          # (kjoenn, oevelse) -> [rad]
    klasse = ovelse = None
    for e in soup.find_all(['div', 'table']):
        if e.name == 'div' and e.get('id') == 'header2':
            klasse = e.get_text(strip=True).lower()
        elif e.name == 'div' and e.get('id') == 'eventheader':
            ovelse = e.get_text(strip=True)
        elif e.name == 'table' and klasse in KLASSER and ovelse:
            for tr in e.find_all('tr'):
                td = tr.find_all('td')
                if len(td) < 4:
                    continue
                ptekst = td[0].get_text(strip=True)
                m = re.match(r'^(\d+)', ptekst)
                if not m:
                    continue
                runde, heat = u.parse_runde(ptekst)
                res, vind, _, _ = u.parse_result_wind(td[1].get_text(strip=True))
                if not res or res.upper() in ('DNS', 'DNF', 'DQ', 'NM', '-'):
                    continue
                navn = td[2].get_text(strip=True)
                aar = None
                ym = re.search(r'\((\d{4})\)$', navn)
                if ym:
                    aar = int(ym.group(1)); navn = navn[:ym.start()].strip()
                rader[(KLASSER[klasse], ovelse)].append({
                    'plass': int(m.group(1)), 'runde': runde, 'heat': heat,
                    'resultat': res.replace(',', '.'), 'navn': navn, 'aar': aar,
                    'klubb': td[3].get_text(strip=True),
                })
    return rader


def finaler(rader, ovelse):
    """Radene medaljene regnes av, etter regelen over."""
    runder = {r['runde'] for r in rader}
    if 'final' in runder:
        return [r for r in rader if r['runde'] == 'final'], 'finale'
    if 'heat' in runder and runder <= {'heat', None}:
        heats = defaultdict(list)
        for r in rader:
            if r['runde'] == 'heat':
                heats[r['heat']].append(r)
        sett = defaultdict(set)
        for h, rr in heats.items():
            for r in rr:
                sett[(r['navn'], r['aar'])].add(h)
        if any(len(h) > 1 for h in sett.values()):
            return [], 'flere runder uten merket finale, manuelt'
        m = re.match(r'^(\d+)\s*meter', ovelse)
        if m and int(m.group(1)) <= 400:         # tidsheat: alle rangeres paa tid
            alle = [r for h in heats.values() for r in h if tid_som_tall(r['resultat']) is not None]
            alle.sort(key=lambda r: tid_som_tall(r['resultat']))
            ut = [dict(r, plass=i + 1) for i, r in enumerate(alle[:3])]
            return ut, f'tidsheat ({len(heats)} heat)'
        def vinner(h):
            v = [tid_som_tall(r['resultat']) for r in heats[h] if r['plass'] == 1]
            return min([x for x in v if x is not None], default=float('inf'))
        beste = min(heats, key=vinner)
        return heats[beste], f'A-heat (heat {beste})'
    if runder == {None}:
        return rader, 'én runde'
    return [], f'uavklart: {sorted(str(x) for x in runder)}'


def koble_utover(navn, aar, kjonn, indeks):
    kand = indeks.get(normaliser(navn), [])
    if aar:
        kand = [k for k in kand if k['birth_year'] in (aar, None)] or kand
    kand = [k for k in kand if k['gender'] in (kjonn, None)] or kand
    if len(kand) == 1:
        return kand[0]['id']
    if aar:
        eksakt = [k for k in kand if k['birth_year'] == aar]
        if len(eksakt) == 1:
            return eksakt[0]['id']
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--stevne', type=int, required=True, help='kildens stevne-id')
    ap.add_argument('--type', required=True, choices=['NM_outdoor', 'NM_indoor'])
    ap.add_argument('--aar', type=int, required=True)
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    rader = hent_kilde(a.stevne)
    log.info('%d klasse/oevelse-grupper i senior fra kilden', len(rader))

    # utoeverindeks paa normalisert navn
    indeks = defaultdict(list)
    fra = '00000000-0000-0000-0000-000000000000'
    while True:
        d = sb.table('athletes').select('id,full_name,birth_year,gender').gt('id', fra).order('id').limit(1000).execute().data
        for r in d:
            indeks[normaliser(r['full_name'])].append(r)
        if len(d) < 1000:
            break
        fra = d[-1]['id']

    finnes = {(m['gender'], m['event_name'], m['medal'])
              for m in sb.table('championship_medals').select('gender,event_name,medal')
                          .eq('year', a.aar).eq('championship_type', a.type).execute().data}

    nye, hoppet = [], []
    for (kjonn, ovelse), rr in sorted(rader.items()):
        if 'uten tilløp' in ovelse.lower():
            continue
        fin, hvordan = finaler(rr, ovelse)
        navn_ov = medaljenavn(ovelse)
        if not fin:
            hoppet.append(f'{kjonn} {ovelse}: {hvordan}')
            continue
        paa_pallen = sorted([r for r in fin if r['plass'] <= 3], key=lambda r: r['plass'])
        for r in paa_pallen:
            medal = MEDALJE[r['plass']]
            if (kjonn, navn_ov, medal) in finnes:
                continue
            aid = koble_utover(r['navn'], r['aar'], kjonn, indeks)
            nye.append({'year': a.aar, 'championship_type': a.type, 'event_name': navn_ov, 'gender': kjonn,
                        'medal': medal, 'athlete_name': r['navn'], 'performance': r['resultat'],
                        'club_name': r['klubb'] or None, 'athlete_id': aid,
                        'source_url': f'{u.BASE_URL}/StevneResultater.php?competition={a.stevne}'})
        log.info('  %s %-28s %-16s %s', kjonn, ovelse, hvordan,
                 ' | '.join(f"{r['plass']}. {r['navn']} {r['resultat']}" for r in paa_pallen))
    for h in hoppet:
        log.warning('  HOPPET OVER %s', h)
    ukoblet = [n for n in nye if not n['athlete_id']]
    log.info('%d nye medaljer, %d uten utoever-kobling: %s', len(nye), len(ukoblet),
             ', '.join(n['athlete_name'] for n in ukoblet))

    if not a.apply:
        log.info('Toerrkjoering. --apply for aa legge inn.')
        return
    for i in range(0, len(nye), 100):
        sb.table('championship_medals').insert(nye[i:i + 100]).execute()
    log.info('Lagt inn %d medaljer for %s %d', len(nye), a.type, a.aar)


if __name__ == '__main__':
    main()
