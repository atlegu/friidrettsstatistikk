#!/usr/bin/env python3
"""Legg verdensrankingen inn i en ferdig kontrakt_2027-oversikt.

    ../../scraper/venv/bin/python legg_inn_ranking.py

Bruker verdensranking.csv (fra hent_verdensranking.py) og oppdaterer
kontrakt_2027.html, .csv og .pdf uten å hente resultater fra basen:

  * en kolonne «Verdensranking» for hver utøver i alle tabellene
  * OL/VM-kriteriet «topp 25 på verdensrankingen»: utøvere som når det og
    ikke alt står på OL/VM, flyttes dit, og oversikten øverst regnes om

Ved en full kjøring av kontrakt_2027.py skjer det samme direkte, så dette
skriptet trengs bare når basen ikke er tilgjengelig.
"""

import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

MAPPE = Path(__file__).resolve().parent
sys.path.insert(0, str(MAPPE.parent))
import kontrakt_2027 as k  # noqa: E402
from klubbrapport.pdf import lag_pdf  # noqa: E402

BELOP = {n: b for n, b, *_ in k.NIVAAER}


def tall(s):
    return int(re.sub(r'\D', '', s) or 0)


def main():
    ranking = k.les_ranking()
    html_sti = MAPPE / 'kontrakt_2027.html'
    soup = BeautifulSoup(html_sti.read_text(encoding='utf-8'), 'html.parser')
    tabeller = soup.select('div.panel table')
    oversikt, detaljer = tabeller[0], tabeller[1:]

    flyttet = []
    for tab in detaljer:
        hode = tab.select_one('thead tr')
        if hode and not any(th.get_text() == 'Verdensranking' for th in hode.find_all('th')):
            th = soup.new_tag('th'); th.string = 'Verdensranking'; hode.append(th)
        for tr in tab.select('tbody tr'):
            navn = tr.find('b').get_text(strip=True)
            liste = ranking.get(navn, [])
            if len(tr.find_all('td', recursive=False)) < len(hode.find_all('th')):
                td = soup.new_tag('td')
                if liste:
                    td.string = k.vis_ranking(liste)
                else:
                    span = soup.new_tag('span', attrs={'class': 'mut'}); span.string = '–'; td.append(span)
                tr.append(td)
            topp25 = [x for x in liste if x[1] <= k.RANKING_GRENSE]
            niv = tr.select_one('span.niv')
            if tab is detaljer[0] and topp25 and niv and niv.get_text() != 'OL/VM':
                flyttet.append((tr, niv.get_text(), topp25[0]))

    # Flytt til OL/VM
    med = detaljer[0].select_one('tbody')
    ol_rader = [tr for tr in med.find_all('tr', recursive=False) if tr.select_one('span.niv').get_text() == 'OL/VM']
    siste_ol = ol_rader[-1] if ol_rader else None
    endret_niva = {}
    for tr, gammelt, (ovelse, plass, dato, _) in flyttet:
        celler = tr.find_all('td', recursive=False)
        andre = [gammelt] + [x.strip() for x in (celler[1].select_one('div.mut').get_text().replace('også', '').split(','))
                             if celler[1].select_one('div.mut')]
        andre = [a for a in andre if a]
        celler[1].clear()
        span = soup.new_tag('span', attrs={'class': 'niv'}); span.string = 'OL/VM'; celler[1].append(span)
        div = soup.new_tag('div', attrs={'class': 'mut'}); div.string = 'også ' + ', '.join(andre); celler[1].append(div)
        celler[2].string = ovelse
        celler[3].clear()
        b = soup.new_tag('b'); b.string = f'nr. {plass} verdensranking'; celler[3].append(b)
        div = soup.new_tag('div', attrs={'class': 'mut'}); div.string = f'krav topp {k.RANKING_GRENSE} verdensranking'; celler[3].append(div)
        celler[4].clear(); celler[4].append('World Athletics World Rankings')
        div = soup.new_tag('div', attrs={'class': 'mut'}); div.string = dato; celler[4].append(div)
        celler[5].string = k.kr(BELOP['OL/VM'])
        stipend = tall(celler[6].contents[0]) if celler[6].contents else 0
        celler[7].clear()
        if stipend:
            diff = BELOP['OL/VM'] - stipend
            sp = soup.new_tag('span', attrs={'class': 'opp' if diff > 0 else 'ned' if diff < 0 else 'lik'})
            sp.string = (f'+{k.kr(diff)}' if diff > 0 else f'−{k.kr(-diff)}' if diff < 0 else '0')
            celler[7].append(sp)
        celler[8].string = '–'
        tr.extract()
        if siste_ol:
            siste_ol.insert_after(tr)
        else:
            med.insert(0, tr)
        siste_ol = tr
        endret_niva[gammelt] = endret_niva.get(gammelt, 0) + 1

    # Regn om oversikten
    if flyttet:
        for tr in oversikt.select('tbody tr'):
            niv = tr.select_one('span.niv')
            celler = tr.find_all('td')
            if niv:
                n = niv.get_text()
                antall = tall(celler[2].get_text()) + (len(flyttet) if n == 'OL/VM' else -endret_niva.get(n, 0))
                celler[2].string = str(antall)
                celler[3].string = k.kr(antall * BELOP[n])
            elif 'Totalt forslag' in tr.get_text():
                sum_ = sum(tall(t.find_all('td')[3].get_text()) for t in oversikt.select('tbody tr') if t.select_one('span.niv'))
                celler[3].clear()
                b = soup.new_tag('b'); b.string = k.kr(sum_); celler[3].append(b)

    # Metodeteksten
    for li in soup.select('ul.regler li'):
        if li.get_text().startswith('Nivåer og beløp') and 'verdensranking' not in li.get_text():
            li.clear()
            li.append(BeautifulSoup(
                "<b>Nivåer og beløp</b> er tatt rett fra regnearket. OL/VM: resultat på OL 24- eller "
                "VM 25-kravet, eller topp 25 på World Athletics' verdensranking i øvelsen (lagt til "
                "23.09.2026). Elite A og B er kravene i kolonnene «Elite A SKV» og «Elite B SKV».",
                'html.parser'))
    regler = soup.select_one('ul.regler')
    if regler and 'Verdensranking</b>' not in str(regler):
        dato = next((x[2] for liste in ranking.values() for x in liste), '')
        regler.append(BeautifulSoup(
            f"<li><b>Verdensranking</b> er World Athletics' plass i hver øvelse utøveren er rangert i, "
            f"per {dato}, fra worldathletics.org/world-rankings. Koblet på fornavn, etternavn og fødselsår. "
            "«–» betyr ikke rangert.</li>", 'html.parser'))

    html_sti.write_text(str(soup), encoding='utf-8')

    # CSV
    csv_sti = MAPPE / 'kontrakt_2027.csv'
    with open(csv_sti, encoding='utf-8-sig') as f:
        rader = list(csv.reader(f, delimiter=';'))
    hode, data = rader[0], rader[1:]
    if 'Verdensranking' not in hode:
        hode.append('Verdensranking')
        for r in data:
            r.append(k.vis_ranking(ranking.get(r[0], [])))
    kol = {h: i for i, h in enumerate(hode)}
    for r in data:
        topp25 = [x for x in ranking.get(r[0], []) if x[1] <= k.RANKING_GRENSE]
        if topp25 and r[kol['Nivå 2027']] and r[kol['Nivå 2027']] != 'OL/VM':
            ovelse, plass, dato, _ = topp25[0]
            andre = [r[kol['Nivå 2027']]] + [a.strip() for a in r[kol['Andre nivåer nådd']].split(',') if a.strip()]
            r[kol['Nivå 2027']], r[kol['Beløp 2027']] = 'OL/VM', str(BELOP['OL/VM'])
            r[kol['Øvelse']], r[kol['Resultat 2026']] = ovelse, f'nr. {plass} verdensranking'
            r[kol['Dato']], r[kol['Stevne']] = dato, 'World Athletics World Rankings'
            r[kol['Krav']], r[kol['Andre nivåer nådd']] = f'topp {k.RANKING_GRENSE} verdensranking', ', '.join(andre)
            r[kol['Nærmeste høyere nivå']], r[kol['Mangler']] = '', ''
    data.sort(key=lambda r: (k.RANG.get(r[kol['Nivå 2027']], 99) if r[kol['Nivå 2027']] else 99))
    with open(csv_sti, 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f, delimiter=';').writerows([hode] + data)

    lag_pdf(html_sti, MAPPE / 'kontrakt_2027.pdf')
    print(f'{len(flyttet)} flyttet til OL/VM: ' + ', '.join(tr.find("b").get_text() for tr, *_ in flyttet))


if __name__ == '__main__':
    main()
