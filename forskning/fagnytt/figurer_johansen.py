#!/usr/bin/env python3
"""Figur til Bjørn Johansens artikkel i Fagnytt: gjennomsnittlig 40 m-tid før og etter seks uker.
Tallene er lest av figur 3 i den publiserte studien (Johansen m.fl., 2025) slik de sto i manuskriptet.
    ../../scraper/venv/bin/python figurer_johansen.py
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / 'figurer'
BLUE, ORANGE, DARK = '#1f4e79', '#d9480f', '#2b2b2b'
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'axes.grid.axis': 'y', 'grid.color': '#e6e6e6', 'axes.axisbelow': True,
    'xtick.color': DARK, 'ytick.color': DARK, 'axes.edgecolor': '#cccccc'})

data = [('Bounding', 6.30, 6.27, ORANGE), ('Single leg jumps', 6.19, 6.08, BLUE)]
fig, ax = plt.subplots(figsize=(7, 4.3))
for i, (navn, før, etter, c) in enumerate(data):
    ax.plot([i, i], [før, etter], color=c, lw=3, alpha=.35, solid_capstyle='round')
    ax.scatter([i], [før], s=110, facecolor='white', edgecolor=c, linewidth=2.5, zorder=3)
    ax.scatter([i], [etter], s=110, color=c, zorder=3)
    k = lambda v: f'{v:.2f}'.replace('.', ',')
    ax.text(i + .07, før, f'før {k(før)}', va='center', color=DARK, fontsize=10.5)
    ax.text(i + .07, etter, f'etter {k(etter)}', va='center', color=c, fontsize=10.5, fontweight='bold')
    ax.text(i, min(før, etter) - .045, f'{k(etter - før)} s'.replace('-', '−'), ha='center', color=c, fontsize=12, fontweight='bold')
ax.set_xlim(-.5, 1.6); ax.set_ylim(5.98, 6.38)
ax.set_xticks([0, 1]); ax.set_xticklabels([d[0] for d in data], fontsize=12, fontweight='bold')
ax.set_ylabel('Gjennomsnittlig 40 m-tid (s)')
ax.invert_yaxis()
ax.set_yticks([6.0,6.1,6.2,6.3]); ax.set_yticklabels(['6,0','6,1','6,2','6,3'])
fig.tight_layout()
fig.savefig(OUT / 'johansen_fig1_40m.png', dpi=200)
