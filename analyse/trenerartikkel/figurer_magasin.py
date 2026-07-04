#!/usr/bin/env python3
"""Publiseringsklare figurer til trenerforening-artikkelen.

Leser CSV-ene fra generate.py (ingen databasetilgang nødvendig) og lager
magasin-stylede figurer (figM1-figM6) i output/.

    ../../scraper/venv/bin/python figurer_magasin.py
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUT = Path(__file__).resolve().parent / 'output'

# ---------- stil ----------
BLUE = '#1f4e79'      # hovedfarge (menn/gutter der kjønn skilles)
ORANGE = '#d9480f'    # kvinner/jenter
GRAY = '#b0b7bf'
DARK = '#2b2b2b'
GREEN = '#2b8a3e'
RED = '#c92a2a'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.grid': True,
    'axes.grid.axis': 'y',
    'grid.color': '#e6e6e6',
    'grid.linewidth': 0.8,
    'axes.axisbelow': True,
    'axes.titlesize': 15,
    'axes.titleweight': 'bold',
    'axes.titlelocation': 'left',
    'axes.titlepad': 14,
    'xtick.color': DARK, 'ytick.color': DARK,
    'axes.edgecolor': '#cccccc',
    'figure.facecolor': 'white',
})


def no_num(x, dec=0):
    """Norsk tallformat (mellomrom som tusenskiller, komma som desimal)."""
    s = f"{x:,.{dec}f}".replace(',', ' ').replace('.', ',')
    return s


def load(name):
    with open(OUT / name, encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def headline(ax, title, subtitle):
    ax.set_title(title, pad=32)
    ax.text(0, 1.03, subtitle, transform=ax.transAxes, fontsize=10.5,
            color='#555555', va='bottom')


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print('Skrev', OUT / name)


YEARS = list(range(2013, 2026))


# ================================================================
# M1 — Ungdomsbredden: én tydelig linje med covid-markering
# ================================================================

def m1():
    rows = load('bredde_aktive.csv')
    per_year = defaultdict(int)
    for r in rows:
        if r['age_band'] in ('10-12', '13-14', '15-19'):
            per_year[int(r['yr'])] += int(r['n_athletes'])
    vals = [per_year[y] for y in YEARS]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axvspan(2019.5, 2021.5, color='#f3f3f3', zorder=0)
    ax.plot(YEARS, vals, color=BLUE, lw=3, marker='o', ms=6,
            markerfacecolor='white', markeredgewidth=2, zorder=3)
    for y, v in [(2019, per_year[2019]), (2025, per_year[2025])]:
        ax.annotate(no_num(v), (y, v), textcoords='offset points',
                    xytext=(0, 12), ha='center', fontweight='bold', color=BLUE)
    ax.text(2020.5, min(vals) * 0.99, 'pandemi', ha='center', fontsize=9.5,
            color='#888888', style='italic')
    pct = 100 * (per_year[2025] - per_year[2019]) / per_year[2019]
    headline(ax, 'Hver fjerde ungdom er borte',
             f'Aktive utøvere 10–19 år med minst ett resultat per år. '
             f'{no_num(abs(pct))} % færre i 2025 enn i 2019.')
    ax.set_ylim(0, max(vals) * 1.15)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: no_num(v)))
    save(fig, 'figM1_ungdomsbredde.png')


# ================================================================
# M2 — Frafall: alle kohorter i grått, budskapet er likheten
# ================================================================

def m2():
    rows = load('frafall_kohorter.csv')
    coh = defaultdict(lambda: defaultdict(int))
    for r in rows:
        coh[int(r['cohort_year'])][int(r['age'])] += int(r['n_active'])

    fig, ax = plt.subplots(figsize=(9, 5))
    for cy in sorted(coh):
        max_age = 13 + (2025 - cy)
        ages = [a for a in range(13, min(19, max_age) + 1)]
        start = coh[cy][13]
        if start == 0 or len(ages) < 4:
            continue
        share = [100 * coh[cy][a] / start for a in ages]
        hilite = cy in (2013, 2019, 2022)
        color = {2013: BLUE, 2019: ORANGE, 2022: GREEN}.get(cy, GRAY)
        ax.plot(ages, share, color=color, lw=2.5 if hilite else 1.2,
                marker='o' if hilite else None, ms=5,
                zorder=3 if hilite else 2, alpha=1 if hilite else 0.7)
        if hilite:
            dy = {2013: -10, 2019: 8, 2022: 0}[cy]
            ax.annotate(f'{cy}-kullet', (ages[-1], share[-1]),
                        textcoords='offset points', xytext=(8, dy),
                        va='center', color=color, fontweight='bold', fontsize=10)
    ax.annotate('Halvparten borte\netter ett år', (14, 55),
                textcoords='offset points', xytext=(20, 30), fontsize=10,
                color=DARK, ha='left',
                arrowprops=dict(arrowstyle='-', color='#999999', lw=0.8))
    headline(ax, 'Frafallet er som før — det er inntaket som svikter',
             'Andel av 13-åringene som fortsatt konkurrerer ved hver alder. Ti årskull, samme kurve.')
    ax.set_xlabel('Alder')
    ax.set_ylim(0, 105)
    ax.set_xlim(12.8, 20.2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:.0f} %'))
    save(fig, 'figM2_frafall.png')


# ================================================================
# Hjelpere for endringsberegning (snitt av to første / to siste år)
# ================================================================

def two_year_mean(pts, years):
    vals = [float(pts[y]) for y in years if y in pts and pts[y] not in (None, '')]
    return sum(vals) / len(vals) if vals else None


def pct_change(rows, key, higher_better):
    """% forbedring fra snitt(2013-14) til snitt(2024-25)."""
    pts = {int(r['yr']): r[key] for r in rows if r.get(key)}
    v0 = two_year_mean(pts, (2013, 2014))
    v1 = two_year_mean(pts, (2024, 2025))
    if not v0 or not v1:
        return None
    return 100 * ((v1 - v0) / v0 if higher_better else (v0 - v1) / v0)


# ================================================================
# M3 — Senior vs. 15-åringene: parvise søyler per øvelse
# ================================================================

def m3():
    senior = load('toppniva_senior.csv')
    aldk = load('toppniva_aldersklasser.csv')
    kast = load('kast_hekk_aldersklasser.csv')

    events = [('100 m', '100m', False), ('800 m', '800m', False),
              ('Lengde', 'lengde', True), ('Høyde', 'hoyde', True),
              ('Kule', 'Kule', True), ('Spyd', 'Spyd', True),
              ('Diskos', 'Diskos', True)]

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6), sharex=True)
    for col, g in enumerate(('M', 'F')):
        ax = axes[col]
        labels, sen_vals, u15_vals = [], [], []
        for title, code, higher in events:
            if code in ('Kule', 'Spyd', 'Diskos'):
                sen_rows = [r for r in kast if r['family'] == code and r['gender'] == g
                            and r['age_class'] == 'Senior']
                u15_rows = [r for r in kast if r['family'] == code and r['gender'] == g
                            and r['age_class'] == '15 år']
            else:
                sen_rows = [r for r in senior if r['event'] == code and r['gender'] == g]
                u15_rows = [r for r in aldk if r['event'] == code and r['gender'] == g
                            and r['age_class'] == '15 år']
            labels.append(title)
            sen_vals.append(pct_change(sen_rows, 'top10_avg', higher))
            u15_vals.append(pct_change(u15_rows, 'top10_avg', higher))

        ypos = range(len(labels))[::-1]
        h = 0.36
        ax.barh([y + h / 2 for y in ypos], [v or 0 for v in sen_vals], height=h,
                color=BLUE if g == 'M' else ORANGE, label='Senior')
        ax.barh([y - h / 2 for y in ypos], [v or 0 for v in u15_vals], height=h,
                color=GRAY, label='15 år')
        ax.axvline(0, color=DARK, lw=1)
        ax.set_yticks(list(ypos), labels)
        ax.grid(axis='x'); ax.grid(axis='y', visible=False)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f'{v:+.0f} %'))
        ax.set_title(('Menn/gutter' if g == 'M' else 'Kvinner/jenter'), fontsize=12, loc='center')
        if col == 0:
            ax.legend(loc='lower right', frameon=False)
    fig.suptitle('Toppen løfter seg — 15-åringene faller', fontsize=15,
                 fontweight='bold', x=0.01, ha='left')
    fig.text(0.01, 0.92, 'Endring i snittet av de 10 beste, fra 2013/14 til 2024/25. '
             'Kast målt med klassens faste redskap.', fontsize=10.5, color='#555555')
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    save(fig, 'figM3_topp_vs_15.png')


# ================================================================
# M4 — Rekruttering: barna kommer tilbake, tenåringsdebuten uteblir
# ================================================================

def m4():
    rows = load('debutalder.csv')
    idx = defaultdict(int)
    for r in rows:
        idx[(int(r['yr']), int(r['debut_age']))] += int(r['n'])
    years = list(range(2015, 2026))
    young = [sum(idx[(y, a)] for a in (10, 11, 12)) for y in years]
    teen = [sum(idx[(y, a)] for a in range(13, 20)) for y in years]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axvspan(2019.5, 2021.5, color='#f3f3f3', zorder=0)
    ax.plot(years, young, color=GREEN, lw=3, marker='o', ms=5)
    ax.plot(years, teen, color=RED, lw=3, marker='o', ms=5)
    ax.annotate('Debut 10–12 år', (years[-1], young[-1]), xytext=(8, 0),
                textcoords='offset points', va='center', color=GREEN, fontweight='bold')
    ax.annotate('Debut 13–19 år', (years[-1], teen[-1]), xytext=(8, 0),
                textcoords='offset points', va='center', color=RED, fontweight='bold')
    headline(ax, 'Veien inn i tenårene gror igjen',
             'Antall utøvere med sitt aller første resultat, etter alder ved debut.')
    ax.set_ylim(0, max(young) * 1.15)
    ax.set_xlim(2014.6, 2027.2)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: no_num(v)))
    save(fig, 'figM4_debut.png')


# ================================================================
# M5 — Kule G15: «samme kule, to meter kortere»
# ================================================================

def m5():
    kast = load('kast_hekk_aldersklasser.csv')
    pts = {int(r['yr']): float(r['top10_avg']) / 1000
           for r in kast if r['family'] == 'Kule' and r['gender'] == 'M'
           and r['age_class'] == '15 år' and r['top10_avg']}
    yrs = sorted(pts)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(yrs, [pts[y] for y in yrs], color=RED, lw=3, marker='o', ms=6,
            markerfacecolor='white', markeredgewidth=2)
    for y in (yrs[0], yrs[-1]):
        ax.annotate(no_num(pts[y], 2) + ' m', (y, pts[y]), textcoords='offset points',
                    xytext=(0, 12), ha='center', fontweight='bold', color=RED)
    headline(ax, 'Samme kule — to meter kortere',
             'Snittet av de 10 beste 15-årige guttene i kule (4 kg), utendørs.')
    ax.set_ylim(10, 16)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: no_num(v) + ' m'))
    save(fig, 'figM5_kule_g15.png')


# ================================================================
# M6 — Seniorfremgangen: 800 m kvinner som eksempel
# ================================================================

def m6():
    senior = load('toppniva_senior.csv')
    fig, ax = plt.subplots(figsize=(9, 5))
    for g, color in (('F', ORANGE), ('M', BLUE)):
        pts = {int(r['yr']): float(r['top10_avg']) / 100
               for r in senior if r['event'] == '800m' and r['gender'] == g and r['top10_avg']}
        yrs = sorted(pts)
        ax.plot(yrs, [pts[y] for y in yrs], color=color, lw=3, marker='o', ms=5)
        lbl = 'Kvinner' if g == 'F' else 'Menn'

        def mmss(v):
            return f"{int(v // 60)}:{v % 60:05.2f}".replace('.', ',')
        ax.annotate(f"{lbl}  {mmss(pts[yrs[-1]])}", (yrs[-1], pts[yrs[-1]]),
                    xytext=(8, 0), textcoords='offset points', va='center',
                    color=color, fontweight='bold')
    headline(ax, 'Mellomdistansen drar hele feltet med seg',
             'Snittet av de 10 beste på 800 meter per år (utendørs, elektronisk tid).')
    ax.set_xlim(2012.6, 2027.8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: f"{int(v // 60)}:{v % 60:04.1f}".replace('.', ',')))
    ax.invert_yaxis()
    save(fig, 'figM6_800m.png')


if __name__ == '__main__':
    m1(); m2(); m3(); m4(); m5(); m6()
