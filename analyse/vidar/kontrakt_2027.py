#!/usr/bin/env python3
"""Sportsklubben Vidar: utøverne mot forslaget til kontraktskriterier 2027.

Leser «Forslag Kontraktskriterie 2027.xlsx», henter alle 2026-resultater for
utøvere som har representert Vidar i 2026, og plasserer hver utøver på det
høyeste nivået de har et resultat for. Lager HTML, CSV og PDF.

    ../../scraper/venv/bin/python kontrakt_2027.py

NIVÅER (beløp fra rad 1 i regnearket)
  OL/VM     180 000  resultat på OL 24- ELLER VM 25-kravet
  EM        140 000  EM 26-kravet
  Elite A    80 000  «Elite A SKV» (EM-poeng minus 80, minus 50 for *-øvelser)
  U23 EM     60 000  «U23 EM 27», bare for født 2005–2007
  U20 EM     60 000  «U20 EM 27», bare for født 2008 eller senere
  Elite B    40 000  «Elite B SKV» (Elite A minus 50 poeng)
  U18 EM     40 000  «U18EM 26», bare for født 2010 eller senere
Aldersgrensene regnes etter kalenderåret 2027, som kontraktene gjelder for.

REGLER FOR RESULTATENE
  Bare 2026. Status OK. Lovlig vind i vindavhengige øvelser utendørs; ukjent
  vind teller ikke. Ikke håndtid i sprint og hekk. Innendørsresultater teller
  og er merket (i). 5 km og 10 km landevei teller som 5000 og 10 000 m, som i
  forslaget. Ungdomsnivåene bruker ungdommens redskap og hekkehøyder.
"""

import csv
import os
import re
import sys
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

import openpyxl
from dotenv import load_dotenv
from supabase import create_client

MAPPE = Path(__file__).resolve().parent
sys.path.insert(0, str(MAPPE.parent))
from klubbrapport import navn as navnemodul  # noqa: E402
from klubbrapport.pdf import lag_pdf  # noqa: E402
import stipend as stipendmodul  # noqa: E402

VIDAR = 'fcfc0ff6-787b-4471-acb6-5705fd7b48d8'
AAR = 2026
KONTRAKTSAAR = 2027

# ------------------------------------------------------------------ nivåer

NIVAAER = [
    # navn, beløp, kolonner i regnearket (0-basert), aldersvilkår, redskap
    ('OL/VM', 180_000, (1, 2), None, 'senior'),
    ('EM', 140_000, (4,), None, 'senior'),
    ('Elite A', 80_000, (7,), None, 'senior'),
    ('U23 EM', 60_000, (14,), lambda f: 2005 <= f <= 2007, 'senior'),
    ('U20 EM', 60_000, (15,), lambda f: f >= 2008, 'u20'),
    ('Elite B', 40_000, (10,), None, 'senior'),
    ('U18 EM', 40_000, (16,), lambda f: f >= 2010, 'u18'),
]
RANG = {n[0]: i for i, n in enumerate(NIVAAER)}

# ------------------------------------------------------------------ øvelser

# Radnavn i regnearket -> øvelseskoder i basen, per kjønn og redskapsnivå.
# «senior» brukes også for U23. Generiske koder (kule, 110mh …) kommer fra
# utenlandske resultater og regnes som seniorredskap.
TIKAMP = ['10_k', '10_k_100m-lengde-kule-høyde-400m-110mh-diskos-stav',
          '10_k_110m_h-diskos-stav-spyd-400m-100m-lengde-kule']
SJUKAMP = ['7_k', '7_k_100mh-høyde-kule-200m-lengde-spyd-800m',
           '7_k_høyde-100mh-kule-100m-lengde-spyd-800m']

OVELSER = {
    'M': {
        '100 m': {'alle': ['100m']},
        '200 m': {'alle': ['200m']},
        '400 m': {'alle': ['400m']},
        '800 m': {'alle': ['800m']},
        '1500 m': {'alle': ['1500m']},
        '3000m': {'alle': ['3000m']},
        '5000 m/5 km': {'alle': ['5000m', '5km']},
        '10000 m/10 km*': {'alle': ['10000m', '10km']},
        '3000 m hinder': {'senior': ['3000mhinder_91_4cm', '3000mhinder'],
                          'u20': ['3000mhinder_91_4cm'],
                          'u18': ['2000mhinder_91_4cm', '2000mhinder']},
        '110 m hekk': {'senior': ['110mh_106_7cm', '110mh'], 'u20': ['110mh_100cm'],
                       'u18': ['110mh_91_4cm']},
        '400 m hekk': {'senior': ['400mh_91_4cm', '400mh'], 'u20': ['400mh_91_4cm'],
                       'u18': ['400mh_84cm']},
        'Halvmaraton*': {'alle': ['halvmaraton']},
        'Maraton*': {'alle': ['maraton']},
        '5000m RW': {'alle': ['kappgang_5000_m']},
        '10000m RW': {'alle': ['kappgang_10000_m', 'kappgang_10_km']},
        'Høyde': {'alle': ['hoyde']},
        'Stav': {'alle': ['stav']},
        'Lengde': {'alle': ['lengde']},
        'Tresteg': {'alle': ['tresteg']},
        'Kule': {'senior': ['kule_7_26kg', 'kule'], 'u20': ['kule_6kg'], 'u18': ['kule_5kg']},
        'Diskos': {'senior': ['diskos_2kg', 'diskos'], 'u20': ['diskos_1_75kg'],
                   'u18': ['diskos_1_5kg']},
        'Slegge': {'senior': ['slegge_7_26kg', 'slegge_726kg/1215cm', 'slegge'],
                   'u20': ['slegge_6kg', 'slegge_60kg/1215cm', 'slegge_60kg/110cm'],
                   'u18': ['slegge_5kg', 'slegge_50kg/120cm']},
        'Spyd': {'senior': ['spyd_800g', 'spyd'], 'u20': ['spyd_800g'],
                 'u18': ['spyd_700g', 'spyd_700_gram_2025']},
        '10-kamp': {'senior': TIKAMP,
                    'u20': TIKAMP + ['10_k_100m_h-diskos-stav-spyd-300m-100m-lengde-kule'],
                    'u18': TIKAMP + ['10_k_100m-lengde-kule-høyde-400m-80mh-diskos-stav-']},
    },
    'F': {
        '100 m': {'alle': ['100m']},
        '200 m': {'alle': ['200m']},
        '400 m': {'alle': ['400m']},
        '800 m': {'alle': ['800m']},
        '1500 m': {'alle': ['1500m']},
        '3000m': {'alle': ['3000m']},
        '5000 m/5 km': {'alle': ['5000m', '5km']},
        '10000 m/10 km*': {'alle': ['10000m', '10km']},
        '3000 m hinder': {'senior': ['3000mhinder_76_2cm', '3000mhinder'],
                          'u20': ['3000mhinder_76_2cm'],
                          'u18': ['2000mhinder_76_2cm', '2000mhinder']},
        '100 m hekk': {'senior': ['100mh_84cm', '100mh'], 'u20': ['100mh_84cm'],
                       'u18': ['100mh_76_2cm']},
        '400 m hekk': {'alle': ['400mh_76_2cm', '400mh']},
        'Halvmaraton*': {'alle': ['halvmaraton']},
        'Maraton*': {'alle': ['maraton']},
        '5000m RW': {'alle': ['kappgang_5000_m']},
        '10000m RW': {'alle': ['kappgang_10000_m', 'kappgang_10_km']},
        'Høyde': {'alle': ['hoyde']},
        'Stav': {'alle': ['stav']},
        'Lengde': {'alle': ['lengde']},
        'Tresteg': {'alle': ['tresteg']},
        'Kule': {'senior': ['kule_4kg', 'kule'], 'u20': ['kule_4kg'], 'u18': ['kule_3kg']},
        'Diskos': {'alle': ['diskos_1kg', 'diskos']},
        'Slegge': {'senior': ['slegge_4kg', 'slegge_40kg/1195cm', 'slegge'],
                   'u20': ['slegge_4kg', 'slegge_40kg/1195cm'],
                   'u18': ['slegge_3kg', 'slegge_30kg_1195cm']},
        'Spyd': {'senior': ['spyd_600g', 'spyd'], 'u20': ['spyd_600g'], 'u18': ['spyd_500g']},
        '7-kamp': {'senior': SJUKAMP,
                   'u20': SJUKAMP + ['7_k_100mh-høyde-kule-200m-lengde-spyd-800m_ungdom'],
                   'u18': SJUKAMP + ['7_k_80mh-høyde-kule-200m-lengde-spyd-800m_ungdom']},
    },
}

SPRINT_HEKK = re.compile(r'^(100m|200m|400m|100mh|110mh|400mh)')
VINDAVHENGIG = re.compile(r'^(100m|200m|100mh|110mh|lengde|tresteg)$|^(100mh|110mh)_')


def koder(kjonn, ovelse, redskap):
    m = OVELSER[kjonn].get(ovelse.strip())
    if not m:
        return []
    return m.get('alle') or m.get(redskap) or []


# ------------------------------------------------------------------ krav

TID_TIMER = {'Halvmaraton*', 'Maraton*'}
TID_SEKUNDER = {'100 m', '200 m', '400 m', '110 m hekk', '100 m hekk', '400 m hekk'}
FELT = {'Høyde', 'Stav', 'Lengde', 'Tresteg', 'Kule', 'Diskos', 'Slegge', 'Spyd'}
POENG = {'10-kamp', '7-kamp'}


def les_krav(verdi, ovelse):
    """Kravet i basens enheter: hundredeler for tid, millimeter for felt,
    poeng for mangekamp. None hvis cellen er tom eller ikke er et krav."""
    if verdi is None or str(verdi).strip() == '':
        return None
    ovelse = ovelse.strip()
    s = str(verdi).strip().replace(' ', '')
    s = re.sub(r'\(.*\)', '', s).replace(',', '.')
    if ovelse in POENG:
        return int(round(float(s)))
    if ovelse in FELT:
        # «2:33» i høyde (VM 25) er en skrivefeil for 2,33
        return int(round(float(s.replace(':', '.')) * 1000))
    deler = [d for d in re.split(r'[.:]', s) if d != '']
    if ovelse in TID_TIMER:                               # h:mm:ss
        t, m, sek = (int(d) for d in (deler + ['0', '0'])[:3])
        return (t * 3600 + m * 60 + sek) * 100
    if isinstance(verdi, (int, float)) and ovelse in TID_SEKUNDER:
        return int(round(float(verdi) * 100))
    if len(deler) == 1:
        return int(round(float(deler[0]) * 100))
    if len(deler) == 2:
        if ovelse in TID_SEKUNDER:                        # 10.00
            return int(round(float(f'{deler[0]}.{deler[1]}') * 100))
        return (int(deler[0]) * 60 + int(deler[1])) * 100  # 13:01
    m, sek, brok = deler[:3]                              # 1.44,70 og 4.03.5
    brok = int(brok) * (10 if len(brok) == 1 else 1)
    return (int(m) * 60 + int(sek)) * 100 + brok


def les_regneark():
    """{kjønn: {øvelse: {nivå: krav}}} fra regnearket."""
    wb = openpyxl.load_workbook(MAPPE / 'Forslag Kontraktskriterie 2027.xlsx')
    ws = wb.worksheets[0]
    krav = {'M': {}, 'F': {}}
    kjonn = None
    for rad in ws.iter_rows(values_only=True):
        forste = (rad[0] or '')
        if isinstance(forste, str) and forste.strip() in ('Menn', 'Kvinner'):
            kjonn = 'M' if forste.strip() == 'Menn' else 'F'
            continue
        if not kjonn or not isinstance(forste, str) or not forste.strip() or forste.strip() == 'AVG':
            continue
        ovelse = forste.strip()
        for navn, _, kolonner, _, _ in NIVAAER:
            verdier = [les_krav(rad[k], ovelse) for k in kolonner]
            verdier = [v for v in verdier if v is not None]
            if not verdier:
                continue
            lavere_best = not (ovelse in FELT or ovelse in POENG)
            # OL/VM: begge krav teller, det letteste avgjør
            krav[kjonn].setdefault(ovelse, {})[navn] = max(verdier) if lavere_best else min(verdier)
    return krav


def vis_krav(v, ovelse):
    ovelse = ovelse.strip()
    if ovelse in POENG:
        return str(v)
    if ovelse in FELT:
        return f'{v / 1000:.2f}'.replace('.', ',')
    sek = v / 100
    if ovelse in TID_TIMER:
        t, rest = divmod(int(round(sek)), 3600)
        return f'{t}:{rest // 60:02d}:{rest % 60:02d}'
    if sek >= 60:
        m, s = divmod(sek, 60)
        return f'{int(m)}:{s:05.2f}'.replace('.', ',')
    return f'{sek:.2f}'.replace('.', ',')


# ------------------------------------------------------------------ data

def klient():
    load_dotenv(MAPPE.parents[1] / 'scraper' / '.env')
    return create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])


def hent_alle(sporring):
    rader, fra = [], 0
    while True:
        d = sporring().range(fra, fra + 999).execute().data
        rader.extend(d)
        if len(d) < 1000:
            return rader
        fra += 1000


def hent():
    sb = klient()
    vidar = hent_alle(lambda: sb.table('results').select('athlete_id')
                      .eq('club_id', VIDAR).gte('date', f'{AAR}-01-01').lte('date', f'{AAR}-12-31')
                      .order('id'))
    ids = sorted({r['athlete_id'] for r in vidar if r['athlete_id']})
    utovere, resultater = {}, []
    for i in range(0, len(ids), 150):
        bit = ids[i:i + 150]
        for a in sb.table('athletes').select('id,full_name,birth_year,gender').in_('id', bit).execute().data:
            utovere[a['id']] = a
        resultater += hent_alle(lambda: sb.table('results').select(
            'id,athlete_id,performance,performance_value,wind,is_wind_legal,is_manual_time,date,status,club_id,'
            'events(code,name),meets(name,indoor)')
            .in_('athlete_id', bit).gte('date', f'{AAR}-01-01').lte('date', f'{AAR}-12-31')
            .eq('status', 'OK').gt('performance_value', 0).order('id'))
    return utovere, resultater


def gyldig(r):
    kode = r['events']['code']
    inne = bool(r['meets'] and r['meets'].get('indoor'))
    if SPRINT_HEKK.match(kode) and r.get('is_manual_time') is True:
        return False
    if not inne and VINDAVHENGIG.search(kode) and r.get('is_wind_legal') is not True:
        return False
    return True


# ------------------------------------------------------------------ vurdering

def vurder(utover, resultater, krav):
    """Alle nivåer utøveren når, og nærmeste nivå over det høyeste."""
    kjonn = utover.get('gender')
    fodt = utover.get('birth_year') or 0
    per_kode = defaultdict(list)
    for r in resultater:
        if gyldig(r):
            per_kode[r['events']['code']].append(r)

    naadd, naermest = [], {}
    for ovelse, per_nivaa in krav.get(kjonn, {}).items():
        lavere_best = not (ovelse in FELT or ovelse in POENG)
        for navn, belop, _, alder, redskap in NIVAAER:
            if navn not in per_nivaa or (alder and not (fodt and alder(fodt))):
                continue
            kandidater = [r for k in koder(kjonn, ovelse, redskap) for r in per_kode.get(k, [])]
            if not kandidater:
                continue
            beste = (min if lavere_best else max)(kandidater, key=lambda r: r['performance_value'])
            k = per_nivaa[navn]
            v = beste['performance_value']
            avvik = (v - k) / k if lavere_best else (k - v) / k    # <= 0 betyr klart
            post = {'nivaa': navn, 'belop': belop, 'ovelse': ovelse, 'krav': k,
                    'resultat': beste, 'avvik': avvik}
            if avvik <= 0:
                naadd.append(post)
            elif navn not in naermest or avvik < naermest[navn]['avvik']:
                naermest[navn] = post
    naadd.sort(key=lambda p: (RANG[p['nivaa']], p['avvik']))
    topp = naadd[0] if naadd else None
    # Nærmeste nivå som betaler mer enn det utøveren har
    neste = None
    grense = topp['belop'] if topp else 0
    for navn, belop, *_ in NIVAAER:
        if belop > grense and navn in naermest:
            if neste is None or naermest[navn]['avvik'] < neste['avvik']:
                neste = naermest[navn]
    return topp, naadd, neste


# ------------------------------------------------------------------ rapport

def kr(n):
    return f'{n:,}'.replace(',', ' ')


def vis_resultat(r):
    inne = ' (i)' if r['meets'] and r['meets'].get('indoor') else ''
    vind = f" ({'+' if r['wind'] > 0 else ''}{r['wind']})" if r.get('wind') is not None and not inne else ''
    return f"{r['performance']}{vind}{inne}"


def main():
    krav = les_regneark()
    utovere, resultater = hent()
    per_utover = defaultdict(list)
    for r in resultater:
        per_utover[r['athlete_id']].append(r)

    rader = []
    for aid, u in utovere.items():
        if not u.get('gender'):
            continue
        topp, naadd, neste = vurder(u, per_utover.get(aid, []), krav)
        treff = navnemodul.finn(u['full_name'], stipendmodul.FLAT)
        rader.append({'u': u, 'topp': topp, 'naadd': naadd, 'neste': neste,
                      'stipend': treff[1] if treff else None})

    med = [r for r in rader if r['topp']]
    med.sort(key=lambda r: (RANG[r['topp']['nivaa']], r['topp']['avvik'], r['u']['full_name']))
    naer = [r for r in rader if not r['topp'] and r['neste'] and r['neste']['avvik'] <= 0.03]
    naer.sort(key=lambda r: r['neste']['avvik'])
    uten_stipend_2027 = [r for r in rader if r['stipend'] and not r['topp']]
    uten_stipend_2027.sort(key=lambda r: r['u']['full_name'])

    lag_csv(med, naer)
    lag_html(med, naer, uten_stipend_2027, krav, len(rader))
    lag_pdf(MAPPE / 'kontrakt_2027.html', MAPPE / 'kontrakt_2027.pdf')
    print(f'{len(rader)} utøvere, {len(med)} på et nivå, {len(naer)} innen 3 %')


def lag_csv(med, naer):
    with open(MAPPE / 'kontrakt_2027.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['Utøver', 'Født', 'Kjønn', 'Nivå 2027', 'Beløp 2027', 'Øvelse', 'Resultat 2026',
                    'Dato', 'Stevne', 'Krav', 'Andre nivåer nådd', 'Stipend 2026', 'Kategori 2026',
                    'Nærmeste høyere nivå', 'Mangler'])
        for r in med + naer:
            u, t, n, s = r['u'], r['topp'], r['neste'], r['stipend']
            andre = sorted({p['nivaa'] for p in r['naadd']} - ({t['nivaa']} if t else set()), key=RANG.get)
            w.writerow([
                u['full_name'], u.get('birth_year') or '', u['gender'],
                t['nivaa'] if t else '', t['belop'] if t else 0,
                t['ovelse'] if t else '', vis_resultat(t['resultat']) if t else '',
                t['resultat']['date'] if t else '', (t['resultat']['meets'] or {}).get('name', '') if t else '',
                vis_krav(t['krav'], t['ovelse']) if t else '',
                ', '.join(andre), s['belop'] if s else '', s['kategori'] if s else '',
                f"{n['nivaa']} ({n['ovelse'].strip()} {vis_krav(n['krav'], n['ovelse'])})" if n else '',
                f"{n['avvik'] * 100:.1f} %" if n else '',
            ])


STIL = """
:root{--bg:#fbfbfa;--fg:#1a1a19;--mut:#6b6b68;--line:#e4e4e1;--card:#fff;--acc:#192E5D;--ok:#0f6b52;--warn:#a8571c;--neg:#b42318}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#151514;--fg:#eeeeec;--mut:#9a9a96;--line:#2c2c2a;--card:#1d1d1b;--acc:#8fb0ea;--ok:#63c6ab;--warn:#e0925a;--neg:#f08b80}}
*{box-sizing:border-box}
body{margin:0;padding:2rem 1.25rem 4rem;background:var(--bg);color:var(--fg);font:14.5px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto}
h1{font-size:1.6rem;margin:0 0 .25rem;letter-spacing:-.02em}
h2{font-size:1.15rem;margin:2rem 0 .6rem}
.sub{color:var(--mut);margin:0 0 1.5rem}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.25rem}
table{width:100%;border-collapse:collapse}
th{font-size:.74rem;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);font-weight:600;text-align:left;padding:.35rem .5rem;border-bottom:1px solid var(--line)}
td{padding:.4rem .5rem;border-bottom:1px solid var(--line);vertical-align:top;font-variant-numeric:tabular-nums}
td.tall,th.tall{text-align:right;white-space:nowrap}
.niv{display:inline-block;font-size:.75rem;font-weight:700;padding:.1rem .5rem;border-radius:999px;background:color-mix(in srgb,var(--acc) 14%,transparent);color:var(--acc);white-space:nowrap}
.mut{color:var(--mut);font-size:.85rem}
.opp{color:var(--ok);font-weight:600}.ned{color:var(--neg);font-weight:600}.lik{color:var(--mut)}
.merk{color:var(--mut);font-size:.83rem;margin:.4rem 0 0}
ul.regler{margin:.3rem 0 0;padding-left:1.1rem}ul.regler li{margin:.15rem 0}
@media (max-width:760px){.skjul{display:none}}
@page{size:A4 landscape;margin:11mm}
@media print{body{padding:0;font-family:Helvetica,Arial,sans-serif;font-size:10.5px}.skjul{display:table-cell!important}h2{break-after:avoid}tr{break-inside:avoid}}
"""


def lag_html(med, naer, mistet, krav, antall):
    per_nivaa = defaultdict(list)
    for r in med:
        per_nivaa[r['topp']['nivaa']].append(r)
    sum_2027 = sum(r['topp']['belop'] for r in med)
    sum_2026 = sum(s['belop'] for s in stipendmodul.FLAT.values())

    def rad(r, vis_nivaa=True):
        u, t, n, s = r['u'], r['topp'], r['neste'], r['stipend']
        vis = t or n                      # uten nivå: vis beste mot nærmeste nivå
        res = vis['resultat'] if vis else None
        andre = sorted({p['nivaa'] for p in r['naadd']} - ({t['nivaa']} if t else set()), key=RANG.get)
        if s and t:
            diff = t['belop'] - s['belop']
            endr = (f'<span class="opp">+{kr(diff)}</span>' if diff > 0 else
                    f'<span class="ned">−{kr(-diff)}</span>' if diff < 0 else '<span class="lik">0</span>')
        elif t:
            endr = '<span class="opp">ny</span>'
        else:
            endr = ''
        naermere = (f"{escape(n['nivaa'])}: {escape(n['ovelse'].strip())} {vis_krav(n['krav'], n['ovelse'])}"
                    f" <span class='mut'>(mangler {n['avvik'] * 100:.1f} %)</span>") if n else '–'
        return (
            '<tr>'
            f"<td><b>{escape(u['full_name'])}</b><div class='mut'>{u.get('birth_year') or '–'} · {'K' if u['gender'] == 'F' else 'M'}</div></td>"
            + (f"<td><span class='niv'>{escape(t['nivaa'])}</span>"
               + (f"<div class='mut'>også {', '.join(andre)}</div>" if andre else '') + '</td>'
               if vis_nivaa else '')
            + (f"<td>{escape(vis['ovelse'].strip())}</td>"
               f"<td><b>{escape(vis_resultat(res))}</b><div class='mut'>krav {vis_krav(vis['krav'], vis['ovelse'])}"
               + ('' if t else f" ({escape(vis['nivaa'])})") + "</div></td>"
               f"<td class='skjul'>{escape((res['meets'] or {}).get('name', ''))}<div class='mut'>{res['date']}</div></td>"
               if vis else '<td>–</td><td>–</td><td class="skjul">–</td>')
            + f"<td class='tall'>{kr(t['belop']) if t else '–'}</td>"
            + f"<td class='tall'>{kr(s['belop']) + '<div class=mut>' + escape(s['kategori']) + '</div>' if s else '–'}</td>"
            + f"<td class='tall'>{endr}</td>"
            + f"<td class='skjul'>{naermere}</td>"
            '</tr>'
        )

    hode = ('<tr><th>Utøver</th><th>Nivå 2027</th><th>Øvelse</th><th>Beste 2026</th>'
            '<th class="skjul">Stevne</th><th class="tall">2027</th><th class="tall">Stipend 2026</th>'
            '<th class="tall">Endring</th><th class="skjul">Nærmeste høyere nivå</th></tr>')

    oversikt = ''.join(
        f"<tr><td><span class='niv'>{escape(navn)}</span></td><td class='tall'>{kr(belop)}</td>"
        f"<td class='tall'>{len(per_nivaa[navn])}</td><td class='tall'>{kr(belop * len(per_nivaa[navn]))}</td></tr>"
        for navn, belop, *_ in NIVAAER)

    deler = [f"""<!doctype html><html lang="nb"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vidar kontrakter 2027</title><style>{STIL}</style></head><body><div class="wrap">
<h1>Sportsklubben Vidar · kontraktskriterier 2027</h1>
<p class="sub">Forslaget til kontraktskriterier 2027 holdt opp mot utøvernes beste resultater i {AAR}.
{antall} utøvere har representert Vidar i {AAR}. Uttrekk {date.today().strftime('%d.%m.%Y')}.</p>

<div class="panel"><table>
<thead><tr><th>Nivå</th><th class="tall">Beløp</th><th class="tall">Utøvere</th><th class="tall">Sum</th></tr></thead>
<tbody>{oversikt}
<tr><td><b>Totalt forslag 2027</b></td><td></td><td class="tall"><b>{len(med)}</b></td><td class="tall"><b>{kr(sum_2027)}</b></td></tr>
<tr><td class="mut">Budsjett 2026, utøverstipend (inkl. fjelløp og OCR)</td><td></td><td class="tall mut">{len(stipendmodul.FLAT)}</td><td class="tall mut">{kr(sum_2026)}</td></tr>
</tbody></table>
<p class="merk">Hver utøver står på det høyeste nivået de har klart i minst én øvelse. Nivåene er rangert etter beløp.</p></div>
"""]

    deler.append(f"<h2>Utøvere som når et nivå ({len(med)})</h2><div class='panel'><table><thead>{hode}</thead><tbody>"
                 + ''.join(rad(r) for r in med) + '</tbody></table></div>')

    if naer:
        hode2 = hode.replace('<th>Nivå 2027</th>', '')
        deler.append(f"<h2>Nær et nivå, innen 3 % ({len(naer)})</h2><div class='panel'><table><thead>{hode2}</thead><tbody>"
                     + ''.join(rad(r, vis_nivaa=False) for r in naer) + '</tbody></table></div>')

    if mistet:
        deler.append(f"<h2>Har stipend 2026, når ikke et nivå med 2026-resultater ({len(mistet)})</h2>"
                     "<div class='panel'><table><thead><tr><th>Utøver</th><th class='tall'>Stipend 2026</th>"
                     "<th>Nærmeste nivå</th></tr></thead><tbody>"
                     + ''.join(
                         f"<tr><td><b>{escape(r['u']['full_name'])}</b><div class='mut'>{r['u'].get('birth_year') or '–'}</div></td>"
                         f"<td class='tall'>{kr(r['stipend']['belop'])}<div class='mut'>{escape(r['stipend']['kategori'])}</div></td>"
                         f"<td>{(escape(r['neste']['nivaa']) + ': ' + escape(r['neste']['ovelse'].strip()) + ' ' + vis_krav(r['neste']['krav'], r['neste']['ovelse']) + ' <span class=mut>(mangler ' + format(r['neste']['avvik'] * 100, '.1f') + ' %)</span>') if r['neste'] else '<span class=mut>ingen resultater i kriterieøvelsene i 2026</span>'}</td></tr>"
                         for r in mistet)
                     + '</tbody></table>'
                     '<p class="merk">Fjelløp og OCR har ingen kriterier i forslaget og står her av den grunn.</p></div>')

    deler.append("""<h2>Slik er det regnet</h2><div class="panel"><ul class="regler">
<li><b>Nivåer og beløp</b> er tatt rett fra regnearket. OL/VM: resultat på OL 24- eller VM 25-kravet. Elite A og B er kravene i kolonnene «Elite A SKV» og «Elite B SKV».</li>
<li><b>Ungdomsnivåene</b> gjelder etter alder i 2027: U23 for født 2005–2007, U20 for født 2008 eller senere, U18 for født 2010 eller senere. Seniornivåene gjelder alle.</li>
<li><b>Ungdomsnivåene bruker ungdommens redskap og hekkehøyder</b>: U20 menn kule 6 kg, diskos 1,75, slegge 6 kg, 110 m hekk 100 cm; U18 menn kule 5 kg, diskos 1,5, slegge 5 kg, spyd 700 g, 110 m hekk 91,4, 400 m hekk 84, 2000 m hinder; U18 kvinner kule 3 kg, slegge 3 kg, spyd 500 g, 100 m hekk 76,2, 2000 m hinder.</li>
<li><b>Bare resultater fra 2026</b>, alle klubber utøveren stilte for i 2026. Lovlig vind i vindavhengige øvelser utendørs; resultater med ukjent vind teller ikke. Ikke håndtid i sprint og hekk. Innendørsresultater teller og er merket (i).</li>
<li><b>5 km og 10 km landevei</b> teller mot 5000 m og 10 000 m, som forslaget sier.</li>
<li><b>Ikke brukt:</b> kolonnen «Plass Europa max3» og kolonnen uten overskrift ved EM 26. Hva de betyr for tildelingen, må klubben avgjøre.</li>
<li><b>Stipend 2026</b> er fra «SKV budsjett 2026 – v1», koblet på navn.</li>
</ul></div></div></body></html>""")
    (MAPPE / 'kontrakt_2027.html').write_text(''.join(deler), encoding='utf-8')


if __name__ == '__main__':
    main()
