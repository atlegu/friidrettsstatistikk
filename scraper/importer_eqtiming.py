#!/usr/bin/env python3
"""Prototype: hent gateløp fra EQ Timing inn i lop_*-tabellene.

    python importer_eqtiming.py --fra 2026-09-01 --til 2026-10-14 --dry-run
    python importer_eqtiming.py --fra 2026-09-01 --til 2026-10-14

Henter arrangementer under Norges Friidrettsforbund med publiserte resultater
fra EQ Timings åpne resultattjeneste (live.eqtiming.com/api), som er den
samme tjenesten resultatsidene deres bruker. Én konkurranse per målpassering
(stasjon med Er_stopp), slik at 5 km og 10 km i samme arrangement blir to løp.

Kvalitetsnivå settes maskinelt (kravspekken §6):
  A  sertifisert målt løype (A- eller B-måling) og offisiell distanse
  B  sertifisert målt løype (C-måling) eller offisiell distanse
  C  øvrige

Er vinnertiden raskere enn verdensrekordfart, er distansen feil: løpet får
nivå C og en merknad.

Løpere kobles til utøverregisteret når fullt navn, kjønn og fødselsår gir
ett entydig treff. Ellers står resultatet uten kobling.

Dette er en prototype. En varig integrasjon bør avtales med EQ Timing, slik
at vi får et dokumentert grensesnitt og varsel om endringer.
"""

import argparse
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).resolve().parent
load_dotenv(HER / '.env')

(HER / 'logs').mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger.addHandler(logging.FileHandler(HER / 'logs' / f'importer_eqtiming_{datetime.now():%Y%m%d_%H%M%S}.log'))

API = 'https://live.eqtiming.com/api'
OFFISIELLE = {3000, 5000, 10000, 15000, 20000, 21097, 25000, 30000, 42195, 50000, 100000}
FORBUND = 'Norges Friidrettsforbund'
# Raskere enn verdensrekordfart på alle distanser fra 800 m (800 m: 126 ms/m)
MINSTE_MS_PER_M = 120
# Bare disse arrangementstypene rangeres på distanse. Terreng-, motbakke-,
# fjell- og ultraløp er registrert aktivitet (nivå C) og får lister per løype.
RANGERES = {'Gateløp', 'Annet', 'Annet/Kombinert'}

sesjon = requests.Session()
sesjon.headers['User-Agent'] = 'friidrettsresultater.no (prototype for NFIF)'


def hent(sti: str, **params):
    for forsok in range(4):
        try:
            r = sesjon.get(f'{API}/{sti}', params=params, timeout=60)
            if r.status_code == 200:
                time.sleep(0.4)
                return r.json()
            logger.warning(f'{sti}: HTTP {r.status_code}')
        except requests.RequestException as e:
            logger.warning(f'{sti}: {e}')
        time.sleep(3 * (forsok + 1))
    return None


def normaliser_distanse(km: float | None) -> int | None:
    if not km:
        return None
    m = km * 1000
    for offisiell in (21097, 42195):
        if abs(m - offisiell) / offisiell < 0.01:
            return offisiell
    return int(round(m / 100.0) * 100)


def pent_navn(u: dict) -> str:
    """Fornavn + etternavn; ord i bare store bokstaver («SANDVIK») gjøres om."""
    navn = f"{u.get('Fornavn') or ''} {u.get('Etternavn') or ''}".strip() or (u.get('NavnFormatert') or '').strip()
    return ' '.join(o.title() if o.isupper() and len(o) > 1 else o for o in navn.split())


def distanse_fra_tekst(tekst: str | None) -> int | None:
    """«3 runder (5 km)» -> 5000, «2 km» -> 2000, «Halvmaraton» -> 21097."""
    if not tekst:
        return None
    t = tekst.lower()
    if 'halvmaraton' in t or 'half marathon' in t:
        return 21097
    if 'maraton' in t or 'marathon' in t:
        return 42195
    funn = re.findall(r'(\d+(?:[.,]\d+)?)\s*(km|k\b|m\b|meter)', t)
    if not funn:
        return None
    tall, enhet = funn[-1]
    v = float(tall.replace(',', '.'))
    return normaliser_distanse(v if enhet in ('km', 'k') else v / 1000)


def kvalitetsnivaa(distanse: int | None, grad: str) -> str:
    offisiell = distanse in OFFISIELLE
    if offisiell and grad in ('A', 'B'):
        return 'A'
    if offisiell or grad == 'C':
        return 'B'
    return 'C'


def grad_fra(navn: str | None) -> str | None:
    """«Certified B-Measured Course» -> «B»."""
    if navn and 'Measured' in navn:
        bokstav = navn.replace('Certified', '').strip()[:1]
        return bokstav if bokstav in 'ABC' else None
    return None


def arrangementer(fra: str, til: str) -> list[dict]:
    d = hent('Events', query='', dateFrom=f'{fra} 00:00', dateTo=f'{til} 23:59', organizationId=0,
             regionIds='', levelIds='', sportIds='', take=1500, dateSort='true', desc='false',
             onlyValidated='false', onlyshowfororganizer='false', organizerIds='', graded='false',
             racequality='false') or []
    return [e for e in d
            if (e.get('Organization') or {}).get('Name') == FORBUND and (e.get('Meta') or {}).get('GotResults')]


def stoppstasjoner(ev: dict) -> list[tuple[int, int, float]]:
    """(etappe_uid, stasjonsoppsett_uid, km) for hver målpassering."""
    ut = []
    for s in (ev.get('Stasjoner') or {}).values():
        for oid, o in (s.get('StasjonsOppsett') or {}).items():
            if o.get('Er_stopp') and o.get('EtappeUID'):
                ut.append((int(o['EtappeUID']), int(oid), o.get('Km') or 0))
    return ut


def resultater(eid: int, etappe: int, stasjon: int) -> list[dict]:
    rader, side = [], 1
    while True:
        d = hent(f'Result/Total/{eid}/{etappe}', justTimeData='false', count=1000, startAt=side,
                 station=stasjon, query='', round=1, passes='false')
        if not d or not d.get('Items'):
            break
        rader += d['Items']
        if side >= (d.get('TotalPages') or 1):
            break
        side += 1
    return rader


def koble_utovere(sb, rader: list[dict]) -> int:
    """Sett athlete_id der navn, kjønn og fødselsår gir ett treff."""
    navn = sorted({r['navn'] for r in rader if r['fodt'] and r['kjonn']})
    treff: dict[tuple, list[str]] = {}
    for i in range(0, len(navn), 150):
        bit = navn[i:i + 150]
        for a in sb.table('athletes').select('id, full_name, gender, birth_year').in_('full_name', bit).execute().data:
            treff.setdefault((a['full_name'], a['gender'], a['birth_year']), []).append(a['id'])
    n = 0
    for r in rader:
        ids = treff.get((r['navn'], r['kjonn'], r['fodt']), [])
        if len(ids) == 1:
            r['athlete_id'] = ids[0]
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fra', required=True)
    ap.add_argument('--til', required=True)
    ap.add_argument('--maks', type=int, default=0, help='høyst så mange arrangementer')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])
    liste = arrangementer(args.fra, args.til)
    if args.maks:
        liste = liste[:args.maks]
    logger.info(f'{len(liste)} arrangementer med resultater under {FORBUND}, {args.fra}–{args.til}')

    tot_lop = tot_res = tot_koblet = 0
    for e in liste:
        ev = hent(f'Event/{e["Id"]}')
        if not ev:
            logger.warning(f'{e["Id"]} {e["Name"]}: fikk ikke hentet arrangementet')
            continue
        # Løypegrad gjelder bare løpet (distansen) som er gradert
        graderte = {}
        for r in (e.get('Race') or {}).values():
            g = grad_fra(((r or {}).get('Grade') or {}).get('Name'))
            if g:
                graderte[(r or {}).get('Distance') or 0] = g
        ranking = any(((r or {}).get('RaceQuality') or {}).get('Name') for r in (e.get('Race') or {}).values())

        arr = {
            'kilde': 'eqtiming', 'kilde_id': e['Id'], 'navn': e['Name'].strip(),
            'dato': e['Starttime'][:10], 'sted': ((e.get('City') or {}).get('Name') or '').strip() or None,
            'arrangor': (e.get('Organizer') or {}).get('Name'), 'gren': (e.get('Sport') or {}).get('Name'),
            'nivaa': (e.get('Sportlevel') or {}).get('Name'), 'forbund': FORBUND,
            'hentet': datetime.now().isoformat(),
        }
        oppgitt = [r.get('Distance') for r in (e.get('Race') or {}).values() if (r or {}).get('Distance')]
        stopp = stoppstasjoner(ev)
        lop_rader = []
        for etappe, stasjon, km in stopp:
            items = resultater(e['Id'], etappe, stasjon)
            if not items:
                continue
            # Distanse: målstasjonen, ellers startgruppens navn («2 km», «3 runder (5 km)»),
            # ellers løpslisten når arrangementet bare har ett løp.
            grupper: dict[int | None, list[dict]] = {}
            for it in items:
                pulje = ((it.get('Deltaker') or {}).get('Pulje') or {}).get('Navn')
                dist = (normaliser_distanse(km) or distanse_fra_tekst(pulje)
                        or (normaliser_distanse(oppgitt[0] / 1000) if len(oppgitt) == 1 and len(stopp) == 1 else None))
                u = (it.get('Deltaker') or {}).get('Utover') or {}
                navn = pent_navn(u)
                if not navn:
                    continue
                kj = (u.get('Kjonn') or '').upper()[:1]
                status = 'OK' if it.get('StatusTekst') == 'TIME' else (it.get('StatusTekst') or 'DNF')
                grupper.setdefault(dist, []).append({
                    'kilde_id': it['EtappeDeltakerUID'],
                    'plass': (it.get('Plassering') or {}).get('Total') if status == 'OK' else None,
                    'navn': navn, 'kjonn': kj if kj in ('M', 'F') else None,
                    'fodt': u.get('Aar') or None,
                    'klubb': ((u.get('Klubb') or {}).get('Navn') or u.get('Klubbnavn') or None),
                    'klasse': ((it.get('Deltaker') or {}).get('Klasse') or {}).get('Navn'),
                    'tid_ms': it.get('AkkumulertTid') if status == 'OK' else None,
                    'status': status, 'athlete_id': None,
                })
            for dist, res in grupper.items():
                unike = {}
                for r in res:  # samme løper kan stå flere ganger (runder); behold første
                    unike.setdefault(r['kilde_id'], r)
                res = list(unike.values())
                if len(grupper) > 1:  # plassering innen hver distanse
                    for i, r in enumerate(sorted((r for r in res if r['tid_ms']), key=lambda r: r['tid_ms']), 1):
                        r['plass'] = i
                grad = graderte.get(dist) or (graderte.get(0) if len(graderte) == 1 and len(stopp) == 1 else None)
                nivaa, merknad = kvalitetsnivaa(dist, grad or ''), None
                if arr['gren'] not in RANGERES:
                    nivaa = 'C'
                beste = min((r['tid_ms'] for r in res if r['tid_ms']), default=None)
                if dist and dist >= 800 and beste and beste < dist * MINSTE_MS_PER_M:
                    nivaa = 'C'
                    merknad = 'Vinnertiden er raskere enn mulig på oppgitt distanse. Distansen må kontrolleres.'
                lop_rader.append(({
                    'kilde_id': stasjon, 'navn': f'{dist / 1000:g} km' if dist else None,
                    'distanse_m': dist, 'loypegrad': grad, 'ranking': ranking,
                    'kvalitetsnivaa': nivaa, 'merknad': merknad,
                }, res))

        if not lop_rader:
            continue
        alle = [r for _, res in lop_rader for r in res]
        koblet = koble_utovere(sb, alle)
        tot_lop += len(lop_rader)
        tot_res += len(alle)
        tot_koblet += koblet
        logger.info(f'{arr["dato"]} {arr["navn"]}: {len(lop_rader)} løp '
                    f'({", ".join(f"{l[0]["navn"]} {l[0]["kvalitetsnivaa"]}" for l in lop_rader)}), '
                    f'{len(alle)} løpere, {koblet} koblet')
        if args.dry_run:
            continue

        a = sb.table('lop_arrangement').upsert(arr, on_conflict='kilde,kilde_id').execute().data[0]
        for lop, res in lop_rader:
            lop['arrangement_id'] = a['id']
            l = sb.table('lop_lop').upsert(lop, on_conflict='arrangement_id,kilde_id,distanse_m').execute().data[0]
            for r in res:
                r['lop_id'] = l['id']
            for i in range(0, len(res), 500):
                sb.table('lop_resultat').upsert(res[i:i + 500], on_conflict='lop_id,kilde_id').execute()

    logger.info(f'Ferdig{" (dry-run)" if args.dry_run else ""}: {tot_lop} løp, {tot_res} resultater, '
                f'{tot_koblet} koblet til utøverregisteret')


if __name__ == '__main__':
    sys.exit(main())
