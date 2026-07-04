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
        w = csv.DictWriter(fh, fieldnames=fieldnames)
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
            r['best_fmt'] = fmt_value(r['best_value'], unit)
        all_rows.extend(rows)
        per_event[code] = rows
    write_csv(f'toppniva_{suffix}.csv', all_rows,
              ['event', 'yr', 'gender', 'n_athletes', 'top10_avg', 'top10_avg_fmt',
               'rank25_value', 'rank25_fmt', 'best_value', 'best_fmt'])

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


def main():
    by_band = analyse_bredde()
    per_event_senior = analyse_topp()
    analyse_topp(age_lo=15, age_hi=15, suffix='15aringer', title_suffix='15-åringer')
    coh = analyse_frafall()

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
    for cy in (2014, 2019):
        if coh.get(cy, {}).get(13):
            surv = 100 * coh[cy].get(19, 0) / coh[cy][13]
            lines.append(f"- Frafall {cy}-kohorten: {surv:.0f} % av 13-åringene fortsatt aktive som 19-åringer")
    (OUT / 'nokkeltall.md').write_text('\n'.join(lines) + '\n')
    logger.info(f"Skrev {OUT / 'nokkeltall.md'}")


if __name__ == '__main__':
    main()
