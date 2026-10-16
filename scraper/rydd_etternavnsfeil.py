"""Flytt resultater fra alle tiders-listene som havnet hos feil utøver med samme etternavn.

BAKGRUNN
--------
Alle tiders-listene på friidrett.no skriver fullt navn, klubb og fødselsdato
bare på utøverens beste rad (fet). De øvrige radene har bare etternavnet.
import_historical.py slo disse opp i et register med ett innslag per
etternavn, og den siste fete raden vant. På stavlista er det ti «Olsen», og
alle Tom Erik Olsens innendørsrader (5.51 i 2003) havnet hos Øyvind Olsen,
f. 1954. Tolkeren er rettet 16.10.2026 (velg_ref i import_historical.py).

HVA SKRIPTET GJØR
-----------------
  1. Henter de 42 seniorlistene på nytt og tolker dem med den rettede tolkeren.
  2. For hvert resultat fra den historiske seniorimporten i basen: finn raden i
     lista (øvelse, dato, resultat, etternavn). Står resultatet på en annen
     person enn lista sier (annet fornavn eller fødselsår), er det feil.
  3. Har riktig utøver allerede resultatet: slett raden (dublett).
     Finnes riktig utøver: flytt raden dit.
     Ellers: bare i rapporten.
  Slettede og flyttede rader lagres i opprydding_etternavnsfeil.

KJØRING
-------
    python rydd_etternavnsfeil.py            # tørrkjøring, rapport
    python rydd_etternavnsfeil.py --apply
"""

import argparse
import csv
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import import_historical as ih

HER = Path(__file__).parent
TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
(HER / 'logs').mkdir(exist_ok=True)
log = logging.getLogger('rydd_etternavnsfeil')
log.setLevel(logging.INFO)
log.propagate = False
for h in (logging.StreamHandler(sys.stdout), logging.FileHandler(HER / 'logs' / f'rydd_etternavnsfeil_{TS}.log', encoding='utf-8')):
    h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    log.addHandler(h)
logging.getLogger('import_historical').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
sb = ih.supabase


def navn(s):
    return re.sub(r'[\s\-]+', ' ', (s or '').lower().replace('.', '')).strip()


def verdi(perf):
    v = ih.performance_to_value((perf or '').replace(',', '.'))
    return round(v, 2) if v is not None else None


def samme_person(n1, b1, n2, b2):
    """Samme person når fornavnet er likt eller nesten likt (Amalia/Amalie,
    Brit/Britt, «A.» mot Arne) og fødselsåret er likt eller ett år unna.
    Kilden og basen staver ikke alltid likt."""
    if b1 and b2 and abs(b1 - b2) > 1 and abs(b1 - b2) != 100:   # 1891/1991: tosifret år
        return False
    f1, f2 = n1.split()[0], n2.split()[0]
    if len(f1) == 1 or len(f2) == 1:          # forbokstav
        return f1[0] == f2[0]
    return ih._levenshtein(f1, f2) <= 2


def hent_alle(tabell, felt, filtre=lambda q: q):
    ut, fra = [], 0
    while True:
        r = filtre(sb.table(tabell).select(felt)).order('id').range(fra, fra + 999).execute().data
        ut.extend(r)
        if len(r) < 1000:
            return ut
        fra += 1000


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    # 1. Listene på nytt
    fasit = {}   # (kode, dato, verdi, etternavn) -> {(fullt navn, fødselsår)}
    for nokkel, (kode_m, kode_k) in ih.SENIOR_EVENTS.items():
        for kjonn, kode in (('M', kode_m), ('F', kode_k)):
            if not kode:
                continue
            lager = HER / 'logs' / 'alletiders_cache' / f'{kjonn}{nokkel}.htm'
            if lager.exists():
                html = lager.read_text(encoding='utf-8')
            else:
                html = ih.fetch_page(ih.build_senior_url(kjonn, nokkel))
                if html:
                    lager.parent.mkdir(parents=True, exist_ok=True)
                    lager.write_text(html, encoding='utf-8')
            if not html:
                log.warning(f"Fikk ikke hentet {kjonn} {nokkel}")
                continue
            rader = ih.parse_senior_page(html, kjonn, kode)
            for r in rader:
                k = (kode, kjonn, r['date_str'], verdi(r['performance']), navn(r['last_name']).split()[-1])
                fasit.setdefault(k, set()).add((navn(r['athlete_name']), r['birth_year']))
            log.info(f"{kjonn} {nokkel}: {len(rader)} rader")

    # 2. Basen
    batcher = [b['id'] for b in sb.table('import_batches').select('id,name').like('name', 'historical_senior%').execute().data]
    events = {e['id']: e['code'] for e in sb.table('events').select('id,code').execute().data}
    log.info("Henter resultater og utøvere ...")
    res = []
    for b in batcher:   # én batch om gangen; in_() over alle ga tidsavbrudd
        res += hent_alle('results', 'id,athlete_id,event_id,date,performance,performance_value,meet_id',
                         lambda q, b=b: q.eq('import_batch_id', b))
    utovere = {a['id']: a for a in hent_alle('athletes', 'id,full_name,birth_year,gender')}
    per_navn = {}
    for a in utovere.values():
        per_navn.setdefault((navn(a['full_name']), a['birth_year'], a['gender']), []).append(a['id'])

    tiltak = []
    for r in res:
        a = utovere.get(r['athlete_id'])
        if not a or not a['full_name']:
            continue
        k = (events[r['event_id']], a['gender'], r['date'], verdi(r['performance']), navn(a['full_name']).split()[-1])
        riktige = fasit.get(k)
        if not riktige:
            continue
        mitt = (navn(a['full_name']), a['birth_year'])
        if any(samme_person(n, b, *mitt) for n, b in riktige):
            continue                     # samme person, ev. med annen skrivemåte
        if len(riktige) != 1:
            tiltak.append({**r, 'fra': a['full_name'], 'fra_fodt': a['birth_year'], 'til': ' / '.join(f'{n} ({b})' for n, b in riktige),
                           'tiltak': 'tvetydig i lista'})
            continue
        (n, b), = riktige
        if re.match(r'^\w\.?$', n.split()[0]) or re.match(r'^\w\.$', a['full_name'].split()[0]):
            # Bare forbokstav (Q. Douglas, A. Kvalheim): kan ikke avgjøres sikkert
            tiltak.append({**r, 'fra': a['full_name'], 'fra_fodt': a['birth_year'], 'til': f'{n} ({b})',
                           'tiltak': 'forbokstav – vurderes manuelt'})
            continue
        kandidater = per_navn.get((n, b, a['gender']), [])
        if len(kandidater) != 1:
            tiltak.append({**r, 'fra': a['full_name'], 'fra_fodt': a['birth_year'], 'til': f'{n} ({b})',
                           'tiltak': 'riktig utøver finnes ikke' if not kandidater else 'flere med samme navn og år'})
            continue
        til = kandidater[0]
        har = sb.table('results').select('id').eq('athlete_id', til).eq('event_id', r['event_id']) \
            .eq('date', r['date']).eq('performance_value', r['performance_value']).limit(1).execute().data
        tiltak.append({**r, 'fra': a['full_name'], 'fra_fodt': a['birth_year'], 'til': utovere[til]['full_name'],
                       'til_fodt': utovere[til]['birth_year'], 'til_id': til,
                       'tiltak': 'slett (riktig utøver har resultatet)' if har else 'flytt'})

    ut = HER / 'opprydding' / f'etternavnsfeil_{TS}.csv'
    with open(ut, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['tiltak', 'fra', 'fra_fodt', 'til', 'til_fodt', 'date', 'performance', 'id', 'athlete_id', 'til_id', 'event_id', 'meet_id', 'performance_value'],
                           extrasaction='ignore', delimiter=';')
        w.writeheader(); w.writerows(tiltak)
    telling = {}
    for t in tiltak:
        telling[t['tiltak']] = telling.get(t['tiltak'], 0) + 1
    log.info(f"{len(res)} historiske seniorresultater kontrollert. Rapport: {ut}")
    for s, n in sorted(telling.items(), key=lambda x: -x[1]):
        log.info(f"   {s}: {n}")
    feil_utovere = {t['athlete_id'] for t in tiltak}
    log.info(f"   ({len(feil_utovere)} utøvere hadde andres resultater)")

    if not args.apply:
        log.info("DRY-RUN. Kjør med --apply.")
        return
    slettet = flyttet = 0
    for t in tiltak:
        if t['tiltak'].startswith('slett'):
            rad = sb.table('results').select('*').eq('id', t['id']).execute().data
            if rad:
                sb.table('opprydding_etternavnsfeil').upsert({'result_id': t['id'], 'rad': rad[0],
                    'grunn': f"tilhører {t['til']} ({t['til_fodt']}), som har resultatet fra før"}).execute()
                sb.table('results').delete().eq('id', t['id']).execute(); slettet += 1
        elif t['tiltak'] == 'flytt':
            rad = sb.table('results').select('*').eq('id', t['id']).execute().data
            if rad:
                sb.table('opprydding_etternavnsfeil').upsert({'result_id': t['id'], 'rad': rad[0],
                    'grunn': f"flyttet fra {t['fra']} ({t['fra_fodt']}) til {t['til']} ({t['til_fodt']})"}).execute()
                sb.table('results').update({'athlete_id': t['til_id']}).eq('id', t['id']).execute(); flyttet += 1
    log.info(f"Ferdig: {slettet} slettet, {flyttet} flyttet. Reserve i opprydding_etternavnsfeil.")


if __name__ == '__main__':
    main()
