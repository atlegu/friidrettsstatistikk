"""Hent «Ikke godkjente resultater» med årsak fra kildens utøversider.

BAKGRUNN
--------
minfriidrettsstatistikk.info viser på hver utøverside en tabell «Ikke godkjente
resultater» under øvelsen, med årsak (kort bane, ikke medlem av NFIF,
feilkoblet startutstyr, for stor innendørsbane, ekstraløp, for mye vind ...).
Stevnesidene som den nattlige importen leser, viser ikke dette. Basen hadde
heller ikke noe sted for årsaken, så slike resultater sto som godkjente
(Kåre Strande 200 m 23.24, Fagernes 2002: kort bane).

HVA SKRIPTET GJØR
-----------------
  For hver utøver fra utovere_til_kontroll() (kilde-id og resultater, ikke
  kontrollert, nyest aktive først): hent utøversiden (POST
  UtoverStatistikk.php, 1,5 s pause; mellomlagrede sider i logs/kilde_utover/
  brukes om de finnes), les tabellene «Ikke godkjente resultater», og finn
  raden i basen (samme utøver, øvelse, dato og resultat).
    - ikke_godkjent_aarsak settes til kildens årsak.
    - status settes til IKKE_GODKJENT, unntatt for ren vind («For mye vind»,
      «Manglende informasjon om vind»), som vindregelen håndterer.
  Hver utøver registreres i kilde_utover_kontroll, så en avbrutt kjøring
  fortsetter der den slapp. Endrede rader logges i opprydding_ikke_godkjente.

KJØRING
-------
    python hent_ikke_godkjente.py --antall 50            # tørrkjøring
    python hent_ikke_godkjente.py --antall 70000 --apply  # hele basen (~27 timer)
    python hent_ikke_godkjente.py --eldre-enn '28 days' --antall 3000 --apply   # jevnlig
"""

import argparse
import logging
import os
import re
import sys
import time
from collections import Counter
from datetime import date, datetime, timezone
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
                              logging.FileHandler(HER / 'logs' / f'hent_ikke_godkjente_{TS}.log', encoding='utf-8')],
                    force=True)
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)

KILDE = 'https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php'
LAGER = HER / 'logs' / 'kilde_utover'
PAUSE = 1.5
REN_VIND = ('for mye vind', 'manglende informasjon om vind')
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) friidrettsresultater.no/1.0'})


def hent_side(ext_id):
    fil = LAGER / f'{ext_id}.htm'
    if fil.exists():
        return fil.read_text(encoding='utf-8')
    for forsok in range(3):
        try:
            time.sleep(PAUSE * (1 + 2 * forsok))
            r = session.post(KILDE, data={'athlete': ext_id, 'type': 'RES'}, timeout=30)
            if r.status_code == 429:
                log.warning("429 fra kilden, venter 60 s")
                time.sleep(60)
                continue
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text
        except requests.RequestException as e:
            feil = e
    raise feil


def verdi(tekst, rt):
    """Kildens resultat («23,24(+1,7)», «1,03,81», «6,10», «3014») -> performance_value."""
    t = re.split(r'[(\s]', tekst.strip())[0].rstrip('+').replace('mx', '').replace('i', '')
    deler = t.split(',')
    if not all(d.isdigit() for d in deler):
        return None
    if rt == 'time':
        if len(deler) == 1:
            return int(deler[0]) * 100
        frac = deler[-1]
        hundredeler = int(frac) * (10 if len(frac) == 1 else 1)
        sek = 0
        for d in deler[:-1]:
            sek = sek * 60 + int(d)
        return sek * 100 + hundredeler
    if rt in ('distance', 'height'):
        if len(deler) != 2:
            return None
        return int(deler[0]) * 1000 + int(deler[1].ljust(2, '0')[:2]) * 10
    return int(deler[0]) if len(deler) == 1 else None


def ikke_godkjente(html):
    """[(øvelse, dato, resultat, årsak)] fra tabellene «Ikke godkjente resultater»."""
    s = BeautifulSoup(html, 'html.parser')
    ut = []
    for h in s.find_all('h4', string=lambda t: t and 'Ikke godkjente' in t):
        # Siden har et tomt <h3> etter hver øvelse: finn nærmeste med tekst
        ov = next((x.get_text(strip=True) for x in h.find_all_previous('h3')
                   if x.get_text(strip=True) and not x.get_text(strip=True).startswith('Født')), '')
        tab = h.find_next('table')
        if not tab or not tab.find('tr'):
            continue
        hode = [c.get_text(strip=True).upper() for c in tab.find('tr').find_all(['th', 'td'])]
        if not {'ÅR', 'RESULTAT', 'DATO', 'ÅRSAK'} <= set(hode):
            continue
        i_aar, i_res, i_dato, i_aarsak = (hode.index(k) for k in ('ÅR', 'RESULTAT', 'DATO', 'ÅRSAK'))
        for tr in tab.find_all('tr')[1:]:
            c = [x.get_text(' ', strip=True) for x in tr.find_all('td')]
            if len(c) != len(hode):
                continue
            am = re.match(r'(\d{4})', c[i_aar])
            dm = re.fullmatch(r'(\d{2})\.(\d{2})\.(\d{2})', c[i_dato])
            if not am or not dm or int(dm.group(3)) != int(am.group(1)) % 100:
                continue
            try:
                dato = date(int(am.group(1)), int(dm.group(2)), int(dm.group(1)))
            except ValueError:      # ugyldig dato i kilden («31.02.»)
                continue
            res, aarsak = c[i_res], c[i_aarsak]
            ut.append((ov, dato, res, aarsak.strip()))
    return ut


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--antall', type=int, default=50)
    ap.add_argument('--eldre-enn', default=None, help="kontroller også utøvere kontrollert før dette (f.eks. '28 days')")
    args = ap.parse_args()

    import update_results as u   # kildens øvelsesnavn -> kode
    ev = sb.table('events').select('id,code,name,result_type').execute().data
    per_kode = {e['code']: e for e in ev}
    per_navn = {e['name']: e for e in ev}

    def ovelser(navn):
        """Kandidatøvelser: importens oversettelse og eksakt navn («Lengde (Sone
        0,5m)» oversettes til en annen kode enn resultatene ligger under)."""
        ut = [per_kode.get(u.EVENT_NAME_TO_CODE.get(navn)), per_navn.get(navn)]
        return list({e['id']: e for e in ut if e}.values())

    teller, aarsaker, ukjente_ov = Counter(), Counter(), Counter()
    behandlet = 0
    while behandlet < args.antall:
        ko = sb.rpc('utovere_til_kontroll', {'p_antall': min(500, args.antall - behandlet),
                                             'p_eldre_enn': args.eldre_enn}).execute().data
        if not ko:
            break
        for a in ko:
            behandlet += 1
            try:
                rader = ikke_godkjente(hent_side(a['external_id']))
            except Exception as e:
                teller['feil ved henting'] += 1
                if args.apply:
                    sb.table('kilde_utover_kontroll').upsert({'athlete_id': a['id'], 'kontrollert': datetime.now(timezone.utc).isoformat(),
                                                              'feil': str(e)[:200]}).execute()
                continue
            merket = ikke_funnet = 0
            # Alle utøverens resultater i ett kall; matching i minnet
            mine = []
            if rader:
                fra = 0
                while True:
                    bit = sb.table('results').select('id,event_id,date,performance,performance_value,status,ikke_godkjent_aarsak') \
                        .eq('athlete_id', a['id']).order('id').range(fra, fra + 999).execute().data
                    mine += bit
                    if len(bit) < 1000:
                        break
                    fra += 1000
            per_nokkel = {}
            for r in mine:
                per_nokkel.setdefault((r['event_id'], r['date']), []).append(r)
            endringer = {}   # (aarsak, ren_vind) -> [rad]
            for ov_navn, dato, res, aarsak in rader:
                kand = ovelser(ov_navn)
                if not kand:
                    ukjente_ov[ov_navn] += 1
                    ikke_funnet += 1
                    continue
                treff = []
                for e in kand:
                    pv = verdi(res, e['result_type'])
                    if pv is None:
                        continue
                    treff += [r for r in per_nokkel.get((e['id'], dato.isoformat()), [])
                              if r['performance_value'] is not None and abs(r['performance_value'] - pv) <= 1]
                if not treff:
                    ikke_funnet += 1
                    teller['ikke funnet i basen'] += 1
                    if teller['ikke funnet i basen'] <= 30:
                        log.info(f"   ikke funnet: {a['navn']} | {ov_navn} {dato} {res[:15]} | {aarsak[:30]}")
                    continue
                ren_vind = aarsak.lower().startswith(REN_VIND)
                for t in treff:
                    if t['ikke_godkjent_aarsak'] == aarsak and (ren_vind or t['status'] == 'IKKE_GODKJENT'):
                        continue
                    endringer.setdefault((aarsak, ren_vind), []).append(t)
                    aarsaker[aarsak[:60]] += 1
                    teller['vind (bare årsak)' if ren_vind else 'merket ikke godkjent'] += 1
                    merket += 1
                    if not ren_vind:
                        log.info(f"   {a['navn']} | {ov_navn} {dato} {t['performance']} | {aarsak}")
            if args.apply and endringer:
                sb.table('opprydding_ikke_godkjente').insert(
                    [{'result_id': t['id'], 'gammel_status': t['status'], 'aarsak': aarsak}
                     for (aarsak, _), tt in endringer.items() for t in tt]).execute()
                for (aarsak, ren_vind), tt in endringer.items():
                    endring = {'ikke_godkjent_aarsak': aarsak}
                    if not ren_vind:
                        endring['status'] = 'IKKE_GODKJENT'
                    sb.table('results').update(endring).in_('id', [t['id'] for t in tt]).execute()
            if args.apply:
                sb.table('kilde_utover_kontroll').upsert({'athlete_id': a['id'], 'kontrollert': datetime.now(timezone.utc).isoformat(),
                                                          'ikke_godkjente': len(rader), 'merket': merket,
                                                          'ikke_funnet': ikke_funnet, 'feil': None}).execute()
            if behandlet % 250 == 0:
                log.info(f"{behandlet} utøvere kontrollert. {dict(teller)}")
        if not args.apply:
            break   # tørrkjøring: køen endres ikke, ta bare én runde

    log.info(f"Ferdig: {behandlet} utøvere. {dict(teller)}")
    for k, v in aarsaker.most_common(25):
        log.info(f"   {v} | {k}")
    if ukjente_ov:
        log.info(f"Øvelsesnavn uten kode: {dict(ukjente_ov.most_common(15))}")
    if not args.apply:
        log.info("DRY-RUN. Kjør med --apply.")


if __name__ == '__main__':
    main()
