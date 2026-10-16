"""Kontroller de offisielle norske mastersrekordene mot basen, og legg inn de som mangler.

BAKGRUNN
--------
Rekordlistene fra Stein Fossen (kappgang: Erling Andersen) ligger som PDF i
NFIFProsjekt/: norgesrekorder-mvu, -kvu (ute, pr. 31.12.2025) og -mvi, -kvi
(inne, pr. 30.06.2026). Hver linje er én rekord: klasse, resultat, vind,
navn, klubb, (fødselsår), sted, dato. En linje uten klasse rett under er en
manuelt tidtatt rekord eller en rekord med gammel spydtype (***).

HVA SKRIPTET GJØR
-----------------
  1. Leser PDF-ene (pdftotext -layout) til én rad per rekord.
  2. Leter i basen etter resultatet: samme øvelse (alle koder øvelsen kan
     ligge under), samme resultat, innen tre dager fra datoen. Treff på en
     utøver med annet navn regnes også som funnet, men merkes.
  3. Rapporten (opprydding/masters_rekorder_<tid>.csv) viser for hver
     rekord: finnes / finnes med annen dato / mangler / kan ikke legges inn
     (øvelse uten kode, ufullstendig dato, stafett).
  4. Med --apply legges manglende rekorder inn: utøveren kobles på navn og
     fødselsår (opprettes ellers), stevnet slås opp på sted og dato (opprettes
     ellers, med samme navneform som den historiske importen). Alle rader får
     egen kilde og importbatch, så de kan fjernes samlet.

KJØRING
-------
    python masters_rekorder_fra_liste.py            # tørrkjøring, bare rapport
    python masters_rekorder_fra_liste.py --apply
"""

import argparse
import csv
import json
import logging
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

HER = Path(__file__).parent
load_dotenv(HER / '.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
LOGG = HER / 'logs'; LOGG.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(LOGG / f'masters_rekorder_fra_liste_{TS}.log', encoding='utf-8')])
logging.getLogger('httpx').setLevel(logging.WARNING)
log = logging.getLogger(__name__)

PDF_MAPPE = HER.parent / 'NFIFProsjekt'
FILER = {  # fil -> (kjønn, inne)
    'norgesrekorder-mvu.pdf': ('M', False),
    'norgesrekorder-kvu.pdf': ('F', False),
    'norgesrekorder-mvi.pdf': ('M', True),
    'norgesrekorder-kvi.pdf': ('F', True),
}
KILDE_NAVN = 'Norske mastersrekorder (Stein Fossen / Erling Andersen)'

# Rekorder som ikke legges inn fordi basen har et annet resultat samme dag.
# Kontrolleres for hånd (16.10.2026).
AVVIK = {
    ('Erik Tysse', '11:18.45'): 'basen har 11:28.45 samme dag; en av dem er feil',
    ('Merete Helgheim', '26:13.98'): 'basen hadde 26:13 (avkortet); rettet til 26:13.98 for hånd',
}

# Navn i rekordlista -> navn i basen, kontrollert for hånd 16.10.2026
# (samme fødselsår, samme kjønn, navneform eller skrivemåte avviker)
ALIAS = {
    ('Halldis Marit (Waaga) (Nagell-)Dahl', 1942): 'Halldis Marit Nagell-Dahl',
    ('Astrid Førde', 1933): 'Astrid Mæhre Førde Johannessen',
    ('Trond Erik Nilsen', 1972): 'Trond-Erik Nilsen',
    ('Lisbet Pedersen', 1975): 'Lisbeth Pedersen',
}

# ---------------------------------------------------------------- øvelser

HEKK = {'106.7': '106_7cm', '99.1': None, '91.4': '91_4cm', '84.0': '84cm', '76.2': '76_2cm', '68.6': '68cm'}
KULE = {'7.26': 'kule_7_26kg', '6.0': 'kule_6kg', '5.0': 'kule_5kg', '4.0': 'kule_4kg', '3.0': 'kule_3kg', '2.0': 'kule_2kg'}
DISKOS = {'2.0': 'diskos_2kg', '1.5': 'diskos_1_5kg', '1.0': 'diskos_1kg', '0.75': 'diskos_750g'}
SLEGGE = {'7.26': ['slegge_726kg/1215cm', 'slegge_7_26kg'],
          '6.0': ['slegge_60kg/1215cm', 'slegge_6kg', 'slegge_60kg/110cm'],
          '5.0': ['slegge_50kg/120cm', 'slegge_5kg'],
          '4.0': ['slegge_40kg/1195cm', 'slegge_4kg', 'slegge_40kg/100cm'],
          '3.0': ['slegge_30kg_1195cm', 'slegge_30kg/110cm', 'slegge_3kg'],
          '2.0': ['slegge_20kg/110cm', 'slegge_2kg']}
SPYD = {'800': 'spyd_800g', '700': 'spyd_700g', '600': 'spyd_600g', '500': 'spyd_500g', '400': 'spyd_400g'}
VEKT = {'15.88': 'vektkast_1588kg', '11.34': 'vektkast_1134kg', '9.08': 'vektkast_908kg',
        '7.26': 'vektkast_726kg', '5.45': 'vektkast_545kg', '4.00': 'vektkast40kg'}
GANG_BANE = {'3000': ['kappgang_3000_m', '3000mg'], '5000': ['kappgang_5000_m', '5000mg'],
             '10000': ['kappgang_10000_m', '10000mg'], '20000': ['kappgang_20000_m']}
GANG_VEI = {'3': ['kappgang_3_km'], '5': ['kappgang_5_km'], '10': ['kappgang_10_km'],
            '15': ['kappgang_15_km'], '20': ['kappgang_20_km', '20kmg'], '25': ['kappgang_25_km'],
            '30': ['kappgang_30_km'], '35': ['kappgang_35_km'], '50': ['kappgang_50_km']}


def ovelse(overskrift: str, gammel_spyd: bool):
    """Overskrift i lista -> (koder å lete i, første er den vi legger inn i) eller None."""
    o = overskrift.strip()
    if re.search(r'stafett|relay', o, re.I):
        return 'stafett'
    m = re.match(r'^(\d+)m( menn)?$', o)
    if m:
        return [f'{m.group(1)}m']
    m = re.match(r'^(\d+)m hekk / hurdles ([\d.]+) cm$', o)
    if m:
        h = HEKK.get(m.group(2))
        return [f'{m.group(1)}mh_{h}', f'{m.group(1)}mh'] if h else None
    m = re.match(r'^(\d+)m hinder / steeplechase ([\d.]+) cm$', o)
    if m:
        h = HEKK.get(m.group(2))
        return [f'{m.group(1)}mhinder_{h}', f'{m.group(1)}mhinder'] if h else None
    m = re.match(r'^(\d+) ?m kappgang', o)
    if m:
        return GANG_BANE.get(m.group(1))
    m = re.match(r'^(\d+) km kappgang', o)
    if m:
        return GANG_VEI.get(m.group(1))
    faste = {'Høyde / High Jump': ['hoyde'], 'Stav / Pole Vault': ['stav'], 'Lengde / Long Jump': ['lengde'],
             'Tresteg / Triple Jump': ['tresteg'], 'Høyde u.t. / Standing High Jump': ['hoyde_ut'],
             'Lengde u.t. / Standing Long Jump': ['lengde_ut']}
    if o in faste:
        return faste[o]
    m = re.match(r'^(Kule|Diskos|Slegge|Spyd|Vektkast) / \w+ T\w+ ([\d.]+) ?(kg|g)$', o) \
        or re.match(r'^(Kule|Diskos|Slegge|Spyd|Vektkast) / [\w ]+? ([\d.]+) ?(kg|g)$', o)
    if m:
        art, vekt = m.group(1), m.group(2)
        if art == 'Kule':
            k = KULE.get(vekt); return [k, 'kule'] if k else None
        if art == 'Diskos':
            k = DISKOS.get(vekt); return [k, 'diskos'] if k else None
        if art == 'Slegge':
            k = SLEGGE.get(vekt); return k + ['slegge'] if k else None
        if art == 'Spyd':
            if gammel_spyd:  # *** = gammel spydtype; bare 800 g har egen kode
                return ['spyd_800g_old'] if vekt == '800' else None
            k = SPYD.get(vekt)
            if not k:
                return None
            return [k, 'spyd', 'spyd_700_gram_2025'] if vekt == '700' else [k, 'spyd']
        if art == 'Vektkast':
            k = VEKT.get(vekt); return [k, 'vektkast'] if k else None
    return None


# ---------------------------------------------------------------- tolking

REKORD = re.compile(
    r'^\s*(?:(?P<kl>[MK]\d{2,3}-\d{2,3})\s+)?(?P<perf>\d[\d:.,]*)\s+'
    r'(?:(?P<vind>[+-]\d+,\d+|\*\*\*|\(\d\))\s+)?'
    r'(?P<nk>\S.*?)\s+\((?P<fodt>\d{2}|\d{4})\)\s+'
    r'(?:(?P<sted>\S.*?)\s+)?(?P<dato>(?:\d{2}-)?\d{2}\.\d{2}\.\d{4}|\.\d{2}\.\d{4}|\.\d{4})\s*$')
SLUTTER_MED_DATO = re.compile(r'\d{4}\s*$')
KLASSE_ALENE = re.compile(r'^\s*[MK]\d{2,3}-\d{2,3}\s*$')
STOY = re.compile(r'^\s*(Utarbeidet|\(erlingandersen|Norske |Menn |Kvinner |pr\. |\*\*\* -|Side )')


def les_pdf(fil: Path, kjonn: str, inne: bool) -> list:
    tekst = subprocess.run(['pdftotext', '-layout', str(fil), '-'], capture_output=True, text=True, check=True).stdout
    rader, overskrift, klasse = [], None, None
    for linje in tekst.splitlines():
        if not linje.strip() or STOY.match(linje) or linje.strip().startswith('('):
            continue
        m = REKORD.match(linje)
        if m:
            if m.group('kl'):
                klasse = m.group('kl')
            rader.append({'fil': fil.name, 'kjonn': kjonn, 'inne': inne, 'overskrift': overskrift,
                          'klasse': klasse, 'hoved': bool(m.group('kl')), **{k: m.group(k) for k in
                          ('perf', 'vind', 'nk', 'fodt', 'sted', 'dato')}})
            continue
        if KLASSE_ALENE.match(linje):
            klasse = linje.strip()
            continue
        if SLUTTER_MED_DATO.search(linje):
            # Stafettlag (uten fødselsår), «***» innendørs (sannsynligvis lav
            # grop, ikke rekord) eller annet vi ikke kan tolke
            if overskrift and 'stafett' not in overskrift.lower() and '***' not in linje:
                log.warning(f"Ikke tolket i {fil.name} / {overskrift}: {linje.strip()}")
            continue
        overskrift = re.sub(r'\s+', ' ', linje.strip())
        klasse = None
    return rader


def fodselsaar(fodt: str, aar: int) -> int:
    y = int(fodt)
    if y >= 1000:
        return y
    # Siste århundre som gjør utøveren minst 35 år (Harald Hoffengh (95) i 1950 = 1895)
    return max(h + y for h in (1800, 1900, 2000) if h + y <= aar - 35)


def normaliser_tid(perf: str) -> str:
    # «20.47,9» (trykkfeil i lista) = 20:47.9
    m = re.match(r'^(\d+)\.(\d{2}),(\d)$', perf)
    if m:
        return f'{m.group(1)}:{m.group(2)}.{m.group(3)}'
    return perf.replace(',', '.')


def verdi(perf: str, rt: str):
    """Resultat -> performance_value slik basen lagrer det (hundredeler / millimeter)."""
    if rt == 'time':
        deler = perf.split(':')
        try:
            minutter = 0
            for d in deler[:-1]:          # timer og minutter
                minutter = minutter * 60 + int(d)
            return round((minutter * 60 + float(deler[-1])) * 100)
        except ValueError:
            return None
    try:
        return round(float(perf) * 1000)
    except ValueError:
        return None


def tid_tekst(perf: str) -> str:
    """Sekunder over 60 uten kolon («143.02») vises som 2:23.02, som i basen."""
    if ':' in perf:
        return perf
    s = float(perf)
    if s < 60:
        return perf
    desimaler = perf.split('.')[1] if '.' in perf else ''
    m, rest = divmod(s, 60)
    sek = f'{rest:0{3 + len(desimaler) if desimaler else 2}.{len(desimaler)}f}' if desimaler else f'{int(rest):02d}'
    return f'{int(m)}:{sek}'


def navnevarianter(navn: str) -> list:
    """«Heidi Barth (Andersen)» -> Heidi Barth, Heidi Andersen, Heidi Barth Andersen."""
    ren = re.sub(r'\s+', ' ', re.sub(r'\([^)]*\)', ' ', navn)).strip()
    ut = [ren]
    for p in re.findall(r'\(([^)]*)\)', navn):
        if navn.strip().startswith(f'({p})'):          # «(Karl) Arthur Andersen»
            ut.append(f'{p} {ren}')
        else:                                          # pikenavn
            ut.append(f'{ren.split()[0]} {p}')
            ut.append(f'{ren} {p}')
    return [re.sub(r'\s+', ' ', v.replace('.', '')).lower() for v in ut]


# ---------------------------------------------------------------- basen

def hent_alle(tabell, felt, filtre=lambda q: q):
    ut, fra = [], 0
    while True:
        r = filtre(sb.table(tabell).select(felt)).order('id').range(fra, fra + 999).execute().data
        ut.extend(r)
        if len(r) < 1000:
            return ut
        fra += 1000


def avkortet_form(basen: str, presis: str) -> bool:
    """«19:15» er avkortet form av 19:15.33, «1.10» (feil format) av 1:10.63."""
    if basen == presis:
        return False
    if presis.startswith(basen):
        return True
    return re.match(r'^\d+\.\d\d$', basen) is not None and presis.startswith(basen.replace('.', ':') + '.')


def rett_avkortede(rapport: Path, apply: bool):
    """Rader i basen med samme person, øvelse og dag som en rekord, men med
    avkortet tid (kappgang og lange løp i hele minutter/sekunder, 400 m som
    «1.10»), rettes til tiden i rekordlista. En rad lagt inn av denne
    importen for samme rekord slettes da, så rekorden står én gang."""
    events = {e['code']: e for e in sb.table('events').select('id,code,result_type').execute().data}
    batch = [b['id'] for b in sb.table('import_batches').select('id,name').like('name', 'Mastersrekorder fra rekordlistene%').execute().data]
    rettet = slettet = 0
    for r in csv.DictReader(open(rapport, encoding='utf-8'), delimiter=';'):
        if not r['koder'] or not r['pv'] or events[r['koder'].split(',')[0]]['result_type'] != 'time':
            continue
        dm = re.match(r'^(?:(\d{2})-)?(\d{2}\.\d{2}\.\d{4})$', r['dato'])
        if not dm:
            continue
        d_slutt = datetime.strptime(dm.group(2), '%d.%m.%Y').date()
        d = d_slutt.replace(day=int(dm.group(1))) if dm.group(1) else d_slutt
        presis = tid_tekst(normaliser_tid(r['perf']))
        ids = [events[k]['id'] for k in r['koder'].split(',')]
        rader = sb.table('results').select('id,athlete_id,performance,date,import_batch_id,athletes(full_name,gender)') \
            .in_('event_id', ids).gte('date', (d - timedelta(days=3)).isoformat()) \
            .lte('date', (d_slutt + timedelta(days=3)).isoformat()).execute().data
        listens = set()
        for v in navnevarianter(r['navn']):
            listens |= set(v.replace('-', ' ').split())
        def samme(x):
            a = x.get('athletes') or {}
            return bool(set((a.get('full_name') or '').lower().replace('-', ' ').split()) & listens)
        avkortede = [x for x in rader if samme(x) and avkortet_form(x['performance'], presis)]
        for aid in {x['athlete_id'] for x in avkortede}:
            hans = [x for x in rader if x['athlete_id'] == aid]
            korte = [x for x in avkortede if x['athlete_id'] == aid]
            presise = [x for x in hans if x not in korte and any(avkortet_form(k['performance'], x['performance']) for k in korte)
                       and x['import_batch_id'] not in batch]
            if presise:
                # Den presise tiden finnes alt: den avkortede raden er en dublett
                for x in korte:
                    log.info(f"{r['navn']} {r['overskrift']} {x['date']}: slett «{x['performance']}» "
                             f"(dublett av {presise[0]['performance']} {presise[0]['date']})")
                    if apply:
                        sb.table('opprydding_masters_20261016').insert({'tabell': 'results', 'id': x['id'],
                            'kolonne': 'slettet (avkortet dublett)', 'gammel': json.dumps(x, default=str), 'ny': None}).execute()
                        sb.table('results').delete().eq('id', x['id']).execute()
                    slettet += 1
                continue
            if len(korte) > 1:
                log.warning(f"{r['navn']} {r['overskrift']}: {len(korte)} avkortede rader, ingen presis; rettes ikke")
                continue
            x = korte[0]
            # Mesterskap lagres ofte med startdatoen: den presise tiden kan
            # ligge noen dager unna og gjør da den avkortede raden til dublett
            naer = sb.table('results').select('id,date').in_('event_id', ids).eq('athlete_id', aid) \
                .eq('performance_value', verdi(presis, 'time')) \
                .gte('date', (d - timedelta(days=10)).isoformat()).lte('date', (d_slutt + timedelta(days=10)).isoformat()) \
                .execute().data
            naer = [y for y in naer if y['id'] != x['id']]
            if naer:
                log.info(f"{r['navn']} {r['overskrift']} {x['date']}: slett «{x['performance']}» (dublett av {presis} {naer[0]['date']})")
                if apply:
                    sb.table('opprydding_masters_20261016').insert({'tabell': 'results', 'id': x['id'],
                        'kolonne': 'slettet (avkortet dublett)', 'gammel': json.dumps(x, default=str), 'ny': None}).execute()
                    sb.table('results').delete().eq('id', x['id']).execute()
                slettet += 1
                continue
            # Rekorden lagt inn av denne importen for samme utøver: den
            # opprinnelige raden (på det riktige stevnet) beholdes og rettes
            duplikat = [y for y in rader if y['import_batch_id'] in batch and y['performance'] == presis]
            log.info(f"{r['navn']} {r['overskrift']} {x['date']}: {x['performance']} -> {presis}"
                     + (f" (og slett {len(duplikat)} innlagt dublett)" if duplikat else ''))
            if apply:
                sb.table('opprydding_masters_20261016').insert({'tabell': 'results', 'id': x['id'], 'kolonne': 'performance',
                                                                'gammel': x['performance'], 'ny': presis}).execute()
                sb.table('results').update({'performance': presis}).eq('id', x['id']).execute()
                for y in duplikat:
                    sb.table('opprydding_masters_20261016').insert({'tabell': 'results', 'id': y['id'], 'kolonne': 'slettet (dublett av rettet rad)',
                                                                    'gammel': json.dumps(y, default=str), 'ny': None}).execute()
                    sb.table('results').delete().eq('id', y['id']).execute()
            rettet += 1; slettet += len(duplikat)
    log.info(f"{'Rettet' if apply else 'Ville rettet'} {rettet} avkortede tider, "
             f"{'slettet' if apply else 'ville slettet'} {slettet} avkortede dubletter.")


def merk_offisielle(rapport: Path, apply: bool):
    """Finn resultatet i basen for hver godkjent rekord og før det inn i
    masters_offisielle_rekorder. Hovedlinjene tas med, og gammel spydtype
    (egen øvelse). Manuelle tilleggslinjer tas ikke med: de ville slått den
    elektroniske rekorden i samme klasse."""
    events = {e['code']: e for e in sb.table('events').select('id,code,result_type').execute().data}
    funnet, ikke = [], []
    for r in csv.DictReader(open(rapport, encoding='utf-8'), delimiter=';'):
        if not r['koder'] or not r['pv']:
            continue
        koder = r['koder'].split(',')
        if r['hoved'] != 'True' and koder[0] != 'spyd_800g_old':
            continue
        dm = re.match(r'^(?:(\d{2})-)?(\d{2}\.\d{2}\.\d{4})$', r['dato'])
        d_slutt = datetime.strptime(dm.group(2), '%d.%m.%Y').date()
        d = d_slutt.replace(day=int(dm.group(1))) if dm.group(1) else d_slutt
        if r['status'] == 'finnes med annen dato' and r['merknad']:
            d = d_slutt = date.fromisoformat(r['merknad'])
        pv = int(r['pv'])
        rader = sb.table('results').select('id,date,athlete_id,athletes(full_name,gender)') \
            .in_('event_id', [events[k]['id'] for k in koder]).eq('performance_value', pv) \
            .gte('date', (d - timedelta(days=10)).isoformat()).lte('date', (d_slutt + timedelta(days=10)).isoformat()) \
            .execute().data
        listens = set()
        for v in navnevarianter(r['navn']):
            listens |= set(v.replace('-', ' ').split())
        kjonn = 'M' if r['fil'].startswith('norgesrekorder-m') else 'F'
        rader = [x for x in rader if (x.get('athletes') or {}).get('gender') in (kjonn, None)
                 and set(((x.get('athletes') or {}).get('full_name') or '').lower().replace('-', ' ').split()) & listens]
        if not rader:
            ikke.append(r); continue
        rader.sort(key=lambda x: abs((date.fromisoformat(x['date']) - d).days))
        funnet.append({'result_id': rader[0]['id'], 'liste': r['fil'][15:18], 'klasse': r['klasse'],
                       'offisielt_resultat': r['perf']})
    unike = {f['result_id']: f for f in funnet}
    log.info(f"{len(unike)} godkjente rekorder funnet i basen, {len(ikke)} ikke funnet")
    for r in ikke:
        log.info(f"   ikke funnet: {r['fil'][15:18]} {r['overskrift']} {r['klasse']} {r['perf']} {r['navn']} {r['dato']} ({r['status']})")
    if apply:
        rader = list(unike.values())
        for i in range(0, len(rader), 200):
            sb.table('masters_offisielle_rekorder').upsert(rader[i:i + 200]).execute()
        log.info("Lagret i masters_offisielle_rekorder. Husk refresh av masters_resultater.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--merk-offisielle', metavar='RAPPORT_CSV',
                    help='fyll masters_offisielle_rekorder med resultat-id for hver godkjent rekord')
    ap.add_argument('--rett-avkortede', metavar='RAPPORT_CSV',
                    help='rett avkortede tider i basen mot rekordlista (rapport fra en tidligere kjøring)')
    args = ap.parse_args()
    if args.merk_offisielle:
        return merk_offisielle(Path(args.merk_offisielle), args.apply)
    if args.rett_avkortede:
        return rett_avkortede(Path(args.rett_avkortede), args.apply)

    rekorder = []
    for fil, (kjonn, inne) in FILER.items():
        r = les_pdf(PDF_MAPPE / fil, kjonn, inne)
        log.info(f"{fil}: {len(r)} rekorder")
        rekorder += r

    events = {e['code']: e for e in sb.table('events').select('id,code,result_type,category').execute().data}
    sesonger = {(s['year'], s['indoor']): s['id'] for s in sb.table('seasons').select('id,year,indoor').execute().data}
    klubber = {}
    for k in hent_alle('clubs', 'id,name'):
        klubber.setdefault(k['name'].lower(), k['id'])
    log.info("Henter utøvere ...")
    utovere = hent_alle('athletes', 'id,first_name,last_name,full_name,birth_year,gender',
                        lambda q: q.lte('birth_year', 1995))
    per_navn = {}
    for a in utovere:
        per_navn.setdefault(re.sub(r'\s+', ' ', (a['full_name'] or '').replace('.', '')).lower(), []).append(a)
    per_etternavn = {}
    for a in utovere:
        etter = (a['last_name'] or '').split()
        if etter:
            per_etternavn.setdefault(etter[-1].lower(), []).append(a)
    _utover = {a['id']: a for a in utovere}

    def utover_av(i):
        if i not in _utover:
            d = sb.table('athletes').select('id,first_name,last_name,full_name,birth_year,gender').eq('id', i).execute().data
            _utover[i] = d[0] if d else {'full_name': '', 'gender': None, 'birth_year': None}
        return _utover[i]

    def samme_person(r, athlete_id):
        """Treff hos en annen utøver-id er samme person bare ved samme kjønn og
        et felles navneledd (Aase/Åse Nyland). Ellers er det en tilfeldighet:
        en annen utøver med samme tid samme uke."""
        a = utover_av(athlete_id)
        if a['gender'] not in (r['kjonn'], None):
            return False
        hennes = set(re.sub(r'[^\wæøå -]', ' ', (a['full_name'] or '').lower()).replace('-', ' ').split())
        listens = set()
        for v in navnevarianter(r['navn']):
            listens |= set(v.replace('-', ' ').split())
        return len(hennes & listens) >= 1 and (not a['birth_year'] or abs(a['birth_year'] - r['aar_fodt']) <= 1)

    def finn_utover(r):
        varianter = navnevarianter(r['navn'])
        alias = ALIAS.get((r['navn'], r['aar_fodt']))
        if alias:
            varianter = [alias.lower()] + varianter
        kandidater = []
        for v in varianter:
            kandidater += per_navn.get(v, [])
        kjonn_ok = [a for a in kandidater if a['gender'] in (r['kjonn'], None)]
        samme_aar = [a for a in kjonn_ok if a['birth_year'] == r['aar_fodt']]
        if samme_aar:
            return samme_aar[0]['id'], 'alias' if alias else 'navn'
        # Helt likt navn, fødselsår ett år unna: trykkfeil i lista
        # (Rune Bråten Liholt står som 76 ute og 77 inne)
        naer = [a for a in kjonn_ok if a['birth_year'] and abs(a['birth_year'] - r['aar_fodt']) == 1]
        if len(naer) == 1:
            return naer[0]['id'], f"navn, fødselsår {naer[0]['birth_year']} i basen"
        # Fornavn + etternavn med mellomnavn som avviker («Martine Hjørnevik»)
        for v in varianter:
            d = v.split()
            for a in per_etternavn.get(d[-1], []):
                if a['birth_year'] == r['aar_fodt'] and a['gender'] in (r['kjonn'], None) \
                        and (a['first_name'] or '').lower().split()[:1] == d[:1]:
                    return a['id'], 'fornavn+etternavn'
        return None, None

    rapport = []
    for r in rekorder:
        r['navn'], _, r['klubb'] = r['nk'].partition(', ')
        r['navn'] = r['navn'].strip()
        r['koder'] = None
        ov = ovelse(r['overskrift'] or '', r['vind'] == '***')
        if ov == 'stafett':
            r['status'] = 'stafett (ikke lagt inn)'; rapport.append(r); continue
        koder = [k for k in (ov or []) if k in events]
        if not koder:
            r['status'] = 'øvelse uten kode i basen'; rapport.append(r); continue
        r['koder'] = koder
        dm = re.match(r'^(?:(\d{2})-)?(\d{2}\.\d{2}\.\d{4})$', r['dato'])
        if not dm:
            r['status'] = 'ufullstendig dato'; rapport.append(r); continue
        # «15-20.03.2006»: mesterskap over flere dager, dagen er ukjent
        d_slutt = datetime.strptime(dm.group(2), '%d.%m.%Y').date()
        d = d_slutt.replace(day=int(dm.group(1))) if dm.group(1) else d_slutt
        r['dato_iso'] = d.isoformat()
        r['aar_fodt'] = fodselsaar(r['fodt'], d.year)
        ev = events[koder[0]]
        perf = normaliser_tid(r['perf']) if ev['result_type'] == 'time' else r['perf'].replace(',', '.')
        if ev['result_type'] == 'time':
            perf = tid_tekst(perf)
        r['perf_ny'] = perf
        r['pv'] = verdi(perf, ev['result_type'])
        r['vind_tall'] = float(r['vind'].replace(',', '.')) if r['vind'] and re.match(r'^[+-]', r['vind']) else None

        ids = [events[k]['id'] for k in koder]
        treff = sb.table('results').select('id,athlete_id,date,performance,event_id') \
            .in_('event_id', ids).eq('performance_value', r['pv']) \
            .gte('date', (d - timedelta(days=3)).isoformat()).lte('date', (d_slutt + timedelta(days=3)).isoformat()) \
            .execute().data
        aid, hvordan = finn_utover(r)
        r['athlete_id'], r['koblet'] = aid, hvordan
        egne = [t for t in treff if t['athlete_id'] == aid] if aid else []
        if egne:
            r['status'] = 'finnes'
        elif treff and (lik := [t for t in treff if samme_person(r, t['athlete_id'])]):
            # Samme resultat samme uke under en annen navneform
            a = utover_av(lik[0]['athlete_id'])
            r['status'] = 'finnes (annen navneform i basen)'; r['merknad'] = f"{a['full_name']} ({a['birth_year']})"
        else:
            annen_dato = []
            if aid:
                annen_dato = sb.table('results').select('date').in_('event_id', ids) \
                    .eq('athlete_id', aid).eq('performance_value', r['pv']).execute().data
            if annen_dato:
                r['status'] = 'finnes med annen dato'; r['merknad'] = annen_dato[0]['date']
            elif (r['navn'], r['perf']) in AVVIK:
                r['status'] = 'avvik mot basen'; r['merknad'] = AVVIK[(r['navn'], r['perf'])]
            else:
                r['status'] = 'mangler' if aid else 'mangler (ny utøver)'
        rapport.append(r)

    # Rapport
    ut = HER / 'opprydding' / f'masters_rekorder_{TS}.csv'
    felt = ['fil', 'overskrift', 'klasse', 'hoved', 'perf', 'vind', 'navn', 'klubb', 'fodt', 'sted', 'dato',
            'status', 'merknad', 'koblet', 'koder', 'athlete_id', 'pv']
    with open(ut, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=felt, extrasaction='ignore', delimiter=';')
        w.writeheader()
        for r in rapport:
            w.writerow({**r, 'koder': ','.join(r['koder'] or [])})
    telling = {}
    for r in rapport:
        telling[r['status']] = telling.get(r['status'], 0) + 1
    log.info(f"{len(rapport)} rekorder. Rapport: {ut}")
    for s, n in sorted(telling.items(), key=lambda x: -x[1]):
        log.info(f"   {s}: {n}")

    nye = [r for r in rapport if r['status'] in ('mangler', 'mangler (ny utøver)')]
    if not args.apply:
        log.info(f"DRY-RUN. {len(nye)} rekorder ville blitt lagt inn. Kjør med --apply.")
        return

    kilde = sb.table('sources').select('id').eq('name', KILDE_NAVN).execute().data
    kilde_id = kilde[0]['id'] if kilde else sb.table('sources').insert({
        'name': KILDE_NAVN, 'source_type': 'other',
        'metadata': {'filer': list(FILER), 'ute_pr': '31.12.2025', 'inne_pr': '30.06.2026'}}).execute().data[0]['id']
    batch = sb.table('import_batches').insert({'name': f'Mastersrekorder fra rekordlistene {TS}',
                                               'source_type': 'other', 'status': 'processing'}).execute().data[0]['id']
    log.info(f"Kilde {kilde_id}, importbatch {batch}")

    stevner, nye_utovere, nye_stevner, lagt_inn = {}, 0, 0, 0
    for r in nye:
        klubb_id = klubber.get(r['klubb'].strip().lower())
        aid = r['athlete_id']
        if not aid:
            navn = navnevarianter(r['navn'])[0]
            orig = re.sub(r'\s+', ' ', re.sub(r'\([^)]*\)', ' ', r['navn'])).strip()
            deler = orig.split()
            if len(deler) < 2:
                log.warning(f"Hopper over (bare fornavn): {r['navn']}"); continue
            aid = sb.table('athletes').insert({
                'first_name': deler[0], 'last_name': ' '.join(deler[1:]), 'gender': r['kjonn'],
                'birth_year': r['aar_fodt'], 'nationality': 'NOR', 'current_club_id': klubb_id,
            }).execute().data[0]['id']
            nye_utovere += 1
            # Samme nye utøver kan ha flere rekorder
            for r2 in nye:
                if r2 is not r and not r2['athlete_id'] and r2['navn'] == r['navn'] and r2['aar_fodt'] == r['aar_fodt']:
                    r2['athlete_id'] = aid
            r['athlete_id'] = aid

        sted = (r['sted'] or 'Ukjent').strip()
        by, _, land = sted.partition(', ')
        land = land.strip().upper() if re.match(r'^[A-Z]{2,3}$', land.strip()) else 'NOR'
        land = {'SPA': 'ESP', 'PR': 'PUR'}.get(land, land)
        nokkel = (by, r['dato_iso'], r['inne'])
        meet_id = stevner.get(nokkel)
        if not meet_id:
            d = date.fromisoformat(r['dato_iso'])
            m = sb.table('meets').select('id').ilike('city', by).eq('indoor', r['inne']) \
                .gte('start_date', (d - timedelta(days=2)).isoformat()) \
                .lte('start_date', (d + timedelta(days=1)).isoformat()).limit(1).execute().data
            if m:
                meet_id = m[0]['id']
            else:
                sesong_aar = d.year + 1 if r['inne'] and d.month >= 10 else d.year
                meet_id = sb.table('meets').insert({
                    'name': by, 'city': by, 'country': land, 'start_date': r['dato_iso'], 'indoor': r['inne'],
                    'season_id': sesonger.get((sesong_aar, r['inne'])),
                    'notes': 'Opprettet fra de offisielle mastersrekordlistene',
                }).execute().data[0]['id']
                nye_stevner += 1
            stevner[nokkel] = meet_id

        ev = events[r['koder'][0]]
        d = date.fromisoformat(r['dato_iso'])
        sesong_aar = d.year + 1 if r['inne'] and d.month >= 10 else d.year
        desimaler = len(r['perf_ny'].split('.')[-1]) if '.' in r['perf_ny'] else 0
        manuell = (ev['category'] in ('sprint', 'hurdles') and desimaler == 1
                   and re.match(r'^(\d+)m', r['koder'][0]) and int(re.match(r'^(\d+)m', r['koder'][0]).group(1)) < 800)
        sb.table('results').insert({
            'athlete_id': r['athlete_id'], 'event_id': ev['id'], 'meet_id': meet_id,
            'season_id': sesonger.get((sesong_aar, r['inne'])), 'performance': r['perf_ny'],
            'date': r['dato_iso'], 'wind': r['vind_tall'], 'status': 'OK', 'club_id': klubb_id,
            'source_id': kilde_id, 'import_batch_id': batch, 'is_manual_time': bool(manuell),
        }).execute()
        lagt_inn += 1
    sb.table('import_batches').update({'row_count': lagt_inn, 'status': 'imported',
                                       'imported_at': datetime.now().isoformat()}).eq('id', batch).execute()
    log.info(f"Ferdig: {lagt_inn} rekorder lagt inn, {nye_utovere} nye utøvere, {nye_stevner} nye stevner. "
             f"Importbatch {batch}.")
    log.info("Husk: refresh materialized view masters_resultater.")


if __name__ == '__main__':
    main()
