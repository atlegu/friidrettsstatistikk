#!/usr/bin/env python3
"""Hent norske gateløp fra Ultimate Sport Service inn i lop_*-tabellene.

    python importer_ultimate.py --aar 2026 --dry-run
    python importer_ultimate.py --aar 2026 [--maks 3] [--event 7257]

Ultimate tar tiden i mange av de største norske løpene (Oslo Maraton,
Drammen10K, Sentrumsløpet, Bergen City Marathon ...). Løpene har opptil
25 000 deltakere, så vi henter bare det statistikken trenger:

  1. Norske løpere innenfor tidskravene i Kondis' «De beste»-lister
     (f.eks. 35:00/42:00 på 10 km for menn/kvinner). Listene er sortert på
     tid, så hentingen stopper ved kravet.
  2. Bruttotid (fra startskuddet) og bosted for hver av disse, fra
     deltakersiden. Listene viser nettotid.

Ultimate har ikke fødselsår, bare aldersklasse (f.eks. M40-44). Løpere
kobles til utøverregisteret på navn og kjønn når det gir ett treff, og
fødselsåret må passe med klassen når registeret har det.

Kilder: kalenderen ultimate.boostcode.net/calendar/events og resultat-
tjenesten live.ultimate.dk (samme som resultatsidene bruker). En varig
integrasjon bør gå gjennom Ultimates API, mot avtale.
"""

import argparse
import html
import logging
import os
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).resolve().parent
load_dotenv(HER / '.env')
(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(HER / 'logs' / f'importer_ultimate_{datetime.now():%Y%m%d_%H%M%S}.log'))
logging.getLogger('httpx').setLevel(logging.WARNING)

KALENDER = 'https://ultimate.boostcode.net/calendar/events?lang=no&year={aar}'
LIVE = 'https://live.ultimate.dk/desktop/front'
MAANEDER = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august',
            'september', 'oktober', 'november', 'desember']
# Kondis' tidskrav for «De beste», i ms: (menn, kvinner)
KRAV = {3000: (600_000, 720_000), 5000: (1_020_000, 1_200_000), 10000: (2_100_000, 2_520_000),
        21097: (4_620_000, 5_700_000), 42195: (10_800_000, 13_800_000)}
# Raskeste mulige tid (verdensrekord på vei), som lop_minste_ms() i basen
MINSTE = {3000: 440_000, 5000: 765_000, 10000: 1_580_000, 21097: 3_440_000, 42195: 7_200_000}
UTELATES = re.compile(r'rullestol|wheelchair|stafett|relay|team|trippel|barn|kids|gang|walk|sykkel|ski|para', re.I)
ALIAS = {'10 for grete': 10000}
# Kopier av et annet arrangement (diplomutskrift, brikker) eller ikke løp
KOPI = re.compile(r'diplom|chips|qr kod|ballot|startnummer', re.I)

sesjon = requests.Session()
sesjon.headers['User-Agent'] = 'Mozilla/5.0 (friidrettsresultater.no, prototype for NFIF)'


def hent(url: str, **params) -> str:
    """GET med samlet tidsgrense. requests' timeout gjelder bare pauser mellom
    pakker, og en treg strøm fra resultattjenesten hengte importen i timevis."""
    for forsok in range(3):
        try:
            with sesjon.get(url, params=params, timeout=(10, 30), stream=True) as r:
                if r.status_code != 200:
                    logger.warning(f'{url}: HTTP {r.status_code}')
                else:
                    frist, deler = time.time() + 60, []
                    for bit in r.iter_content(65536):
                        deler.append(bit)
                        if time.time() > frist:
                            raise requests.Timeout('over 60 s samlet')
                    time.sleep(1.0)  # skånsomt mot Ultimates tjeneste
                    return b''.join(deler).decode(r.encoding or 'utf-8', errors='replace')
        except requests.RequestException as e:
            logger.warning(f'{url} {params.get("mode", "")} {params.get("pid", "")}: {e}')
        time.sleep(3 * (forsok + 1))
    return ''


def tekst(s: str) -> str:
    return html.unescape(re.sub(r'<[^>]+>', '', s)).replace("\\'", "'").strip()


def ms(t: str) -> int | None:
    t = t.strip().split()[0] if t.strip() else ''
    if not re.fullmatch(r'\d{1,2}(:\d{2}){1,2}(\.\d+)?', t):
        return None
    deler = t.split(':')
    sek = 0.0
    for d in deler:
        sek = sek * 60 + float(d)
    return int(round(sek * 1000))


def distanse(navn: str) -> int | None:
    n = navn.lower().strip()
    if n in ALIAS:
        return ALIAS[n]
    if 'halvmaraton' in n or 'half marathon' in n or 'halv maraton' in n:
        return 21097
    if 'maraton' in n or 'marathon' in n:
        return 42195
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(km|k)\b', n)
    if m:
        v = round(float(m.group(1).replace(',', '.')) * 1000)
        return 21097 if v == 21100 else 42195 if v == 42200 else v
    m = re.search(r'(\d{3,5})\s*m(eter)?\b', n)
    return int(m.group(1)) if m else None


def kalender(aar: int) -> list[dict]:
    s = hent(KALENDER.format(aar=aar))
    ut, mnd = [], None
    for m in re.finditer(r'<h5[^>]*>\s*([a-zæøå]+)\s*</h5>|<tr class="bg-secondary">(.*?)</tr>', s, re.S):
        if m.group(1):
            mnd = MAANEDER.index(m.group(1).lower()) + 1 if m.group(1).lower() in MAANEDER else mnd
            continue
        rad = m.group(2)
        dag = re.search(r'<h4[^>]*>\s*(\d+)\s*</h4>', rad)
        lenke = re.search(r'resultsmenu\.php\?id=(\d+)[^>]*>([^<]+)</a>', rad)
        tds = [tekst(t) for t in re.findall(r'<td[^>]*>(.*?)</td>', rad, re.S)]
        if not (dag and lenke and mnd):
            continue
        navn = re.sub(r'^\{\s*"#cdata-section":\s*"(.*)"\s*\}$', r'\1', tekst(lenke.group(2)), flags=re.S).strip()
        ut.append({'id': int(lenke.group(1)), 'navn': navn,
                   'dato': date(aar, mnd, int(dag.group(1))), 'land': tds[2] if len(tds) > 2 else '',
                   'resultater': 'Resultater' in rad})
    return ut


def valg(side: str, felt: str) -> list[tuple[str, str]]:
    m = re.search(rf'<select[^>]*id="{felt}"[^>]*>(.*?)</select>', side, re.S)
    if not m:
        return []
    return [(v, tekst(t)) for v, t in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', m.group(1), re.S)]


def resultatliste(eid: int, dist_id: str, kategori: str, krav: int) -> list[dict]:
    """Rader sortert på tid, til og med tidskravet.

    Med results_startrecord gir tjenesten hele listen fra starten av, opp til
    neste tusen, ikke bare neste side. Vi stopper derfor når en side ikke gir
    nye løpere, når siste løper med tid er over kravet, eller etter ti sider.
    Brudd og ikke startet står sist og har ingen tid; de stopper ikke hentingen
    alene (det hengte importen 15.10.2026).
    """
    sett: dict[int, dict] = {}
    start = 0
    for _ in range(10):
        params = dict(eventid=eid, mode='results', distance=dist_id, category=kategori, language='no')
        if start:
            params = dict(results_startrecord=start, **params)
        s = hent(f'{LIVE}/data.php', **params)
        nye, siste_tid = 0, None
        for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', s, re.S):
            tds = [tekst(t) for t in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
            pid = re.search(r'doParticipantInfo\((\d+)\)', tr)
            if len(tds) < 7 or not pid or not tds[0].isdigit():
                continue
            t = ms(tds[6])
            if t:
                siste_tid = t
            p = int(pid.group(1))
            if p not in sett:
                nye += 1
                sett[p] = {'plass': int(tds[0]), 'pid': p, 'navn': tds[2], 'nasjon': tds[3] or None,
                           'klubb': tds[4] or None, 'klasse': tds[5] or None, 'netto': t}
        neste = re.search(r'results_startrecord\s*=\s*(\d+)', s)
        if not nye or not neste or (siste_tid and siste_tid > krav) or int(neste.group(1)) <= start:
            break
        start = int(neste.group(1))
    return [r for r in sett.values() if r['netto'] and r['netto'] <= krav]


def deltaker(eid: int, pid: int) -> dict:
    s = tekst(hent(f'{LIVE}/data.php', eventid=eid, mode='participantinfo', pid=pid, language='no'))
    s = re.sub(r'\s+', ' ', s)
    brutto = re.search(r'bruttotid\s*(\d{1,2}:\d{2}(?::\d{2})?)', s)
    by = re.search(r'\bby\s+([A-ZÆØÅa-zæøå .\-]+?)\s+land\b', s)
    return {'brutto': ms(brutto.group(1)) if brutto else None, 'by': by.group(1).strip().title() if by else None}


def velg_tid(brutto: int | None, netto: int | None) -> int | None:
    """Bruttotid fra startskuddet, men bare når den er troverdig.

    Bruttotid kan ikke være kortere enn nettotid. Er den det, er starttiden
    feil hos tidtakeren (Drammen10K 2026: «faktisk starttid» fire minutter før
    «offisiell starttid», så Knut Sverre Jørgenvåg fikk 27:46 i stedet for
    31:57). Da, og når forskjellen er urimelig stor, brukes nettotiden."""
    if brutto and netto and netto - 1_500 <= brutto <= netto + 30 * 60_000:  # 1,5 s for avrunding
        return brutto
    return netto or brutto


def klasse_alder(klasse: str | None) -> tuple[int, int] | None:
    m = re.search(r'(\d{1,2})\s*-\s*(\d{1,2})', klasse or '')
    return (int(m.group(1)), int(m.group(2))) if m else None


def koble(sb, rader: list[dict], aar: int) -> int:
    navn = sorted({r['navn'] for r in rader})
    treff: dict[tuple, list[dict]] = {}
    for i in range(0, len(navn), 150):
        for a in sb.table('athletes').select('id, full_name, gender, birth_year').in_('full_name', navn[i:i + 150]).execute().data:
            treff.setdefault((a['full_name'], a['gender']), []).append(a)
    n = 0
    for r in rader:
        kand = treff.get((r['navn'], r['kjonn']), [])
        band = klasse_alder(r['klasse'])
        if band:
            kand = [a for a in kand if not a['birth_year'] or band[0] - 1 <= aar - a['birth_year'] <= band[1] + 1]
        if len(kand) == 1:
            r['athlete_id'], r['fodt'] = kand[0]['id'], kand[0]['birth_year']
            n += 1
    return n


def rett_tider(sb, dry_run: bool):
    """Hent nettotidene på nytt og rett lagrede tider som er kortere."""
    arrangementer = sb.table('lop_arrangement').select('id, kilde_id, navn').eq('kilde', 'ultimate').execute().data
    n_rettet = 0
    for a in arrangementer:
        for l in sb.table('lop_lop').select('id, kilde_id, distanse_m, navn').eq('arrangement_id', a['id']).execute().data:
            dist_id, kj = str(l['kilde_id'] // 10), 'M' if l['kilde_id'] % 10 == 1 else 'F'
            kat = 'S_M' if kj == 'M' else 'S_W'
            netto = {r['pid']: r['netto'] for r in resultatliste(a['kilde_id'], dist_id, kat, KRAV[l['distanse_m']][0 if kj == 'M' else 1] + 60_000)}
            lagret = sb.table('lop_resultat').select('id, kilde_id, navn, tid_ms').eq('lop_id', l['id']).execute().data
            for r in lagret:
                ny = velg_tid(r['tid_ms'], netto.get(r['kilde_id']))
                if netto.get(r['kilde_id']) and ny != r['tid_ms']:
                    n_rettet += 1
                    logger.info(f'{a["navn"]} {l["navn"]}: {r["navn"]} {r["tid_ms"] / 1000:.0f} s -> {ny / 1000:.0f} s')
                    if not dry_run:
                        sb.table('lop_resultat').update({'tid_ms': ny}).eq('id', r['id']).execute()
    logger.info(f'{n_rettet} tider {"ville blitt " if dry_run else ""}rettet')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--aar', type=int, default=date.today().year)
    ap.add_argument('--maks', type=int, default=0)
    ap.add_argument('--event', type=int, help='bare dette arrangementet')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--alle', action='store_true', help='hent også arrangementer som alt er importert')
    ap.add_argument('--rett-tider', action='store_true',
                    help='rett lagrede tider som er kortere enn nettotiden (henter bare listene)')
    args = ap.parse_args()
    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

    if args.rett_tider:
        return rett_tider(sb, args.dry_run)
    arr = [e for e in kalender(args.aar) if e['land'] == 'NOR' and e['resultater'] and e['dato'] <= date.today()
           and not KOPI.search(e['navn'])]
    if args.event:
        arr = [e for e in arr if e['id'] == args.event]
    if not args.alle and not args.event:
        har = {a['kilde_id'] for a in sb.table('lop_arrangement').select('kilde_id').eq('kilde', 'ultimate').execute().data}
        arr = [e for e in arr if e['id'] not in har]
    if args.maks:
        arr = arr[:args.maks]
    logger.info(f'{len(arr)} norske arrangementer med resultater hos Ultimate i {args.aar} som skal hentes')

    tot_lop = tot_res = tot_koblet = tot_kall = 0
    for e in arr:
        side = hent(f'{LIVE}/index.php', eventid=e['id'], language='no')
        distanser = [(v, t) for v, t in valg(side, 'results_distance') if v]
        kategorier = {v: t for v, t in valg(side, 'results_category') if v.startswith('S_')}
        kjonn_kat = {}
        for v, t in kategorier.items():
            tl = t.lower()
            if tl.startswith(('men', 'menn', 'herr', 'mænd', 'mann')) or v in ('S_M', 'S_H'):
                kjonn_kat['M'] = v
            elif tl.startswith(('women', 'kvinn', 'dam', 'kvinder')) or v in ('S_W', 'S_K', 'S_D'):
                kjonn_kat['F'] = v
        lop_rader = []
        for dist_id, dist_navn in distanser:
            dist = distanse(dist_navn)
            if UTELATES.search(dist_navn) or dist not in KRAV:
                continue
            for kj, kat in kjonn_kat.items():
                krav = KRAV[dist][0 if kj == 'M' else 1]
                liste = [r for r in resultatliste(e['id'], dist_id, kat, krav) if r['nasjon'] == 'NOR']
                res = []
                for r in liste:
                    info = deltaker(e['id'], r['pid'])
                    tot_kall += 1
                    tid = velg_tid(info['brutto'], r['netto'])
                    status = 'KONTROLL' if tid < MINSTE.get(dist, 0) else 'OK'
                    res.append({'kilde_id': r['pid'], 'plass': r['plass'], 'navn': r['navn'], 'kjonn': kj,
                                'fodt': None, 'klubb': r['klubb'], 'klasse': r['klasse'], 'tid_ms': tid,
                                'status': status, 'athlete_id': None, 'nasjon': 'NOR'})
                if res:
                    lop_rader.append(({'kilde_id': int(dist_id) * 10 + (1 if kj == 'M' else 2),
                                       'navn': dist_navn, 'distanse_m': dist, 'loypegrad': None, 'ranking': False,
                                       'kvalitetsnivaa': 'B', 'dato': e['dato'].isoformat(),
                                       'merknad': 'Bare norske løpere innenfor tidskravene er hentet. Tid fra startskuddet.'},
                                      res))
        if not lop_rader:
            logger.info(f'{e["dato"]} {e["navn"]}: ingen standarddistanser med norske løpere innenfor kravene')
            continue
        alle = [r for _, res in lop_rader for r in res]
        koblet = koble(sb, alle, args.aar)
        tot_lop += len(lop_rader)
        tot_res += len(alle)
        tot_koblet += koblet
        logger.info(f'{e["dato"]} {e["navn"]}: '
                    + ', '.join(f'{l["navn"]} {"M" if l["kilde_id"] % 10 == 1 else "K"} {len(r)}' for l, r in lop_rader)
                    + f' — {len(alle)} løpere, {koblet} koblet')
        if args.dry_run:
            continue
        a = sb.table('lop_arrangement').upsert({
            'kilde': 'ultimate', 'kilde_id': e['id'], 'navn': e['navn'], 'dato': e['dato'].isoformat(),
            'sted': None, 'arrangor': None, 'gren': 'Gateløp', 'nivaa': None, 'forbund': None,
            'hentet': datetime.now().isoformat()}, on_conflict='kilde,kilde_id').execute().data[0]
        for lop, res in lop_rader:
            lop['arrangement_id'] = a['id']
            l = sb.table('lop_lop').upsert(lop, on_conflict='arrangement_id,kilde_id,distanse_m').execute().data[0]
            for r in res:
                r['lop_id'] = l['id']
            for i in range(0, len(res), 500):
                sb.table('lop_resultat').upsert(res[i:i + 500], on_conflict='lop_id,kilde_id').execute()

    if not args.dry_run:
        fylt = sb.rpc('lop_fyll_fra_andre_kilder').execute().data
        logger.info(f'Fødselsår og utøverkobling fra andre gateløpsresultater: {fylt}')
    logger.info(f'Ferdig{" (dry-run)" if args.dry_run else ""}: {tot_lop} løp, {tot_res} norske løpere innenfor '
                f'kravene, {tot_koblet} koblet til utøverregisteret, {tot_kall} deltakeroppslag')


if __name__ == '__main__':
    sys.exit(main())
