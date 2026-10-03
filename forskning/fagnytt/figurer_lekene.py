#!/usr/bin/env python3
"""Figurer i magasinstørrelse til lekene-artikkelen i Fagnytt.

Leser ferdige tabeller fra forskning/lekene-trend/tables/ (ingen databasetilgang).

    ../../scraper/venv/bin/python figurer_lekene.py
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
TAB = HERE.parent / 'lekene-trend' / 'tables'
OUT = HERE / 'figurer'

BLUE, ORANGE, DARK, GRAY = '#1f4e79', '#d9480f', '#2b2b2b', '#b0b7bf'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8, 'axes.axisbelow': True,
    'xtick.color': DARK, 'ytick.color': DARK, 'axes.edgecolor': '#cccccc', 'figure.facecolor': 'white',
})
KLASSER = [('G13', BLUE, 'o', 'Gutter 13'), ('G14', BLUE, 's', 'Gutter 14'),
           ('J13', ORANGE, 'o', 'Jenter 13'), ('J14', ORANGE, 's', 'Jenter 14')]


def no(x, d=0):
    return f"{x:.{d}f}".replace('.', ',')


def forklaring(fig, ekstra=None, y=0.005):
    h = [Line2D([], [], color=c, marker=m, ls='-' if m == 's' else '--', lw=1.8, ms=6, label=l)
         for _, c, m, l in KLASSER]
    if ekstra:
        h += ekstra
    fig.legend(handles=h, loc='lower center', ncol=len(h), frameon=False, fontsize=9.5,
               bbox_to_anchor=(0.5, y), handlelength=2.2, columnspacing=1.6)


# ---------------------------------------------------------------- Figur 1: trendoversikt
t = pd.read_csv(TAB / 'trender_per_serie.csv')
grupper = ['Sprint', 'Hekk', 'Mellomdistanse', 'Horisontale hopp', 'Vertikale hopp', 'Kast']
t['_g'] = t['ovelsesgruppe'].map(grupper.index)
t = t.sort_values('_g', kind='stable')
order = list(dict.fromkeys(t['ovelse']))
fig, axes = plt.subplots(1, 2, figsize=(7.3, 7.6), sharey=True)
off = {'G13': -0.27, 'G14': -0.09, 'J13': 0.09, 'J14': 0.27}
for ax, lab, tittel in zip(axes, ['median', 'topp'], ['Bredden (medianen)', 'Toppen (beste desil)']):
    for g, c, m, _ in KLASSER:
        for _, r in t[t['gruppe'] == g].iterrows():
            y = order.index(r['ovelse']) + off[g]
            ax.plot([r[f'{lab}_ki_lo'], r[f'{lab}_ki_hi']], [y, y], color=c, lw=1.1, alpha=0.55)
            ax.plot(r[f'{lab}_pct_tiaar'], y, m, color=c, ms=5.5, mew=1.3,
                    mfc=c if r[f'{lab}_p'] < 0.05 else 'white')
    ax.axvline(0, color=DARK, lw=1)
    i = 0
    for gr in grupper:
        n = t.loc[t['ovelsesgruppe'] == gr, 'ovelse'].nunique()
        if i:
            ax.axhline(i - 0.5, color='#cccccc', lw=0.8)
        i += n
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order, fontsize=10)
    ax.set_ylim(len(order) - 0.5, -0.5); ax.set_xlim(-27, 17)
    ax.grid(axis='y', visible=False)
    ax.set_title(tittel, loc='left', fontweight='bold', fontsize=11.5, color=DARK)
    ax.set_xlabel('Prosent bedre per tiår')
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
forklaring(fig, [Line2D([], [], color=DARK, marker='o', ls='', mfc='white', ms=6, label='ikke sikker')])
fig.tight_layout(rect=(0, 0.045, 1, 1), w_pad=1.5)
fig.savefig(OUT / 'lek_fig1_trender.png', dpi=220); plt.close(fig)

# ---------------------------------------------------------------- Figur 2: kast, median per år
k = pd.read_csv(TAB / 'kvantiler_per_aar.csv')
k = k[k['n'] >= 10]
fig, axes = plt.subplots(2, 2, figsize=(7.3, 6.0), sharex=True)
for ax, navn in zip(axes.flat, ['Spyd', 'Kule', 'Diskos', 'Slegge']):
    sub = k[k['ovelse'].str.startswith(navn)]
    for g, c, m, _ in KLASSER:
        s = sub[sub['gruppe'] == g]
        s = s[s['ovelse'] == s['ovelse'].value_counts().idxmax()].sort_values('yr')   # klassens faste redskap
        ax.plot(s['yr'], s['median'], marker=m, color=c, ls='-' if m == 's' else '--', lw=1.9, ms=4.5)
    ax.axvspan(2019.5, 2021.5, color='#f1f1f1', zorder=0)
    ax.set_title(navn, loc='left', fontweight='bold', fontsize=11.5, color=DARK)
    d = 1 if navn == 'Kule' else 0
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _, d=d: f"{no(v, d)} m"))
    ax.set_xticks(range(2012, 2027, 2)); ax.grid(axis='x', visible=False)
forklaring(fig)
fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=1.4)
fig.savefig(OUT / 'lek_fig2_kast.png', dpi=220); plt.close(fig)

# ---------------------------------------------------------------- Figur 3: forbedring 13 -> 14
g = pd.read_csv(TAB / 'gjentakere_forbedring.csv')
g = g[g['n'] >= 10]
fig, axes = plt.subplots(2, 3, figsize=(7.3, 5.2), sharex=True)
for ax, navn in zip(axes.flat, ['60 m', '600 m', '1500 m', 'Lengde', 'Høyde', 'Stav']):
    for sx, c, l in [('G', BLUE, 'Gutter'), ('J', ORANGE, 'Jenter')]:
        s = g[(g['ovelse'] == navn) & (g['sex'] == sx)].sort_values('yr')
        ax.plot(s['yr'], s['median_forb'], 'o-', color=c, lw=1.9, ms=4, label=l)
    ax.axhline(0, color='#bbbbbb', lw=0.8)
    ax.axvspan(2019.5, 2021.5, color='#f1f1f1', zorder=0)
    ax.set_title(navn + (' (tre år samlet)' if navn == 'Stav' else ''), loc='left', fontweight='bold',
                 fontsize=11, color=DARK)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{no(v)} %"))
    ax.set_xticks([2014, 2018, 2022, 2026]); ax.grid(axis='x', visible=False)
h = [Line2D([], [], color=BLUE, marker='o', lw=1.9, label='Gutter'),
     Line2D([], [], color=ORANGE, marker='o', lw=1.9, label='Jenter')]
fig.legend(handles=h, loc='lower center', ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.0))
fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=1.4)
fig.savefig(OUT / 'lek_fig3_forbedring.png', dpi=220); plt.close(fig)
print('Skrev lek_fig1-3 til', OUT)
