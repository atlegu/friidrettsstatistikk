#!/usr/bin/env python3
"""Figurer til foredraget fra de to nye artiklene (stagnasjon-exit og debutalder).

Leser bare ferdige tabeller (ingen persondata):
  forskning/stagnasjon-exit/tables/manus/fig2_data.csv, fig3_data.csv
  tallene i forskning/debutalder/manus/t2.tex og t3.tex (lagt inn under)

    ../../../scraper/venv/bin/python figurer_foredrag.py
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'bilder'
A1 = ROOT / 'forskning' / 'stagnasjon-exit' / 'tables' / 'manus'

BLUE, ORANGE, DARK, GRAY, GREEN, RED = '#1f4e79', '#d9480f', '#2b2b2b', '#b0b7bf', '#2b8a3e', '#c92a2a'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 12,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'axes.grid.axis': 'y', 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8,
    'axes.axisbelow': True, 'axes.titlesize': 15, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
    'xtick.color': DARK, 'ytick.color': DARK, 'axes.edgecolor': '#cccccc', 'figure.facecolor': 'white',
})
pct = mticker.FuncFormatter(lambda v, _: f"{v:.0f} %")

# ---------------------------------------------------------------- 1. Debutalder (A3, tabell 2 og 3)
alder = [10, 11, 12, 13, 14, 15, 16]
senior = [3.8, 2.4, 2.1, 2.9, 2.4, 3.9, 6.6]
n = [6626, 3616, 2529, 1691, 1747, 863, 424]
ret = {10: [51, 38, 29, 22, 17], 11: [40, 27, 19, 13, 10], 12: [37, 23, 14, 9, 7],
       13: [38, 23, 15, 10, 7], 14: [34, 13, 8, 5, 3], 15: [26, 13, 8, 5, 4], 16: [35, 21, 11, 7, 6]}

fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
ax = axes[0]
ax.plot(alder, senior, 'o-', color=BLUE, lw=2.8, ms=8)
for a, s, k in zip(alder, senior, n):
    ax.annotate(f"{s:.1f} %".replace('.', ','), (a, s), xytext=(0, 9), textcoords='offset points', ha='center', fontsize=11, fontweight='bold', color=BLUE)
ax.set_ylim(0, 8.5); ax.yaxis.set_major_formatter(pct); ax.set_xticks(alder)
ax.set_xlabel('Alder ved første stevne'); ax.set_title('Andel som er aktive som senior (20 år +)')
ax = axes[1]
for a, farge, dy in [(10, BLUE, 0), (12, '#6f8fb0', 5), (16, '#e8936b', -2), (14, ORANGE, -9)]:
    ax.plot(range(0, 6), [100] + ret[a], 'o-', color=farge, lw=2.6, ms=6)
    ax.annotate(f"Debut {a}", (5, ret[a][-1]), xytext=(8, dy), textcoords='offset points', va='center', color=farge, fontweight='bold', fontsize=11)
ax.set_ylim(0, 105); ax.yaxis.set_major_formatter(pct); ax.set_xticks(range(0, 6)); ax.set_xlim(-0.2, 6.3)
ax.set_xlabel('År etter debutsesongen'); ax.set_title('Fortsatt med, år for år etter debut')
fig.text(0.01, 0.985, 'Ingen alder er for sen. Men den første sesongen er filteret.', fontsize=16, fontweight='bold', va='top', color=DARK)
fig.text(0.01, 0.93, 'Alle som debuterte som 10–16-åring, født 2001–2005 (17 496 utøvere). Venstre: andel som ble seniorer. Høyre: hvor lenge de holdt på.', fontsize=11, va='top', color='#666666')
fig.tight_layout(rect=(0, 0, 1, 0.88)); fig.savefig(OUT / 'debut_u.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- 2. Stagnasjon før exit (A1, fig 2-data)
d = pd.read_csv(A1 / 'fig2_data.csv')
fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
for ax, panel, tittel, farge, enhet in [(axes[0], 'Age-graded performance', 'Prestasjon (Tyrving-poeng)', ORANGE, 'poeng'),
                                        (axes[1], 'Competition volume', 'Antall stevner', BLUE, 'stevner')]:
    s = d[d.panel == panel]
    x = [0, 1, 2, 3]
    ax.fill_between(x, s.ki_lav, s.ki_hoy, color=farge, alpha=0.15)
    ax.plot(x, s['median'], 's-', color=farge, lw=2.8, ms=8)
    for xi, v in zip(x, s['median']):
        ax.annotate(f"{v:+.0f}".replace('-', '−'), (xi, v), xytext=(0, 9 if v >= 0 else -16), textcoords='offset points', ha='center', fontsize=11, fontweight='bold', color=farge)
    ax.axhline(0, color='#999999', lw=1, ls='--')
    ax.set_xticks(x); ax.set_xticklabels(['3 sesonger før', '2 før', 'Siste før', 'Siste sesong'])
    ax.set_title(tittel); ax.set_ylabel(f'Endring fra eget nivå ({enhet})')
fig.text(0.01, 0.985, 'Deltakelsen faller først. Prestasjonen holder til siste sesong.', fontsize=16, fontweight='bold', va='top', color=DARK)
fig.text(0.01, 0.93, 'Utøvere som sluttet som 16–19-åringer, de fire siste sesongene, sammenlignet med eget nivå tre sesonger før exit. Median med 95 % intervall.', fontsize=11, va='top', color='#666666')
fig.tight_layout(rect=(0, 0, 1, 0.88)); fig.savefig(OUT / 'exit_aligned.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- 3. Fremgang × volum (A1, fig 3-data)
q = pd.read_csv(A1 / 'fig3_data.csv')
fig, ax = plt.subplots(figsize=(11, 5.4))
for tert, farge, navn in [('Low volume 15–16', RED, 'Få stevner som 15–16-åring (1–5)'),
                          ('Mid volume 15–16', GRAY, 'Middels (5–19)'),
                          ('High volume 15–16', GREEN, 'Mange (19 eller flere)')]:
    s = q[q.voltertil == tert]
    ax.plot(s.kvintil, s.andel_pst, 'o-', color=farge, lw=2.8, ms=8)
    ax.annotate(navn, (5, s.andel_pst.iloc[-1]), xytext=(10, 0), textcoords='offset points', va='center', color=farge, fontweight='bold', fontsize=11)
ax.set_xticks([1, 2, 3, 4, 5]); ax.set_xticklabels(['Størst tilbakegang', '2', '3', '4', 'Størst fremgang'])
ax.set_xlim(0.7, 7.2); ax.set_ylim(0, 55); ax.yaxis.set_major_formatter(pct)
ax.set_xlabel('Fremgang fra 13–14 til 15–16 år, femdeler'); ax.set_ylabel('Aktive som senior')
fig.text(0.01, 0.985, 'Fremgang teller, men bare der utøveren fortsatt er med', fontsize=16, fontweight='bold', va='top', color=DARK)
fig.text(0.01, 0.93, 'Andel som ble seniorer etter fremgang fra 13–14 til 15–16 år, delt etter hvor mange stevner de gikk som 15–16-åring (3 877 utøvere).', fontsize=11, va='top', color='#666666')
fig.tight_layout(rect=(0, 0, 1, 0.88)); fig.savefig(OUT / 'fremgang_volum.png', dpi=200); plt.close(fig)
print('Skrev debut_u, exit_aligned, fremgang_volum til', OUT)
