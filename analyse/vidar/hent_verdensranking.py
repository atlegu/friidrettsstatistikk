#!/usr/bin/env python3
"""World Athletics' verdensranking for Vidar-utøverne -> verdensranking.csv.

    ../../scraper/venv/bin/python hent_verdensranking.py

Fremgangsmåte, per rankingøvelse og kjønn:
  1. Hent den norske listen (regionType=countries&region=nor). Den gir poeng,
     men norsk plass, ikke verdensplass.
  2. Koble navnene mot Vidar-utøverne (samme navneregler som stipendlisten).
  3. Bla i verdenslisten til poengsummen er lavere enn den svakeste Vidar-
     utøveren i øvelsen, og les verdensplassen der utøverens profil-lenke står.

Alle rankingøvelser en utøver står i, tas med. World Athletics oppdaterer
listene hver tirsdag; datoen står i CSV-en.
"""

import csv
import html
import json
import re
import sys
import time
from pathlib import Path

import requests

MAPPE = Path(__file__).resolve().parent
sys.path.insert(0, str(MAPPE.parent))
from klubbrapport import navn as navnemodul  # noqa: E402

BASE = 'https://worldathletics.org/world-rankings'
HODE = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/128 Safari/537.36'}

# WA-øvelse -> navn i rapporten. 110 m hekk bare menn, 100 m hekk bare kvinner.
OVELSER = [
    ('100m', '100 m'), ('200m', '200 m'), ('400m', '400 m'), ('800m', '800 m'),
    ('1500m', '1500 m'), ('5000m', '5000 m'), ('10000m', '10 000 m'),
    ('3000msc', '3000 m hinder'), ('110mh', '110 m hekk'), ('100mh', '100 m hekk'),
    ('400mh', '400 m hekk'), ('high-jump', 'Høyde'), ('pole-vault', 'Stav'),
    ('long-jump', 'Lengde'), ('triple-jump', 'Tresteg'), ('shot-put', 'Kule'),
    ('discus-throw', 'Diskos'), ('hammer-throw', 'Slegge'), ('javelin-throw', 'Spyd'),
    ('decathlon', '10-kamp'), ('heptathlon', '7-kamp'), ('marathon', 'Maraton'),
    ('road-running', 'Landevei'), ('race-walking', 'Kappgang'), ('cross-country', 'Terreng'),
]
GYLDIG = {('110mh', 'women'), ('100mh', 'men'), ('decathlon', 'women'), ('heptathlon', 'men')}

sesjon = requests.Session()
sesjon.headers.update(HODE)


def hent_side(slug, kjonn, side, norsk):
    url = f'{BASE}/{slug}/{kjonn}?page={side}' + ('&regionType=countries&region=nor' if norsk else '')
    for forsok in range(4):
        try:
            r = sesjon.get(url, timeout=40)
            if r.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(3 * (forsok + 1))
    else:
        raise SystemExit(f'Fikk ikke hentet {url}')
    time.sleep(0.4)
    h = r.text
    dato = (re.findall(r'[Aa]s of (\d+ [A-Za-z]+ 20\d{2})', h) or [''])[0]
    rader = []
    for lenke, kropp in re.findall(r'<tr[^>]*data-athlete-url="([^"]*)"[^>]*>(.*?)</tr>', h, re.S):
        c = {k: ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', v)).split())
             for k, v in re.findall(r'<td data-th="([^"]+)">(.*?)</td>', kropp, re.S)}
        try:
            aar = (c.get('DOB', '').split() or [''])[-1]
            rader.append({'plass': int(c.get('Rank', '0')), 'navn': c.get('Competitor', ''),
                          'poeng': int(c.get('score', '0')), 'lenke': lenke,
                          'fodt': int(aar) if aar.isdigit() else None})
        except ValueError:
            continue
    return rader, dato


def koble(wa, vidar):
    """Samme fornavn, samme etternavn og samme fødselsår. Mellomnavn kan
    mangle på den ene siden. Strengere enn stipendkoblingen med vilje:
    «Marte Mæhlum-Johansen» ble ellers tatt for «Marte Lien Johnsen».
    Returnerer Vidar-navnet eller None."""
    ord_wa = navnemodul.folde(pent(wa['navn'])).split()
    for navn, u in vidar.items():
        ord_v = navnemodul.folde(navn).split()
        if not ord_wa or not ord_v or ord_wa[0] != ord_v[0] or ord_wa[-1] != ord_v[-1]:
            continue
        if wa['fodt'] and u.get('fodt') and wa['fodt'] != u['fodt']:
            continue
        if set(ord_wa) <= set(ord_v) or set(ord_v) <= set(ord_wa):
            return navn
    return None


def pent(navn):
    """«Elea Jørstad BOCK» -> «Elea Jørstad Bock»."""
    return ' '.join(o.title() if o.isupper() else o for o in navn.split())


def main():
    data = json.loads((MAPPE / 'data.json').read_text())
    vidar = {u['navn']: u for u in data['utovere'].values()}
    ut, dato_liste = [], ''
    for slug, visning in OVELSER:
        for kjonn in ('men', 'women'):
            if (slug, kjonn) in GYLDIG:
                continue
            norske, side = [], 1
            while True:
                rader, dato = hent_side(slug, kjonn, side, norsk=True)
                dato_liste = dato or dato_liste
                if not rader:
                    break
                norske += rader
                if len(rader) < 100:
                    break
                side += 1
            funn = {}
            for r in norske:
                treff = koble(r, vidar)
                if treff:
                    funn[r['lenke']] = (treff, r)
            if not funn:
                continue
            laveste = min(r['poeng'] for _, r in funn.values())
            igjen, side = dict(funn), 1
            while igjen:
                rader, dato = hent_side(slug, kjonn, side, norsk=False)
                if not rader:
                    break
                for r in rader:
                    if r['lenke'] in igjen:
                        vnavn, _ = igjen.pop(r['lenke'])
                        ut.append({'Utøver': vnavn, 'Øvelse': visning, 'Plass': r['plass'],
                                   'Poeng': r['poeng'], 'Dato': dato, 'WA-navn': r['navn'],
                                   'Kilde': f'{BASE}/{slug}/{kjonn}'})
                if rader[-1]['poeng'] < laveste:
                    break
                side += 1
            for vnavn, r in igjen.values():                     # ikke funnet i verdenslisten
                ut.append({'Utøver': vnavn, 'Øvelse': visning, 'Plass': '', 'Poeng': r['poeng'],
                           'Dato': dato_liste, 'WA-navn': r['navn'], 'Kilde': f'{BASE}/{slug}/{kjonn}'})
            print(f'{slug}/{kjonn}: {len(funn)} Vidar-utøvere')

    ut.sort(key=lambda r: (r['Utøver'], r['Plass'] or 99999))
    with open(MAPPE / 'verdensranking.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['Utøver', 'Øvelse', 'Plass', 'Poeng', 'Dato', 'WA-navn', 'Kilde'], delimiter=';')
        w.writeheader()
        w.writerows(ut)
    print(f'{len(ut)} rangeringer, {len({r["Utøver"] for r in ut})} utøvere, liste per {dato_liste}')


if __name__ == '__main__':
    main()
