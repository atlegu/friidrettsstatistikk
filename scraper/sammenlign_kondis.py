#!/usr/bin/env python3
"""Mål gateløpsstatistikken vår mot Kondis' årslister.

    python sammenlign_kondis.py            # 2026, alle distanser
    python sammenlign_kondis.py --aar 2026 --distanse 10000

Kondis fører «De beste»-lister for 3 km, 5 km, 10 km, halvmaraton og maraton,
med tidskrav (f.eks. 35:00 for menn på 10 km). For hver liste sjekker vi
hvor mange av løperne der som også står i vår årsbeste (lop_arsbeste, norske
løpere, nivå A og B), og hvilke løp vi mangler. Målet er at vår statistikk
til enhver tid skal være minst like komplett.

Listene hos Kondis brukes bare til denne kontrollen. Ingenting lagres eller
publiseres. Endrer ingen data.
"""

import argparse
import html
import logging
import os
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).resolve().parent
load_dotenv(HER / '.env')
(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(HER / 'logs' / f'sammenlign_kondis_{datetime.now():%Y%m%d_%H%M%S}.log'))
logging.getLogger('httpx').setLevel(logging.WARNING)

DISTANSER = {'3 km': 3000, '5 km': 5000, '10 km': 10000, 'Halvmaraton': 21097, 'Maraton': 42195}
HODE = {'User-Agent': 'Mozilla/5.0 (friidrettsresultater.no, kvalitetskontroll)'}


def fold(s: str) -> str:
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c)).replace('ø', 'o').replace('æ', 'ae').replace('ß', 'ss')
    return ' '.join(re.sub(r'[^a-z ]', ' ', s).split())


def tid_ms(t: str) -> int | None:
    """Kondis skriver «27.22», «1.02.33» og «2.21.06»."""
    deler = t.strip().replace(',', '.').split('.')
    try:
        tall = [int(d) for d in deler]
    except ValueError:
        return None
    sek = 0
    for d in tall:
        sek = sek * 60 + d
    return sek * 1000


# Oversiktssiden hos Kondis laster lenkene med JavaScript, så adressene til
# årets lister står her. Nye år: åpne kondis.no/de-beste og legg dem inn.
LISTER = {
    2026: {
        (3000, 'M'): '/statistikk/de-beste-2026-3-km-menn/1547198',
        (3000, 'F'): '/statistikk/de-beste-2026-3-km-kvinner/1547204',
        (5000, 'M'): '/statistikk/de-beste-2026-5-km-menn/1547210',
        (5000, 'F'): '/statistikk/de-beste-2026-5-km-kvinner/1547216',
        (10000, 'M'): '/statistikk/de-beste-2026-10-km-menn/1547222',
        (10000, 'F'): '/statistikk/de-beste-2026-10-km-kvinner/1547232',
        (21097, 'M'): '/statistikk/de-beste-2026-halvmaraton-menn/1547238',
        (21097, 'F'): '/statistikk/de-beste-2026-halvmaraton-kvinner/1547244',
        (42195, 'M'): '/statistikk/de-beste-2026-maraton-menn/1547444',
        (42195, 'F'): '/statistikk/de-beste-2026-maraton-kvinner/1547450',
    },
}


def kondis_lister(aar: int) -> dict[tuple[int, str], str]:
    return LISTER.get(aar, {})


def les_liste(url: str) -> list[dict]:
    s = requests.get(url if url.startswith('http') else f'https://www.kondis.no{url}', headers=HODE, timeout=60).text
    rader = []
    for tr in re.findall(r'<tr>(.*?)</tr>', s, re.S):
        tds = [html.unescape(re.sub(r'<[^>]+>', '', t)).strip() for t in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(tds) < 5 or not tds[0].isdigit():
            continue
        m = re.match(r'(.+?)\s+-(\d{2})(\(\*\))?$', tds[1])
        if not m:
            continue
        rader.append({'navn': m.group(1), 'aa': int(m.group(2)), 'utenlandsk': bool(m.group(3)),
                      'tid': tid_ms(tds[2]), 'sted': tds[3], 'dato': tds[4],
                      'utland': bool(re.search(r'\([A-Z]{3}\)|, [A-Z]{3}\b', tds[3])),
                      'bane': bool(re.search(r'\((b|i)\)', tds[3]))})
    return rader


def nokkel(navn: str, aa: int) -> tuple[str, int]:
    deler = fold(navn).split()
    return (f'{deler[0]} {deler[-1]}' if len(deler) > 1 else fold(navn), aa % 100)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--aar', type=int, default=datetime.now().year)
    ap.add_argument('--distanse', type=int)
    args = ap.parse_args()
    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

    lister = kondis_lister(args.aar)
    if not lister:
        raise SystemExit('Fant ingen Kondis-lister for året')
    totalt = Counter()
    for (dist, kj), url in sorted(lister.items()):
        if args.distanse and dist != args.distanse:
            continue
        kondis = les_liste(url)
        if not kondis:
            logger.warning(f'{dist} {kj}: tom liste hos Kondis')
            continue
        grense = max(r['tid'] for r in kondis if r['tid'])
        vaar = sb.rpc('lop_arsbeste', {'p_aar': args.aar, 'p_distanse': dist, 'p_kjonn': kj,
                                       'p_nivaa': ['A', 'B'], 'p_antall': 5000, 'p_bare_norske': True}).execute().data
        vaar_k = {nokkel(r['navn'], r['fodt'] or 0): r for r in vaar if r['fodt']}
        bane = [r for r in kondis if r['bane'] and not r['utland']]
        innenlands = [r for r in kondis if not r['utland'] and not r['bane']]
        har = [r for r in innenlands if nokkel(r['navn'], r['aa']) in vaar_k]
        mangler = [r for r in innenlands if nokkel(r['navn'], r['aa']) not in vaar_k]
        kondis_k = {nokkel(r['navn'], r['aa']) for r in kondis}
        ekstra = [r for r in vaar if r['tid_ms'] and r['tid_ms'] <= grense + 999
                  and r['fodt'] and nokkel(r['navn'], r['fodt']) not in kondis_k]
        dekning = 100 * len(har) / len(innenlands) if innenlands else 0
        utland = sum(1 for r in kondis if r['utland'])
        totalt.update(kondis=len(innenlands), har=len(har), ekstra=len(ekstra), utland=utland, bane=len(bane))
        logger.info(f'\n{dist / 1000:g} km {"menn" if kj == "M" else "kvinner"}: Kondis {len(kondis)} '
                    f'({len(innenlands)} fra norske gateløp, {len(bane)} fra bane/inne, {utland} fra utlandet). '
                    f'Vi har {len(har)} av {len(innenlands)} fra norske gateløp ({dekning:.0f} %), '
                    f'og {len(ekstra)} innenfor tidskravet som Kondis ikke har.')
        for sted, n in Counter(r['sted'] for r in mangler).most_common(8):
            logger.info(f'   mangler {n:3d} fra {sted}')
    if totalt['kondis']:
        logger.info(f'\nSamlet: {totalt["har"]} av {totalt["kondis"]} løpere fra norske gateløp '
                    f'({100 * totalt["har"] / totalt["kondis"]:.0f} %). {totalt["ekstra"]} innenfor tidskravene '
                    f'som Kondis ikke har. I tillegg {totalt["bane"]} fra bane/inne (ligger i banestatistikken) '
                    f'og {totalt["utland"]} fra utlandet (innsamlingskanal 2).')


if __name__ == '__main__':
    sys.exit(main())
