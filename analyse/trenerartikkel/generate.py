#!/usr/bin/env python3
"""Genererer tabeller og figurer til trenerforening-artikkelen om nivå- og
breddeutvikling i norsk friidrett 2013-2025.

Datagrunnlag: friidrett.live-databasen (Supabase). All aggregering skjer
server-side via SQL-funksjonene analyse_active_athletes, analyse_event_trend
og analyse_survival (migrasjon add_trend_analysis_functions, juli 2026).

Kjøres med scraper-venv:
    ../../scraper/venv/bin/python generate.py

Output: ./output/ (CSV-er, PNG-figurer og nokkeltall.md)
"""

import csv
import logging
import os
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from supabase import create_client

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
load_dotenv(REPO_ROOT / 'scraper' / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

OUT = SCRIPT_DIR / 'output'
OUT.mkdir(exist_ok=True)

FROM_YEAR, TO_YEAR = 2013, 2025
GENDER_LABEL = {'M': 'Menn/gutter', 'F': 'Kvinner/jenter'}

# Øvelse: (kode, tittel, min_v, max_v, higher_better, enhet)
# Tider i hundredeler, hopp i millimeter. Kast er utelatt (redskapsvekter
# varierer med alder/kjønn og gjør sammenligning på tvers av år upresis).
EVENTS = [
    ('100m',   '100 meter',   950,   2500,   False, 's'),
    ('800m',   '800 meter',   10000, 30000,  False, 'min'),
    ('3000m',  '3000 meter',  44000, 120000, False, 'min'),
    ('lengde', 'Lengde',      2000,  8500,   True,  'm'),
    ('hoyde',  'Høyde',       800,   2400,   True,  'm'),
]


def fmt_value(v, unit):
    """Formater performance_value for visning."""
    if v is None:
        return ''
    v = float(v)
    if unit == 's':
        return f"{v / 100:.2f}"
    if unit == 'min':
        s = v / 100
        return f"{int(s // 60)}:{s % 60:05.2f}"
    return f"{v / 1000:.2f}"


def to_plot_value(v, unit):
    """Konverter til plottbar enhet (sekunder eller meter)."""
    if v is None:
        return None
    return float(v) / (100 if unit in ('s', 'min') else 1000)


def rpc(fn, params):
    return supabase.rpc(fn, params).execute().data


def write_csv(name, rows, fieldnames):
    path = OUT / name
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    logger.info(f"Skrev {path} ({len(rows)} rader)")


def savefig(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Skrev {path}")


# ------------------------------------------------------------
# 1. Bredde: aktive utøvere per år / aldersbånd / kjønn
# ------------------------------------------------------------

def analyse_bredde():
    logger.info("1/4 Bredde ...")
    rows = rpc('analyse_active_athletes', {'from_year': FROM_YEAR, 'to_year': TO_YEAR})
    write_csv('bredde_aktive.csv', rows, ['yr', 'gender', 'age_band', 'n_athletes'])

    bands = ['10-12', '13-14', '15-19', '20-34', '35+']
    by_band = defaultdict(lambda: defaultdict(int))   # band -> yr -> n
    by_gender_youth = defaultdict(lambda: defaultdict(int))  # gender -> yr -> n (10-19 år)
    for r in rows:
        by_band[r['age_band']][r['yr']] += r['n_athletes']
        if r['age_band'] in ('10-12', '13-14', '15-19') and r['gender'] in ('M', 'F'):
            by_gender_youth[r['gender']][r['yr']] += r['n_athletes']

    years = list(range(FROM_YEAR, TO_YEAR + 1))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for band in bands:
        ax.plot(years, [by_band[band].get(y, 0) for y in years], marker='o', label=f'{band} år')
    ax.set_title('Aktive utøvere per år og aldersgruppe (minst ett resultat)')
    ax.set_ylabel('Antall utøvere')
    ax.grid(alpha=0.3)
    ax.legend()
    savefig(fig, 'fig1_bredde_aldersgrupper.png')

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for g in ('F', 'M'):
        ax.plot(years, [by_gender_youth[g].get(y, 0) for y in years], marker='o', label=GENDER_LABEL[g])
    ax.set_title('Aktive utøvere 10-19 år per kjønn')
    ax.set_ylabel('Antall utøvere')
    ax.grid(alpha=0.3)
    ax.legend()
    savefig(fig, 'fig2_bredde_kjonn_ungdom.png')
    return by_band


# ------------------------------------------------------------
# 2. Toppnivå: topp-10-snitt og nr. 25 per øvelse (alle aldre, utendørs)
# ------------------------------------------------------------

def analyse_topp(age_lo=0, age_hi=200, suffix='senior', title_suffix='alle aldre'):
    logger.info(f"2/4 Toppnivå ({suffix}) ...")
    all_rows = []
    per_event = {}
    for code, title, min_v, max_v, higher, unit in EVENTS:
        rows = rpc('analyse_event_trend', {
            'p_event_code': code, 'p_min_v': min_v, 'p_max_v': max_v,
            'p_higher_better': higher, 'p_from_year': FROM_YEAR, 'p_to_year': TO_YEAR,
            'p_age_lo': age_lo, 'p_age_hi': age_hi, 'p_outdoor_only': True,
        })
        for r in rows:
            r['event'] = code
            r['top10_avg_fmt'] = fmt_value(r['top10_avg'], unit)
            r['rank25_fmt'] = fmt_value(r['rank25_value'], unit)
            r['rank50_fmt'] = fmt_value(r['rank50_value'], unit)
            r['rank100_fmt'] = fmt_value(r['rank100_value'], unit)
            r['best_fmt'] = fmt_value(r['best_value'], unit)
        all_rows.extend(rows)
        per_event[code] = rows
    write_csv(f'toppniva_{suffix}.csv', all_rows,
              ['event', 'yr', 'gender', 'n_athletes', 'top10_avg', 'top10_avg_fmt',
               'rank25_value', 'rank25_fmt', 'rank50_value', 'rank50_fmt',
               'rank100_value', 'rank100_fmt', 'best_value', 'best_fmt'])

    fig, axes = plt.subplots(2, 5, figsize=(22, 8))
    for col, (code, title, _, _, higher, unit) in enumerate(EVENTS):
        for row_i, g in enumerate(('M', 'F')):
            ax = axes[row_i][col]
            pts = sorted([r for r in per_event[code] if r['gender'] == g], key=lambda r: r['yr'])
            ys = [r['yr'] for r in pts]
            ax.plot(ys, [to_plot_value(r['top10_avg'], unit) for r in pts], marker='o', label='Snitt topp-10')
            ax.plot(ys, [to_plot_value(r['rank25_value'], unit) for r in pts], marker='s', ls='--', label='Nr. 25')
            ax.set_title(f"{title} — {GENDER_LABEL[g]}", fontsize=10)
            ax.grid(alpha=0.3)
            if not higher:
                ax.invert_yaxis()  # raskere = oppover
            if col == 0 and row_i == 0:
                ax.legend(fontsize=8)
            ax.set_ylabel('sek' if unit in ('s', 'min') else 'meter', fontsize=8)
    fig.suptitle(f'Nivåutvikling {FROM_YEAR}-{TO_YEAR} ({title_suffix}, utendørs). '
                 f'Pil oppover = bedre.', fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, f'fig3_toppniva_{suffix}.png')
    return per_event


# ------------------------------------------------------------
# 2b. Nivå per aldersklasse: topp-10 for 15, 16, 17, 18/19 år
# ------------------------------------------------------------

AGE_CLASSES = [('15 år', 15, 15), ('16 år', 16, 16), ('17 år', 17, 17), ('18/19 år', 18, 19)]
AGE_EVENTS = [e for e in EVENTS if e[0] in ('100m', '800m', 'lengde', 'hoyde')]


def analyse_aldersklasser():
    logger.info("2b/4 Nivå per aldersklasse ...")
    all_rows = []
    data = {}  # (code, label) -> rows
    for code, title, min_v, max_v, higher, unit in AGE_EVENTS:
        for label, lo, hi in AGE_CLASSES:
            rows = rpc('analyse_event_trend', {
                'p_event_code': code, 'p_min_v': min_v, 'p_max_v': max_v,
                'p_higher_better': higher, 'p_from_year': FROM_YEAR, 'p_to_year': TO_YEAR,
                'p_age_lo': lo, 'p_age_hi': hi, 'p_outdoor_only': True,
            })
            for r in rows:
                r['event'] = code
                r['age_class'] = label
                r['top10_avg_fmt'] = fmt_value(r['top10_avg'], unit)
                r['rank25_fmt'] = fmt_value(r['rank25_value'], unit)
            all_rows.extend(rows)
            data[(code, label)] = rows
    write_csv('toppniva_aldersklasser.csv', all_rows,
              ['event', 'age_class', 'yr', 'gender', 'n_athletes',
               'top10_avg', 'top10_avg_fmt', 'rank25_value', 'rank25_fmt'])

    fig, axes = plt.subplots(len(AGE_EVENTS), 2, figsize=(13, 4 * len(AGE_EVENTS)))
    for row_i, (code, title, _, _, higher, unit) in enumerate(AGE_EVENTS):
        for col, g in enumerate(('M', 'F')):
            ax = axes[row_i][col]
            for label, lo, hi in AGE_CLASSES:
                pts = sorted([r for r in data[(code, label)] if r['gender'] == g],
                             key=lambda r: r['yr'])
                ax.plot([r['yr'] for r in pts],
                        [to_plot_value(r['top10_avg'], unit) for r in pts],
                        marker='o', ms=3, label=label)
            ax.set_title(f"{title} — {GENDER_LABEL[g]} (snitt topp-10)", fontsize=10)
            ax.grid(alpha=0.3)
            if not higher:
                ax.invert_yaxis()
            ax.set_ylabel('sek' if unit in ('s', 'min') else 'meter', fontsize=8)
            if row_i == 0 and col == 0:
                ax.legend(fontsize=8)
    fig.suptitle('Nivåutvikling per aldersklasse (utendørs). Pil oppover = bedre.', fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    savefig(fig, 'fig4_aldersklasser.png')
    return data


# ------------------------------------------------------------
# 2c. Rekruttering: aktive per alderstrinn og kjønn
# ------------------------------------------------------------

def analyse_bredde_alder():
    logger.info("1b/4 Bredde per alderstrinn ...")
    rows = rpc('analyse_active_by_age', {'from_year': FROM_YEAR, 'to_year': TO_YEAR})
    write_csv('bredde_per_alder.csv', rows, ['yr', 'gender', 'age', 'n_athletes'])

    years = list(range(FROM_YEAR, TO_YEAR + 1))
    idx = {(r['gender'], r['age'], r['yr']): r['n_athletes'] for r in rows}
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
    for col, g in enumerate(('M', 'F')):
        ax = axes[col]
        for age in (11, 13, 15, 17, 19):
            ax.plot(years, [idx.get((g, age, y), 0) for y in years], marker='o', ms=3, label=f'{age} år')
        ax.set_title(GENDER_LABEL[g])
        ax.grid(alpha=0.3)
        ax.set_ylabel('Antall utøvere')
        ax.legend(fontsize=8)
    fig.suptitle('Aktive utøvere per alderstrinn — rekrutteringskullene år for år', fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    savefig(fig, 'fig2b_bredde_per_alder.png')
    return idx


# ------------------------------------------------------------
# 2d. Dybde: topp-10, nr. 25, 50 og 100 (alle aldre)
# ------------------------------------------------------------

def analyse_dybde(per_event_senior):
    logger.info("2c/4 Dybde ...")
    depth_events = [e for e in EVENTS if e[0] in ('100m', '800m', 'lengde')]
    fig, axes = plt.subplots(2, len(depth_events), figsize=(15, 8))
    for col, (code, title, _, _, higher, unit) in enumerate(depth_events):
        for row_i, g in enumerate(('M', 'F')):
            ax = axes[row_i][col]
            pts = sorted([r for r in per_event_senior[code] if r['gender'] == g],
                         key=lambda r: r['yr'])
            ys = [r['yr'] for r in pts]
            for key, lbl, style in (('top10_avg', 'Snitt topp-10', '-'),
                                    ('rank25_value', 'Nr. 25', '--'),
                                    ('rank50_value', 'Nr. 50', '-.'),
                                    ('rank100_value', 'Nr. 100', ':')):
                ax.plot(ys, [to_plot_value(r[key], unit) for r in pts],
                        style, marker='o', ms=3, label=lbl)
            ax.set_title(f"{title} — {GENDER_LABEL[g]}", fontsize=10)
            ax.grid(alpha=0.3)
            if not higher:
                ax.invert_yaxis()
            ax.set_ylabel('sek' if unit in ('s', 'min') else 'meter', fontsize=8)
            if col == 0 and row_i == 0:
                ax.legend(fontsize=8)
    fig.suptitle('Dybden i norsk friidrett: fra topp-10 til nr. 100 (alle aldre, utendørs). '
                 'Pil oppover = bedre.', fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    savefig(fig, 'fig6_dybde.png')


# ------------------------------------------------------------
# 3. Frafall: kohorter av 13-åringer
# ------------------------------------------------------------

def analyse_frafall():
    logger.info("4/4 Frafall ...")
    rows = rpc('analyse_survival', {'p_start_age': 13, 'p_cohort_from': 2013,
                                    'p_cohort_to': 2022, 'p_max_age': 19})
    write_csv('frafall_kohorter.csv', rows, ['cohort_year', 'gender', 'age', 'n_active'])

    # kohort -> age -> n (kjønn samlet), + startstørrelse
    coh = defaultdict(lambda: defaultdict(int))
    for r in rows:
        coh[r['cohort_year']][r['age']] += r['n_active']

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for cy in sorted(coh):
        max_age_observable = 13 + (TO_YEAR - cy)
        ages = [a for a in range(13, min(19, max_age_observable) + 1)]
        start = coh[cy][13]
        if start == 0 or len(ages) < 3:
            continue
        ax.plot(ages, [100 * coh[cy][a] / start for a in ages], marker='o', label=f'{cy} (n={start})')
    ax.set_title('Andel av 13-årskohorten som fortsatt konkurrerer, per alder')
    ax.set_xlabel('Alder')
    ax.set_ylabel('% fortsatt aktive')
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    savefig(fig, 'fig5_frafall_kohorter.png')
    return coh


# ------------------------------------------------------------
# 2e. Kast og hekk: vekt-/høydespesifikke øvelser per aldersklasse
# ------------------------------------------------------------
# Redskapsvekter og hekkhøyder varierer MED aldersklasse men har vært
# KONSTANTE per klasse gjennom hele perioden (verifisert empirisk: dominant
# variant per klasse/kjønn er stabil 2013-2025). Dermed er sammenligning
# innen klasse gyldig. Mappingen under er utledet fra resultatdataene selv
# (dominant øvelsesvariant per kjønn x kalenderalder).

KH_CLASSES = [('13 år', 13, 13), ('15 år', 15, 15), ('17 år', 17, 17),
              ('18/19 år', 18, 19), ('Senior', 20, 34)]

# familie -> kjønn -> klasselabel -> (event_code, kort redskapslabel)
KH_MAP = {
    'Kule': {
        'F': {'13 år': ('kule_2kg', '2kg'), '15 år': ('kule_3kg', '3kg'),
              '17 år': ('kule_3kg', '3kg'), '18/19 år': ('kule_4kg', '4kg'),
              'Senior': ('kule_4kg', '4kg')},
        'M': {'13 år': ('kule_3kg', '3kg'), '15 år': ('kule_4kg', '4kg'),
              '17 år': ('kule_5kg', '5kg'), '18/19 år': ('kule_6kg', '6kg'),
              'Senior': ('kule_7_26kg', '7,26kg')},
    },
    'Spyd': {
        'F': {'13 år': ('spyd_400g', '400g'), '15 år': ('spyd_500g', '500g'),
              '17 år': ('spyd_500g', '500g'), '18/19 år': ('spyd_600g', '600g'),
              'Senior': ('spyd_600g', '600g')},
        'M': {'13 år': ('spyd_400g', '400g'), '15 år': ('spyd_600g', '600g'),
              '17 år': ('spyd_700g', '700g'), '18/19 år': ('spyd_800g', '800g'),
              'Senior': ('spyd_800g', '800g')},
    },
    'Diskos': {
        'F': {'13 år': ('diskos_600g', '600g'), '15 år': ('diskos_750g', '750g'),
              '17 år': ('diskos_1kg', '1kg'), '18/19 år': ('diskos_1kg', '1kg'),
              'Senior': ('diskos_1kg', '1kg')},
        'M': {'13 år': ('diskos_750g', '750g'), '15 år': ('diskos_1kg', '1kg'),
              '17 år': ('diskos_1_5kg', '1,5kg'), '18/19 år': ('diskos_1_75kg', '1,75kg'),
              'Senior': ('diskos_2kg', '2kg')},
    },
    'Slegge': {
        'F': {'13 år': ('slegge_20kg/110cm', '2kg'), '15 år': ('slegge_30kg_1195cm', '3kg'),
              '17 år': ('slegge_30kg_1195cm', '3kg'), '18/19 år': ('slegge_40kg/1195cm', '4kg'),
              'Senior': ('slegge_40kg/1195cm', '4kg')},
        'M': {'13 år': ('slegge_30kg_1195cm', '3kg'), '15 år': ('slegge_40kg/1195cm', '4kg'),
              '17 år': ('slegge_50kg/120cm', '5kg'), '18/19 år': ('slegge_60kg/1215cm', '6kg'),
              'Senior': ('slegge_726kg/1215cm', '7,26kg')},
    },
    'Sprinthekk': {
        'F': {'13 år': ('60mh_76_2cm', '60m/76,2'), '15 år': ('80mh_76_2cm', '80m/76,2'),
              '17 år': ('100mh_76_2cm', '100m/76,2'), '18/19 år': ('100mh_84cm', '100m/84'),
              'Senior': ('100mh_84cm', '100m/84')},
        'M': {'13 år': ('60mh_76_2cm', '60m/76,2'), '15 år': ('100mh_84cm', '100m/84'),
              '17 år': ('110mh_91_4cm', '110m/91,4'), '18/19 år': ('110mh_100cm', '110m/100'),
              'Senior': ('110mh_106_7cm', '110m/106,7')},
    },
}

THROW_RANGE = {'Kule': (3000, 23000), 'Spyd': (5000, 90000),
               'Diskos': (5000, 75000), 'Slegge': (4000, 85000)}


def hurdle_range(code):
    dist = code.split('mh')[0]
    return {'60': (700, 2000), '80': (900, 2600),
            '100': (1100, 3200), '110': (1250, 3400)}[dist]


def analyse_kast_hekk():
    logger.info("2e/5 Kast og hekk per aldersklasse ...")
    all_rows = []
    data = {}  # (familie, gender, klasse) -> rows
    for family, per_gender in KH_MAP.items():
        higher = family != 'Sprinthekk'
        for g, per_class in per_gender.items():
            for label, code_impl in per_class.items():
                code, impl = code_impl
                lo, hi = dict((l, (a, b)) for l, a, b in KH_CLASSES)[label]
                min_v, max_v = THROW_RANGE[family] if higher else hurdle_range(code)
                rows = rpc('analyse_event_trend', {
                    'p_event_code': code, 'p_min_v': min_v, 'p_max_v': max_v,
                    'p_higher_better': higher, 'p_from_year': FROM_YEAR, 'p_to_year': TO_YEAR,
                    'p_age_lo': lo, 'p_age_hi': hi, 'p_outdoor_only': True,
                })
                unit = 'm' if higher else 's'
                for r in rows:
                    r.update(family=family, age_class=label, event=code, implement=impl,
                             top10_avg_fmt=fmt_value(r['top10_avg'], unit))
                all_rows.extend(r for r in rows if r['gender'] == g)
                data[(family, g, label)] = [r for r in rows if r['gender'] == g]
    write_csv('kast_hekk_aldersklasser.csv', all_rows,
              ['family', 'event', 'implement', 'age_class', 'yr', 'gender',
               'n_athletes', 'top10_avg', 'top10_avg_fmt', 'rank25_value'])

    # Kast: meter på y-aksen, linjer per klasse (redskap i etiketten)
    throw_families = ['Kule', 'Spyd', 'Diskos', 'Slegge']
    fig, axes = plt.subplots(len(throw_families), 2, figsize=(13, 4 * len(throw_families)))
    for row_i, family in enumerate(throw_families):
        for col, g in enumerate(('M', 'F')):
            ax = axes[row_i][col]
            for label, lo, hi in KH_CLASSES:
                rows = data.get((family, g, label), [])
                impl = KH_MAP[family][g][label][1]
                pts = sorted(rows, key=lambda r: r['yr'])
                ax.plot([r['yr'] for r in pts],
                        [to_plot_value(r['top10_avg'], 'm') for r in pts],
                        marker='o', ms=3, label=f'{label} ({impl})')
            ax.set_title(f"{family} — {GENDER_LABEL[g]} (snitt topp-10)", fontsize=10)
            ax.set_ylabel('meter', fontsize=8)
            ax.grid(alpha=0.3)
            if row_i == 0 and col == 0:
                ax.legend(fontsize=7)
    fig.suptitle('Kastøvelsene per aldersklasse (utendørs). Samme redskapsvekt per klasse '
                 'hele perioden — linjene er direkte sammenlignbare over tid.', fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    savefig(fig, 'fig8_kast.png')

    # Hekk: ulike distanser -> indekser mot første år (100 = startnivå, opp = bedre)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for col, g in enumerate(('M', 'F')):
        ax = axes[col]
        for label, lo, hi in KH_CLASSES:
            rows = sorted(data.get(('Sprinthekk', g, label), []), key=lambda r: r['yr'])
            impl = KH_MAP['Sprinthekk'][g][label][1]
            base = next((float(r['top10_avg']) for r in rows if r['top10_avg']), None)
            if not base:
                continue
            ax.plot([r['yr'] for r in rows],
                    [100 * base / float(r['top10_avg']) for r in rows],
                    marker='o', ms=3, label=f'{label} ({impl})')
        ax.axhline(100, color='gray', lw=0.8)
        ax.set_title(GENDER_LABEL[g])
        ax.set_ylabel('Indeks (første år = 100, høyere = raskere)', fontsize=8)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle('Sprinthekk per aldersklasse (utendørs, snitt topp-10, indeksert). '
                 'Samme distanse og høyde per klasse hele perioden.', fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    savefig(fig, 'fig9_hekk.png')
    return data


# ------------------------------------------------------------
# 3b. Barneidretten: frafall fra 10 år og debutalder
# ------------------------------------------------------------

def analyse_frafall_barn():
    """Kohorter av 10-åringer: overgangen barneidrett -> ungdomsfriidrett.
    NB: Kun deltakelse — ingen nivåanalyse for barn under 13
    (barneidrettsbestemmelsene)."""
    logger.info("3b/5 Frafall fra 10 år ...")
    rows = rpc('analyse_survival', {'p_start_age': 10, 'p_cohort_from': 2013,
                                    'p_cohort_to': 2022, 'p_max_age': 15})
    write_csv('frafall_barnekohorter.csv', rows, ['cohort_year', 'gender', 'age', 'n_active'])

    coh = defaultdict(lambda: defaultdict(int))
    for r in rows:
        coh[r['cohort_year']][r['age']] += r['n_active']

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for cy in sorted(coh):
        max_age_observable = 10 + (TO_YEAR - cy)
        ages = list(range(10, min(15, max_age_observable) + 1))
        start = coh[cy][10]
        if start == 0 or len(ages) < 4:
            continue
        ax.plot(ages, [100 * coh[cy][a] / start for a in ages], marker='o', label=f'{cy} (n={start})')
    ax.set_title('Andel av 10-årskohorten som fortsatt konkurrerer, per alder')
    ax.set_xlabel('Alder')
    ax.set_ylabel('% fortsatt aktive')
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    savefig(fig, 'fig5b_frafall_fra_10.png')
    return coh


def analyse_debut():
    """Debutalder: når kommer utøverne inn i konkurransefriidretten?"""
    logger.info("3c/5 Debutalder ...")
    rows = rpc('analyse_debut', {'from_year': 2015, 'to_year': TO_YEAR})
    write_csv('debutalder.csv', rows, ['yr', 'gender', 'debut_age', 'n'])

    years = list(range(2015, TO_YEAR + 1))
    groups = [('10-11 år', (10, 11)), ('12-13 år', (12, 13)),
              ('14-15 år', (14, 15)), ('16-19 år', (16, 17, 18, 19))]
    idx = defaultdict(int)
    for r in rows:
        idx[(r['yr'], r['debut_age'])] += r['n']

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for label, ages in groups:
        ax.plot(years, [sum(idx[(y, a)] for a in ages) for y in years], marker='o', label=label)
    ax.set_title('Debutanter per år etter alder ved første resultat')
    ax.set_ylabel('Antall debutanter')
    ax.grid(alpha=0.3)
    ax.legend()
    savefig(fig, 'fig7_debutalder.png')
    return idx


def main():
    by_band = analyse_bredde()
    analyse_bredde_alder()
    per_event_senior = analyse_topp()
    analyse_dybde(per_event_senior)
    age_data = analyse_aldersklasser()
    kh_data = analyse_kast_hekk()
    coh = analyse_frafall()
    coh_barn = analyse_frafall_barn()
    analyse_debut()

    # ------------------------------------------------------------
    # Nøkkeltall til artikkelen
    # ------------------------------------------------------------
    lines = ['# Nøkkeltall (autogenerert av generate.py)\n']
    pre = sum(by_band[b].get(2019, 0) for b in ('10-12', '13-14', '15-19'))
    post = sum(by_band[b].get(2025, 0) for b in ('10-12', '13-14', '15-19'))
    lines.append(f"- Aktive 10-19 år: {pre} (2019) -> {post} (2025), endring {100 * (post - pre) / pre:+.1f} %")
    for code, title, _, _, _, unit in EVENTS:
        for g in ('M', 'F'):
            pts = {r['yr']: r for r in per_event_senior[code] if r['gender'] == g}
            if 2013 in pts and 2025 in pts:
                lines.append(f"- {title} {GENDER_LABEL[g]}: topp-10-snitt "
                             f"{fmt_value(pts[2013]['top10_avg'], unit)} (2013) -> "
                             f"{fmt_value(pts[2025]['top10_avg'], unit)} (2025); "
                             f"nr. 25: {fmt_value(pts[2013]['rank25_value'], unit)} -> "
                             f"{fmt_value(pts[2025]['rank25_value'], unit)}")
    lines.append('\n## Aldersklasser (topp-10-snitt 2013 -> 2025, antall utøvere i parentes)')
    for code, title, _, _, _, unit in AGE_EVENTS:
        for label in ('15 år', '18/19 år'):
            for g in ('M', 'F'):
                pts = {r['yr']: r for r in age_data[(code, label)] if r['gender'] == g}
                if 2013 in pts and 2025 in pts:
                    lines.append(f"- {title} {label} {GENDER_LABEL[g]}: "
                                 f"{fmt_value(pts[2013]['top10_avg'], unit)} -> "
                                 f"{fmt_value(pts[2025]['top10_avg'], unit)} "
                                 f"(n: {pts[2013]['n_athletes']} -> {pts[2025]['n_athletes']})")
    lines.append('')
    for cy in (2014, 2019):
        if coh.get(cy, {}).get(13):
            surv = 100 * coh[cy].get(19, 0) / coh[cy][13]
            lines.append(f"- Frafall {cy}-kohorten: {surv:.0f} % av 13-åringene fortsatt aktive som 19-åringer")
    lines.append('\n## Kast og hekk (topp-10-snitt første -> siste år, samme redskap/høyde per klasse)')
    for family in KH_MAP:
        unit = 'm' if family != 'Sprinthekk' else 's'
        for g in ('M', 'F'):
            for label in ('15 år', 'Senior'):
                pts = {r['yr']: r for r in kh_data.get((family, g, label), [])}
                yrs = sorted(pts)
                if len(yrs) >= 2:
                    y0, y1 = yrs[0], yrs[-1]
                    impl = KH_MAP[family][g][label][1]
                    lines.append(f"- {family} {label} {GENDER_LABEL[g]} ({impl}): "
                                 f"{fmt_value(pts[y0]['top10_avg'], unit)} ({y0}) -> "
                                 f"{fmt_value(pts[y1]['top10_avg'], unit)} ({y1}) "
                                 f"(n: {pts[y0]['n_athletes']} -> {pts[y1]['n_athletes']})")

    lines.append('\n## Barneidretten (kun deltakelse — ingen nivåanalyse under 13)')
    for cy in sorted(coh_barn):
        c = coh_barn[cy]
        if c.get(10) and cy + 3 <= TO_YEAR:
            lines.append(f"- 10-åringer {cy}: {c[10]} startet, {100 * c.get(11, 0) / c[10]:.0f} % igjen ved 11, "
                         f"{100 * c.get(13, 0) / c[10]:.0f} % ved 13")
    (OUT / 'nokkeltall.md').write_text('\n'.join(lines) + '\n')
    logger.info(f"Skrev {OUT / 'nokkeltall.md'}")


if __name__ == '__main__':
    main()
