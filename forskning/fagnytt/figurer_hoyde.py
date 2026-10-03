#!/usr/bin/env python3
"""Figurer til høydehopp-artikkelen (Hofstad) i Fagnytt: resultatet til nr. 1, 5, 10, 25 og 50 på årslisten, 1968-2026.

Kilde: Høydetilgraf.csv (årslister, norske utøvere). Damer 2006 mangler i filen og vises som brudd.

    ../../scraper/venv/bin/python figurer_hoyde.py
"""
from pathlib import Path
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mc

HERE = Path(__file__).resolve().parent
OUT = HERE / 'figurer'
BLUE, ORANGE, DARK, GRAY = '#1f4e79', '#d9480f', '#2b2b2b', '#777777'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 9.5,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'axes.grid.axis': 'y', 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8,
    'axes.axisbelow': True, 'xtick.color': DARK, 'ytick.color': DARK, 'axes.edgecolor': '#cccccc',
    'figure.facecolor': 'white',
})

raw = pd.read_csv(HERE / 'Høydetilgraf.csv', sep=';', header=None, skiprows=2, encoding='utf-8-sig')
cols = ['aar'] + [f'h{n}' for n in (1, 3, 5, 10, 25, 50)] + [f'd{n}' for n in (1, 3, 5, 10, 25, 50)]
raw.columns = cols
raw = raw.apply(pd.to_numeric, errors='coerce').dropna(subset=['aar'])
raw['aar'] = raw.aar.astype(int)

NR = [1, 5, 10, 25, 50]


def ramp(color, n):
    """Mørk til lys i samme fargetone: nr. 1 mørkest og tykkest."""
    base = np.array(mc.to_rgb(color))
    return [tuple(base + (1 - base) * t) for t in np.linspace(0, 0.68, n)]


def komma(v, d=2):
    return f'{v:.{d}f}'.replace('.', ',')


def tittel_s(fig, hoved, under):
    fig.text(0.01, 0.985, hoved, fontsize=13, fontweight='bold', va='top', ha='left', color=DARK)
    fig.text(0.01, 0.925, '\n'.join(textwrap.wrap(under, 62)), fontsize=8.6, va='top', ha='left', color='#666666')


def tegn(prefiks, farge, hoved, under, ylo, fil):
    fig, ax = plt.subplots(figsize=(5.4, 4.5))
    farger = ramp(farge, len(NR))
    for i, n in enumerate(NR):
        y = raw.set_index('aar')[f'{prefiks}{n}']
        lw = 2.2 if n == 1 else 1.5
        ax.plot(y.index, y.values, color=farger[i], lw=lw, solid_capstyle='round', zorder=5 - i)
        siste = y.dropna()
        ax.text(2026.8, siste.iloc[-1], f'Nr. {n}', color=farger[i] if n > 1 else farge, fontsize=8, fontweight='bold',
                va='center', ha='left')
    # toppverdi for nr. 1
    y1 = raw.set_index('aar')[f'{prefiks}1']
    ax.annotate(f'{komma(y1.max())} ({int(y1.idxmax())})', (y1.idxmax(), y1.max()), xytext=(-4, 6), textcoords='offset points',
                ha='right', fontsize=7.8, color=farge, fontweight='bold')
    # årtusenskiftet
    ax.axvline(2000, color='#999999', lw=0.9, ls=(0, (3, 3)), zorder=1)
    ax.text(2000.4, ylo + 0.01, 'År 2000', fontsize=7.5, color=GRAY, va='bottom', ha='left')
    ax.set_xlim(1967, 2031)
    ax.set_ylim(ylo, ylo + 0.85)
    ax.set_xticks(range(1970, 2030, 10))
    ax.set_yticks(np.arange(ylo + 0.05, ylo + 0.86, 0.1) if False else ax.get_yticks())
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: komma(v, 1) if abs(v * 10 - round(v * 10)) < 1e-6 else komma(v, 2)))
    ax.set_ylabel('Høyde (m)', fontsize=8.5, color=GRAY)
    tittel_s(fig, hoved, under)
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    fig.savefig(OUT / fil, dpi=220)
    plt.close(fig)


tegn('h', BLUE, 'Herrer: toppen og bredden går tilbake',
     'Resultat for nr. 1, 5, 10, 25 og 50 på norsk årsliste i høyde, 1968–2026.', 1.55, 'hoyde_fig1_herrer.png')
tegn('d', ORANGE, 'Damer: toppen og bredden går tilbake',
     'Resultat for nr. 1, 5, 10, 25 og 50 på norsk årsliste i høyde, 1968–2026.', 1.25, 'hoyde_fig2_damer.png')
print('ok')
