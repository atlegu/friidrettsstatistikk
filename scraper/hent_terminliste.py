#!/usr/bin/env python3
"""Hent terminlisten og koble den mot resultatene vi har.

    python hent_terminliste.py --dry-run
    python hent_terminliste.py

Kilder:
  * Terminlisten på friidrett.no/terminliste. Den bygges fra iSonen og har
    hvert arrangement med id, type, krets, arrangør, sted, dato og øvelser.
  * Stevnelisten i LiveRes (liveres.andro.no/data/frisys.json), for å se om
    et stevne som mangler hos oss, har resultater der.

For hvert arrangement som er avholdt, finner vi stevnet (bane) eller løpet
(gateløp) med resultater: samme dato, pluss likt navn eller samme sted.
Resultatet lagres i tabellen terminliste; purring og avlysning føres i
terminliste_oppfolging fra administrasjonsverktøyet og røres ikke her.
"""

import argparse
import html
import json
import logging
import os
import re
import sys
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).resolve().parent
load_dotenv(HER / '.env')
(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(HER / 'logs' / f'hent_terminliste_{datetime.now():%Y%m%d_%H%M%S}.log'))
logging.getLogger('httpx').setLevel(logging.WARNING)

TERMINLISTE = 'https://www.friidrett.no/terminliste'
LIVERES = 'https://liveres.andro.no/data/frisys.json'
OSLO = ZoneInfo('Europe/Oslo')

GATETYPER = {'Gateløp', 'Terrengløp', 'Ultraløp', 'Fjell-løp', 'Motbakkeløp', 'Trappeløp', 'Hinderløp', 'Stafett'}
FYLL = {'friidrett', 'friidrettsklubb', 'idrettslag', 'il', 'if', 'ik', 'fik', 'og', 'i', 'stevne', 'stevnet',
        'nasjonalt', 'innendørs', 'utendørs'}


def norm(s: str | None) -> str:
    s = (s or '').lower()
    s = re.sub(r'\b(19|20)\d{2}\b', ' ', s)
    s = re.sub(r'[^a-zæøå0-9 ]', ' ', s)
    return ' '.join(o for o in s.split() if o not in FYLL)


def likhet(a: str | None, b: str | None) -> float:
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    ta, tb = set(na.split()), set(nb.split())
    jaccard = len(ta & tb) / len(ta | tb)
    return max(SequenceMatcher(None, na, nb).ratio(), jaccard)


def lokal_dato(iso: str) -> date:
    return datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(OSLO).date()


GATEORD = re.compile(r'gateløp|motbakke|terreng|fjell|trappeløp|ultra|maraton|\bmila\b|milå|roadmile|\d+[.,]?\d* ?km\b', re.I)
# Baneøvelser: tekniske øvelser, eller løp oppgitt i meter («3000 meter»,
# «1 engelsk mil» regnes ikke). Banestevner med bare løp finnes, så det er
# meterangivelsen som avgjør, ikke at det er løp.
BANEOVELSE = re.compile(r'\b(høyde|lengde|tresteg|stav|kule|diskos|slegge|spyd|hekk|ballkast|vektkast)\b'
                        r'|\b\d{2,5} ?(m|meter)\b|\bstafett\b', re.I)
BANENAVN = re.compile(r'\bbane\b|banestevne|stadion|idrettspark|\barena\b|innendørs|hallen?\b', re.I)


def kategori(e: dict) -> str:
    """Bane eller gateløp.

    1. iSonen-typen avgjør når den er entydig (Gateløp, Terrengløp ...).
    2. Ellers øvelsene: meterangivelse eller tekniske øvelser gir bane,
       km, motbakke, terreng og liknende gir gateløp.
    3. Uten øvelser: navnet. «Bane», «stadion» eller «innendørs» gir bane.
    """
    if e.get('CompetitionType') in GATETYPER:
        return 'gate'
    tittel = e.get('Title') or ''
    if e.get('EventSource') == 'EqTiming':  # løpstidtaker; banestevner der har «bane» eller meter i navnet
        return 'bane' if BANENAVN.search(tittel) or re.search(r'\b\d{3,5} ?(m|meter)\b', tittel, re.I) else 'gate'
    ovelser = ' '.join(a.get('ActivityName') or '' for a in e.get('Activities') or [])
    if ovelser.strip():
        if BANEOVELSE.search(ovelser):
            return 'bane'
        if GATEORD.search(ovelser):
            return 'gate'
    if GATEORD.search(tittel) and not BANENAVN.search(tittel):
        return 'gate'
    return 'bane'


def hent_terminliste() -> list[dict]:
    r = requests.get(TERMINLISTE, headers={'User-Agent': 'Mozilla/5.0 (friidrettsresultater.no)'}, timeout=120)
    r.raise_for_status()
    m = re.search(r':events="(\[.*?\])"', r.text, re.S)
    if not m:
        raise SystemExit('Fant ikke arrangementslisten på friidrett.no/terminliste')
    return json.loads(html.unescape(m.group(1)))


def alle(sb, fn):
    rader, fra = [], 0
    while True:
        bit = fn(fra, fra + 999)
        rader += bit
        if len(bit) < 1000:
            return rader
        fra += 1000


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

    arr = hent_terminliste()
    idag = date.today()
    liste = []
    for e in arr:
        start, slutt = lokal_dato(e['ScheduleStartDateTime']), lokal_dato(e['ScheduleEndDateTime'])
        liste.append({
            'isonen_id': e['Id'], 'tittel': (e.get('Title') or '').strip(), 'krets': e.get('ConfederationName'),
            'type': e.get('CompetitionType'), 'kategori': kategori(e), 'arrangor': e.get('Organizer'),
            'sted': ', '.join(x for x in (e.get('LocationName'), e.get('LocationPostalArea')) if x) or None,
            'start_dato': start.isoformat(), 'slutt_dato': slutt.isoformat(), 'url': e.get('EventUrl'),
            'antall_ovelser': len(e.get('Activities') or []), '_postnr_sted': e.get('LocationPostalArea'),
            '_eq': e.get('EventSource') == 'EqTiming',
        })
    logger.info(f'{len(liste)} arrangementer i terminlisten '
                f'({sum(1 for t in liste if t["kategori"] == "bane")} bane, '
                f'{sum(1 for t in liste if t["kategori"] == "gate")} gateløp)')

    fra = min(date.fromisoformat(t['start_dato']) for t in liste) - timedelta(days=2)
    til = min(idag, max(date.fromisoformat(t['slutt_dato']) for t in liste)) + timedelta(days=2)
    stevner = alle(sb, lambda a, b: sb.rpc('terminliste_stevner', {'p_fra': fra.isoformat(), 'p_til': til.isoformat()})
                   .range(a, b).execute().data)
    lop = alle(sb, lambda a, b: sb.table('lop_oversikt').select('id, navn, dato, sted, lopere, kilde_id')
               .gte('dato', fra.isoformat()).lte('dato', til.isoformat()).range(a, b).execute().data)
    try:
        liveres = requests.get(LIVERES, timeout=60).json().get('competitions', [])
    except Exception as feil:  # LiveRes er et tillegg; terminlisten skal oppdateres uansett
        logger.warning(f'LiveRes: {feil}')
        liveres = []
    logger.info(f'{len(stevner)} stevner og {len(lop)} gateløp i perioden {fra}–{til}, {len(liveres)} stevner i LiveRes')

    def kandidater(t, kilde, dato_felt, slutt_felt=None):
        s, e = date.fromisoformat(t['start_dato']) - timedelta(days=1), date.fromisoformat(t['slutt_dato']) + timedelta(days=1)
        for k in kilde:
            d = date.fromisoformat(k[dato_felt][:10])
            if s <= d <= e:
                yield k

    koblet = {'bane': 0, 'gate': 0}
    for t in liste:
        t['meet_id'] = t['lop_arrangement_id'] = t['liveres_id'] = None
        t['antall_resultater'] = 0
        if date.fromisoformat(t['start_dato']) > idag:
            continue
        serie = (date.fromisoformat(t['slutt_dato']) - date.fromisoformat(t['start_dato'])).days > 7
        sted = t.pop('_postnr_sted', None)
        def finn_stevne():
            # Stedsord fra iSonen: poststed, anleggsnavn og arrangørens navn
            stedsord = set(norm(f"{sted or ''} {t['sted'] or ''} {t['arrangor'] or ''}").split())
            aktuelle = [k for k in kandidater(t, stevner, 'start_date') if k['resultater']]
            samme_by = [k for k in aktuelle if k.get('city') and set(norm(k['city']).split()) <= stedsord]
            treff = []
            for k in aktuelle:
                score = max(likhet(t['tittel'], k['name']), likhet(t['arrangor'], k['name']))
                if k in samme_by:
                    score += 0.3
                    if len(samme_by) == 1:  # eneste stevne med resultater i byen den dagen
                        score = max(score, 0.6)
                elif k.get('city') and stedsord:
                    score -= 0.15  # annen by: generiske navn som «Treningsstevne» skal ikke treffe
                if score >= 0.6:
                    treff.append((score, k))
            if treff:
                treff.sort(key=lambda x: (-x[0], x[1]['start_date']))
                valgt = [k for _, k in treff] if serie else [treff[0][1]]
                t['meet_id'] = valgt[-1]['id'] if serie else valgt[0]['id']
                t['antall_resultater'] = sum(k['resultater'] for k in valgt)

        if t['kategori'] == 'bane':
            finn_stevne()
        else:
            eq_id = t.pop('_eq', False) and t['isonen_id'].isdigit() and int(t['isonen_id'])
            direkte = [k for k in lop if eq_id and k.get('kilde_id') == eq_id]
            if direkte:  # samme arrangement i EQ Timing
                t['lop_arrangement_id'] = direkte[0]['id']
                t['antall_resultater'] = direkte[0]['lopere']
                if t['antall_resultater']:
                    koblet[t['kategori']] += 1
                continue
            treff = sorted(((likhet(t['tittel'], k['navn']) + (0.3 if sted and k.get('sted') and norm(sted) in norm(k['sted']) else 0), k)
                            for k in kandidater(t, lop, 'dato')), key=lambda x: -x[0])
            if treff and treff[0][0] >= 0.6:
                t['lop_arrangement_id'] = treff[0][1]['id']
                t['antall_resultater'] = treff[0][1]['lopere']
            else:
                finn_stevne()  # kappgang og enkelte løp ligger i banestatistikken
        if t['antall_resultater']:
            koblet[t['kategori']] += 1
        lr = [(likhet(t['tittel'], c.get('name')), c) for c in liveres
              if c.get('date_start') and abs((date.fromisoformat(c['date_start']) - date.fromisoformat(t['start_dato'])).days) <= 1]
        lr = [x for x in lr if x[0] >= 0.6]
        if lr:
            t['liveres_id'] = max(lr, key=lambda x: x[0])[1]['id']
    for t in liste:
        t.pop('_postnr_sted', None)
        t.pop('_eq', None)
        t['sist_sett'] = t['oppdatert'] = datetime.now().isoformat()

    avholdt = [t for t in liste if date.fromisoformat(t['slutt_dato']) < idag]
    for kat in ('bane', 'gate'):
        n = sum(1 for t in avholdt if t['kategori'] == kat)
        mangler = sum(1 for t in avholdt if t['kategori'] == kat and not t['antall_resultater'])
        logger.info(f'{kat}: {n} avholdt, {koblet[kat]} med resultater hos oss, {mangler} uten')
    if args.dry_run:
        for t in [t for t in avholdt if not t['antall_resultater']][:15]:
            logger.info(f'  mangler: {t["slutt_dato"]} {t["kategori"]} {t["tittel"]} ({t["arrangor"]})'
                        f'{" — finnes i LiveRes" if t["liveres_id"] else ""}')
        logger.info('Dry-run: ingenting lagret')
        return

    for i in range(0, len(liste), 200):
        sb.table('terminliste').upsert(liste[i:i + 200], on_conflict='isonen_id').execute()
    logger.info(f'{len(liste)} arrangementer lagret')


if __name__ == '__main__':
    sys.exit(main())
