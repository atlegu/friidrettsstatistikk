#!/usr/bin/env python3
"""Figurer til superskoartikkelen i Fagnytt.

Datafilene lages av shoes/scripts/ncaa_07_clean_analysis.R og eksporteres til
CSV med et lite R-skript (se fagnytt_sko_data.R i samme mappe).

    ../../scraper/venv/bin/python figurer_sko.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / 'figurer'
DATA = HERE / 'data_sko'

BLUE, ORANGE, GRAY, DARK, RED = '#1f4e79', '#d9480f', '#b0b7bf', '#2b2b2b', '#c92a2a'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'axes.grid.axis': 'y', 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8,
    'axes.axisbelow': True, 'axes.titlesize': 15, 'axes.titleweight': 'bold',
    'axes.titlelocation': 'left', 'axes.titlepad': 14,
    'xtick.color': DARK, 'ytick.color': DARK, 'axes.edgecolor': '#cccccc',
    'figure.facecolor': 'white',
})


def tittel(fig, hoved, under):
    fig.text(0.01, 0.985, hoved, fontsize=16, fontweight='bold', va='top', ha='left', color=DARK)
    fig.text(0.01, 0.930, under, fontsize=11, va='top', ha='left', color='#666666')


def komma(x, dec=2):
    return f"{x:.{dec}f}".replace('.', ',')


# ------------------------------------------------------------------ Figur 1
trend = pd.read_csv(DATA / 'fagnytt_trend.csv')

GRUPPER = [
    ('distance_spikes', 'Distanse (800 m–10 000 m)', RED, 2.3, 'o'),
    ('sprint', 'Sprint (60 m–400 m hekk)', BLUE, 2.0, 'o'),
    ('control', 'Tekniske øvelser (kontroll)', GRAY, 2.0, 'o'),
]

fig, ax = plt.subplots(figsize=(9.4, 4.5))
for key, lab, col, lw, mk in GRUPPER:
    d = trend[trend.treatment_group == key].sort_values('academic_year')
    ax.plot(d.academic_year, d.mean_z, color=col, lw=lw, marker=mk, ms=5,
            label=lab, zorder=3, clip_on=False)

ax.axvline(2021, color=DARK, lw=1.0, ls=(0, (4, 3)), alpha=0.55, zorder=1)
ax.text(2021.1, 1.30, 'Karbonpiggene\nslår gjennom', fontsize=9.5, color=DARK,
        va='top', ha='left', linespacing=1.35)

ax.set_xlim(2014.7, 2025.3)
ax.set_ylim(0.8, 1.95)
ax.set_xticks([2015, 2017, 2019, 2021, 2023, 2025])
ax.set_yticks([0.8, 1.0, 1.2, 1.4, 1.6, 1.8])
ax.set_yticklabels([komma(v, 1) for v in [0.8, 1.0, 1.2, 1.4, 1.6, 1.8]])
ax.set_ylabel('Gjennomsnittlig z-skår', color='#555555', fontsize=10)
ax.tick_params(length=0)

for key, lab, col, lw, mk in GRUPPER:
    d = trend[trend.treatment_group == key].sort_values('academic_year')
    ax.annotate(lab.split(' (')[0], xy=(2025.05, d.mean_z.iloc[-1]), color=col,
                fontsize=10.5, fontweight='bold', va='center', ha='left',
                xytext=(4, 0), textcoords='offset points')

tittel(fig, 'Distanseøvelsene skiller lag etter 2021',
       'Gjennomsnittlig standardisert resultat blant de 100 beste hvert år. Høyere er bedre.')
fig.text(0.01, 0.02, 'Sesongen 2020 er utelatt (pandemien). Skalaen er z-skår med 2015–2018 som referanse.',
         fontsize=9, color='#888888', ha='left')
fig.subplots_adjust(left=0.075, right=0.80, top=0.80, bottom=0.13)
fig.savefig(OUT / 'sko_fig1_trend.png', dpi=300)
plt.close(fig)

# ------------------------------------------------------------------ Figur 2
dose = pd.read_csv(DATA / 'fagnytt_dose.csv')
dist = dose[dose.treatment_group == 'distance_spikes'].copy()
spr = dose[dose.treatment_group == 'sprint'].copy()

NAVN = {'60': '60 m', '60H': '60 m hk', '100': '100 m', '100H': '100 m hk',
        '110H': '110 m hk', '200': '200 m', '400': '400 m', '400H': '400 m hk',
        '800': '800 m', '1500': '1500 m', 'MILE': 'Mile', '3000': '3000 m',
        '3000S': '3000 m hi', '5000': '5000 m', '10000': '10 000 m'}

fig, ax = plt.subplots(figsize=(9.4, 4.8))
ax.axhline(0, color='#cccccc', lw=1.0, zorder=1)

for d, col, lab in [(spr, BLUE, 'Sprintøvelser'), (dist, RED, 'Distanseøvelser')]:
    ax.errorbar(d.log_dist, d.coef, yerr=[d.coef - d.ci_lo, d.ci_hi - d.coef],
                fmt='o', ms=7, color=col, ecolor=col, elinewidth=1.4,
                capsize=0, alpha=0.95, zorder=3, label=lab)

b, a = np.polyfit(dist.log_dist, dist.coef, 1)
xs = np.linspace(dist.log_dist.min() - 0.15, dist.log_dist.max() + 0.15, 50)
ax.plot(xs, a + b * xs, color=RED, lw=2.0, alpha=0.55, zorder=2)

bs, as_ = np.polyfit(spr.log_dist, spr.coef, 1)
xs2 = np.linspace(spr.log_dist.min() - 0.15, spr.log_dist.max() + 0.15, 50)
ax.plot(xs2, as_ + bs * xs2, color=BLUE, lw=2.0, alpha=0.45, zorder=2)

ETIKETT = {'60': (-20, 14), '60H': (-22, -14), '100': (-20, 14), '100H': (0, -20),
           '110H': (24, 8), '200': (0, -20), '400': (-4, -21), '400H': (0, 14),
           '800': (0, -21), '1500': (-22, 12), 'MILE': (20, 2), '3000': (-6, 15),
           '3000S': (22, -12), '5000': (0, 15), '10000': (0, 15)}
for _, r in dose.iterrows():
    col = RED if r.treatment_group == 'distance_spikes' else BLUE
    dx, dy = ETIKETT.get(str(r.event), (0, 12))
    ax.annotate(NAVN.get(str(r.event), str(r.event)), xy=(r.log_dist, r.coef),
                xytext=(dx, dy), textcoords='offset points', fontsize=8.8,
                color=col, ha='center', va='center')

ticks = [60, 100, 200, 400, 800, 1500, 3000, 5000, 10000]
ax.set_xticks(np.log(ticks))
ax.set_xticklabels(['60', '100', '200', '400', '800', '1500', '3000', '5000', '10 000'])
ax.set_xlabel('Løpsdistanse i meter (logaritmisk skala)', color='#555555', fontsize=10)
ax.set_ylabel('Estimert løft etter skoskiftet (z-skår)', color='#555555', fontsize=10)
ax.set_ylim(0.10, 0.78)
ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
ax.set_yticklabels([komma(v, 1) for v in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]])
ax.tick_params(length=0)
ax.legend(loc='upper left', frameon=False, fontsize=10.5, handletextpad=0.5)

tittel(fig, 'Effekten vokser med distansen',
       'Hver prikk er én øvelse målt mot de tekniske øvelsene. Loddrette streker er 95 % usikkerhet.')
fig.text(0.01, 0.02, 'Distanseøvelsene stiger jevnt med distansen; sprintøvelsene viser ingen tilsvarende sammenheng.',
         fontsize=9, color='#888888', ha='left')
fig.subplots_adjust(left=0.085, right=0.985, top=0.80, bottom=0.155)
fig.savefig(OUT / 'sko_fig2_dose.png', dpi=300)
plt.close(fig)

print('Skrev sko_fig1_trend.png og sko_fig2_dose.png til', OUT)
