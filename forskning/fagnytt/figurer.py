#!/usr/bin/env python3
"""Figurer og tabell til hovedartikkelen i Fagnytt.

Leser ferdige datafiler (ingen databasetilgang nødvendig):
  - DrPhilos/utvikling/data/season_bests*.csv  (JSAMS-artikkelen)
  - forskning/RAE/analyser/rae_per_age.csv     (RAE-artikkelen)
  - tall fra frafallsartiklene (Table 2 / resultattekst, hardkodet med kilde)
  - ferdige figurer fra analyse/trenerartikkel/output/ (kopieres)

    ../../scraper/venv/bin/python figurer.py
"""
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = Path(__file__).resolve().parent
OUT = HERE / 'figurer'
ROOT = HERE.parents[1]                      # Statistikk/
UTV = ROOT.parent / 'DrPhilos' / 'utvikling' / 'data'
RAE = ROOT / 'forskning' / 'RAE' / 'analyser' / 'rae_per_age.csv'
TREN = ROOT / 'analyse' / 'trenerartikkel' / 'output'

BLUE, ORANGE, GRAY, DARK, GREEN, RED = '#1f4e79', '#d9480f', '#b0b7bf', '#2b2b2b', '#2b8a3e', '#c92a2a'
plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.spines.left': False,
    'axes.grid': True, 'axes.grid.axis': 'y', 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8,
    'axes.axisbelow': True, 'axes.titlesize': 15, 'axes.titleweight': 'bold',
    'axes.titlelocation': 'left', 'axes.titlepad': 14,
    'xtick.color': DARK, 'ytick.color': DARK, 'axes.edgecolor': '#cccccc', 'figure.facecolor': 'white',
})


def no_num(x, dec=0):
    return f"{x:,.{dec}f}".replace(',', ' ').replace('.', ',')


def tittel(fig, hoved, under):
    fig.text(0.01, 0.985, hoved, fontsize=16, fontweight='bold', va='top', ha='left', color=DARK)
    fig.text(0.01, 0.935, under, fontsize=11, va='top', ha='left', color='#666666')


# ---------------------------------------------------------------- utviklingsdata (JSAMS)
EV = {'60m': ('time', '60 m', 10), '800m': ('time', '800 m', 13),
      'hoyde': ('field', 'Høyde', 10), 'lengde': ('field', 'Lengde', 10)}
RNG = np.random.default_rng(42)

modern = pd.read_csv(UTV / 'season_bests.csv')
modern = modern[(modern.age >= 10) & (modern.age <= 25) & (modern.season.between(2011, 2025))]
allt = pd.read_csv(UTV / 'season_bests_alltime.csv')
allt = allt[(allt.age >= 10) & (allt.age <= 25) & (allt.season <= 2025)]
# lengde 13 år: overgang sone -> planke, upålitelig punkt (som i artikkelen)
modern = modern[~((modern.event == 'lengde') & (modern.age == 13))]
allt = allt[~((allt.event == 'lengde') & (allt.age == 13))]


def cs_curve(df, ev, is_time, n=100):
    e = df[df.event == ev]; out = []
    for (g, a), grp in e.groupby(['gender', 'age']):
        v = np.sort(grp.season_best.values)
        top = v[:min(n, len(v))] if is_time else v[-min(n, len(v)):]
        out.append({'gender': g, 'age': a, 'mean': top.mean(), 'n': len(top)})
    return pd.DataFrame(out)


def panel_curve(df, ev):
    e = df[df.event == ev]; sp = e.groupby('athlete_id').age.nunique(); ids = sp[sp >= 3].index
    p = e[e.athlete_id.isin(ids)]; out = []
    for (g, a), grp in p.groupby(['gender', 'age']):
        v = grp.season_best.values
        out.append({'gender': g, 'age': a, 'mean': v.mean(), 'n': len(v)})
    return pd.DataFrame(out)


def pct(ages, vals, base, is_time):
    bv = vals[ages == base][0]
    return (bv - vals) / bv * 100 if is_time else (vals - bv) / bv * 100


curves = {}
for ev, (typ, lab, ba) in EV.items():
    is_time = typ == 'time'
    cs = cs_curve(allt, ev, is_time); pn = panel_curve(modern, ev)
    for g in ['M', 'F']:
        t = cs[(cs.gender == g) & (cs.n >= 50) & (cs.age >= ba)].sort_values('age')
        p = pn[(pn.gender == g) & (pn.age >= ba)].sort_values('age')
        curves[(ev, g)] = {
            'cs_age': t.age.values, 'cs_pct': pct(t.age.values, t['mean'].values, ba, is_time),
            'p_age': p.age.values, 'p_pct': pct(p.age.values, p['mean'].values, ba, is_time),
            'p_mean': p['mean'].values, 'p_n': p.n.values, 'is_time': is_time, 'base': ba,
        }

# ---- Figur 1: panel vs tverrsnitt, høyde og lengde
fig, axes = plt.subplots(2, 2, figsize=(11, 8.2), sharex=True)
for r, ev in enumerate(['hoyde', 'lengde']):
    for c, g in enumerate(['M', 'F']):
        ax = axes[r, c]; d = curves[(ev, g)]
        ax.plot(d['cs_age'], d['cs_pct'], 'o-', color=GRAY, lw=2.2, ms=4, label='Topp-100 per alder (tverrsnitt)')
        ax.plot(d['p_age'], d['p_pct'], 's-', color=BLUE if g == 'M' else ORANGE, lw=2.6, ms=4,
                label='Samme utøvere fulgt over tid (panel)')
        ax.set_title(f"{EV[ev][1]}, {'gutter/menn' if g == 'M' else 'jenter/kvinner'}", fontsize=12.5, pad=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} %"))
        ax.set_xticks(range(10, 26, 3))
        ax.axvline(18, color='#dddddd', lw=1, ls='--')
        last_cs = d['cs_pct'][-1]; last_p = d['p_pct'][-1]
        ax.annotate(f"{last_p:.0f} %", (d['p_age'][-1], last_p), xytext=(5, 0), textcoords='offset points',
                    color=BLUE if g == 'M' else ORANGE, fontweight='bold', va='center', fontsize=10)
        ax.annotate(f"{last_cs:.0f} %", (d['cs_age'][-1], last_cs), xytext=(5, 0), textcoords='offset points',
                    color='#888888', fontweight='bold', va='center', fontsize=10)
        if r == 1: ax.set_xlabel('Alder')
axes[0, 0].legend(loc='upper left', frameon=False, fontsize=9.5)
tittel(fig, 'Utviklingen stopper ikke ved 18',
       'Fremgang i prosent fra 10 år. Grå: de 100 beste ved hver alder (ulike utøvere). Farget: samme utøvere fulgt over tid.')
fig.tight_layout(rect=(0, 0, 1, 0.91))
fig.savefig(OUT / 'fig1_utvikling.png', dpi=200); plt.close(fig)

# ---- Figur 2: kjønnsforskjell per alder (panel)
fig, ax = plt.subplots(figsize=(10, 5.6))
farger = {'60m': BLUE, '800m': GREEN, 'hoyde': ORANGE, 'lengde': RED}
for ev, (typ, lab, ba) in EV.items():
    m = curves[(ev, 'M')]; f = curves[(ev, 'F')]
    ages = sorted(set(m['p_age']) & set(f['p_age']))
    gap = []
    for a in ages:
        mv = m['p_mean'][list(m['p_age']).index(a)]; fv = f['p_mean'][list(f['p_age']).index(a)]
        gap.append((fv - mv) / fv * 100 if m['is_time'] else (mv - fv) / fv * 100)
    ax.plot(ages, gap, 'o-', color=farger[ev], lw=2.4, ms=4, label=lab)
    ax.annotate(lab, (ages[-1], gap[-1]), xytext=(6, 0), textcoords='offset points', color=farger[ev],
                fontweight='bold', va='center')
ax.axvspan(12.5, 14.5, color='#f3f3f3', zorder=0)
ax.text(13.5, ax.get_ylim()[1] * 0.97, 'Skillet\nåpner seg', ha='center', va='top', color='#777777', fontsize=9.5)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.set_xticks(range(10, 26, 1)); ax.set_xlabel('Alder'); ax.set_xlim(9.5, 27)
tittel(fig, 'Like til 12, adskilt fra 14', 'Guttenes forsprang på jentene i prosent, samme utøvere fulgt over tid.')
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(OUT / 'fig2_kjonn.png', dpi=200); plt.close(fig)

# ---- Tabell: forventet fremgang (kumulativ, panel) ved utvalgte aldre
aldre = [12, 14, 16, 18, 20, 22, 25]
rows = []
for ev, (typ, lab, ba) in EV.items():
    for g in ['M', 'F']:
        d = curves[(ev, g)]; cells = []
        for a in aldre:
            if a in list(d['p_age']):
                i = list(d['p_age']).index(a); cells.append(f"{d['p_pct'][i]:.0f} %")
            else:
                cells.append('–')
        rows.append([lab, 'Gutter/menn' if g == 'M' else 'Jenter/kvinner'] + cells)
hdr = '| Øvelse | Kjønn | ' + ' | '.join(f"{a} år" for a in aldre) + ' |\n'
hdr += '|---|---|' + '---|' * len(aldre) + '\n'
body = ''.join('| ' + ' | '.join(r) + ' |\n' for r in rows)
(OUT / 'tabell_fremgang.md').write_text(hdr + body, encoding='utf-8')

# Årlig fremgang per aldersintervall (til tekst)
lines = []
for ev, (typ, lab, ba) in EV.items():
    for g in ['M', 'F']:
        d = curves[(ev, g)]; ages = list(d['p_age']); vals = d['p_mean']
        segs = []
        for a0, a1 in [(ba, 14), (14, 16), (16, 18), (18, 21), (21, 25)]:
            if a0 in ages and a1 in ages:
                v0, v1 = vals[ages.index(a0)], vals[ages.index(a1)]
                tot = (v0 - v1) / v0 * 100 if d['is_time'] else (v1 - v0) / v0 * 100
                segs.append(f"{a0}–{a1}: {tot / (a1 - a0):.1f} %/år")
        lines.append(f"{lab} {g}: " + '; '.join(segs))
(OUT / 'aarlig_fremgang.txt').write_text('\n'.join(lines), encoding='utf-8')

# ---- Figur 3: RAE per alder
r = pd.read_csv(RAE); r = r[r.age <= 25]
fig, ax = plt.subplots(figsize=(10, 5.4))
x = np.arange(len(r)); w = 0.38
ax.bar(x - w / 2, r.Q1_pct, w, color=BLUE, label='Født januar–mars')
ax.bar(x + w / 2, r.Q4_pct, w, color=ORANGE, label='Født oktober–desember')
ax.axhline(24.6, color=BLUE, lw=1.2, ls='--'); ax.axhline(22.9, color=ORANGE, lw=1.2, ls='--')
ax.text(-0.55, 24.9, 'Befolkningen: 24,6 %', color=BLUE, fontsize=9, ha='left', va='bottom',
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.9))
ax.text(-0.55, 22.6, 'Befolkningen: 22,9 %', color=ORANGE, fontsize=9, ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.9))
ax.set_xticks(x); ax.set_xticklabels(r.age.astype(int)); ax.set_xlabel('Alder')
ax.set_ylim(0, 34); ax.set_xlim(-0.7, len(r) - 0.3); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.legend(loc='upper left', frameon=False, ncol=2)
tittel(fig, 'Skjevheten er der allerede hos 10-åringene',
       'Andel av alle konkurrerende utøvere ved hver alder som er født i første og fjerde kvartal, 2011–2026.')
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(OUT / 'fig3_rae.png', dpi=200); plt.close(fig)

# ---- Figur 4: konkurransevolum, blir vs slutter (Table 2 i «Pulling back before dropout»)
ages = [13, 14, 15, 16, 17, 18]
blir = [13, 17, 19, 18, 17, 14]      # median stevner per år, aktive som senior (n=348)
slutter = [8, 8, 3, 0, 0, 0]         # median, sluttet før 20 år (n=1 775)
fig, ax = plt.subplots(figsize=(10, 5.4))
ax.plot(ages, blir, 'o-', color=GREEN, lw=3, ms=7, label='Fortsatt aktive som seniorer (n = 348)')
ax.plot(ages, slutter, 'o-', color=RED, lw=3, ms=7, label='Sluttet før 20 år (n = 1 775)')
ax.axvspan(14.5, 16.5, color='#f3f3f3', zorder=0)
ax.text(15.5, 20.3, 'UM-kvalifisering', ha='center', color='#777777', fontsize=9.5)
for a, v in zip(ages, blir): ax.annotate(str(v), (a, v), xytext=(0, 8), textcoords='offset points', ha='center', color=GREEN, fontsize=9.5, fontweight='bold')
for a, v in zip(ages, slutter): ax.annotate(str(v), (a, v), xytext=(0, -14), textcoords='offset points', ha='center', color=RED, fontsize=9.5, fontweight='bold')
ax.set_xticks(ages); ax.set_xlabel('Alder'); ax.set_ylim(-2, 22)
ax.set_ylabel('Stevner per år (median)')
ax.legend(loc='upper right', frameon=False)
tittel(fig, 'De som slutter, trekker seg tilbake først',
       'Antall stevner per år for 13–14-åringer fra ungdomslekene 2011–2016, etter om de var aktive som seniorer.')
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(OUT / 'fig4_volum.png', dpi=200); plt.close(fig)

# ---- Figur 5: UM-status ved 15–16 og andel aktive fem år senere (SJMSS-manus, resultatdel)
grupper = ['Kvalifisert\nog deltok', 'Kvalifisert,\ndeltok ikke', 'Bommet med\nunder 2 %',
           'Bommet med\n2–5 %', 'Bommet med\n5–15 %', 'Bommet med\nover 15 %']
andel = [41.6, 16.4, 16.1, 8.7, 4.4, 5.6]
n = [527, 75, 65, 86, None, None]
farg = [GREEN, RED, ORANGE, GRAY, GRAY, GRAY]
fig, ax = plt.subplots(figsize=(10, 5.4))
b = ax.bar(grupper, andel, color=farg, width=0.62)
for rect, v in zip(b, andel):
    ax.annotate(f"{no_num(v, 1)} %", (rect.get_x() + rect.get_width() / 2, v), xytext=(0, 5),
                textcoords='offset points', ha='center', fontweight='bold', color=DARK)
ax.set_ylim(0, 50); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.set_ylabel('Fortsatt aktive fem år etter 16-årssesongen')
tittel(fig, 'Å klare kravet hjelper lite hvis du ikke drar',
       'Status ved UM-kvalifisering som 15–16-åring og andel som fortsatt konkurrerte fem år senere (n = 882).')
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(OUT / 'fig5_um.png', dpi=200); plt.close(fig)

# ---- Kopier ferdige figurer fra trenerartikkelen
shutil.copy(TREN / 'figM2_frafall.png', OUT / 'fig6_frafall.png')
shutil.copy(TREN / 'figM5_kule_g15.png', OUT / 'fig7_kule.png')
shutil.copy(TREN / 'figM8_arvtakere.png', OUT / 'fig8_arvtakere.png')
print('Skrev figurer til', OUT)
print((OUT / 'tabell_fremgang.md').read_text())
print((OUT / 'aarlig_fremgang.txt').read_text())


# =====================================================================
# Spaltebrede versjoner (magasinmal i to spalter, ca. 83 mm bred spalte)
# =====================================================================
import textwrap

S_W, S_H = 5.4, 4.5


def tittel_s(fig, hoved, under):
    fig.text(0.01, 0.985, hoved, fontsize=13, fontweight='bold', va='top', ha='left', color=DARK)
    fig.text(0.01, 0.925, '\n'.join(textwrap.wrap(under, 62)), fontsize=8.6, va='top', ha='left', color='#666666')


plt.rcParams.update({'font.size': 9.5})

# fig3s: RAE, færre aldre for lesbarhet
r = pd.read_csv(RAE); r = r[r.age.isin([10, 12, 14, 16, 18, 20, 22, 25])]
fig, ax = plt.subplots(figsize=(S_W, S_H))
x = np.arange(len(r)); w = 0.38
ax.bar(x - w / 2, r.Q1_pct, w, color=BLUE, label='Født januar–mars')
ax.bar(x + w / 2, r.Q4_pct, w, color=ORANGE, label='Født oktober–desember')
ax.axhline(24.6, color=BLUE, lw=1, ls='--'); ax.axhline(22.9, color=ORANGE, lw=1, ls='--')
ax.text(len(r) - 0.5, 24.9, 'Befolkningen 24,6 %', color=BLUE, fontsize=7.5, ha='right', va='bottom',
        bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.9))
ax.text(len(r) - 0.5, 22.6, 'Befolkningen 22,9 %', color=ORANGE, fontsize=7.5, ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.9))
ax.set_xticks(x); ax.set_xticklabels(r.age.astype(int)); ax.set_xlabel('Alder')
ax.set_ylim(0, 34); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.legend(loc='upper left', frameon=False, fontsize=8, ncol=2, handlelength=1.2)
tittel_s(fig, 'Skjevheten er der allerede hos 10-åringene',
         'Andel av alle konkurrerende utøvere ved hver alder som er født i første og fjerde kvartal, 2011–2026.')
fig.tight_layout(rect=(0, 0, 1, 0.87)); fig.savefig(OUT / 'fig3s_rae.png', dpi=220); plt.close(fig)

# fig4s: konkurransevolum
fig, ax = plt.subplots(figsize=(S_W, S_H))
ax.plot(ages, blir, 'o-', color=GREEN, lw=2.6, ms=6, label='Aktive som seniorer (n = 348)')
ax.plot(ages, slutter, 'o-', color=RED, lw=2.6, ms=6, label='Sluttet før 20 år (n = 1 775)')
ax.axvspan(14.5, 16.5, color='#f3f3f3', zorder=0)
ax.text(15.5, 21.2, 'UM-kvalifisering', ha='center', color='#777777', fontsize=8)
for a, v in zip(ages, blir): ax.annotate(str(v), (a, v), xytext=(0, 7), textcoords='offset points', ha='center', color=GREEN, fontsize=8.5, fontweight='bold')
for a, v in zip(ages, slutter): ax.annotate(str(v), (a, v), xytext=(0, -13), textcoords='offset points', ha='center', color=RED, fontsize=8.5, fontweight='bold')
ax.set_xticks(ages); ax.set_xlabel('Alder'); ax.set_ylim(-2.5, 23.5); ax.set_ylabel('Stevner per år (median)')
ax.legend(loc='lower left', frameon=False, fontsize=8)
tittel_s(fig, 'De som slutter, trekker seg tilbake først',
         'Stevner per år for 13–14-åringer fra ungdomslekene 2011–2016, etter om de var aktive som seniorer.')
fig.tight_layout(rect=(0, 0, 1, 0.87)); fig.savefig(OUT / 'fig4s_volum.png', dpi=220); plt.close(fig)

# fig5s: UM-status
grupper_s = ['Kvalifisert,\ndeltok', 'Kvalifisert,\ndeltok ikke', 'Bommet\n< 2 %', 'Bommet\n2–5 %', 'Bommet\n5–15 %', 'Bommet\n> 15 %']
fig, ax = plt.subplots(figsize=(S_W, S_H))
b = ax.bar(grupper_s, andel, color=farg, width=0.64)
for rect, v in zip(b, andel):
    ax.annotate(f"{no_num(v, 1)} %", (rect.get_x() + rect.get_width() / 2, v), xytext=(0, 4),
                textcoords='offset points', ha='center', fontweight='bold', color=DARK, fontsize=8.5)
ax.set_ylim(0, 50); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} %"))
ax.tick_params(axis='x', labelsize=8)
ax.set_ylabel('Fortsatt aktive fem år etter 16-årssesongen', fontsize=8.5)
tittel_s(fig, 'Å klare kravet hjelper lite hvis du ikke drar',
         'Status ved UM-kvalifisering som 15–16-åring og andel som fortsatt konkurrerte fem år senere (n = 882).')
fig.tight_layout(rect=(0, 0, 1, 0.87)); fig.savefig(OUT / 'fig5s_um.png', dpi=220); plt.close(fig)

# fig6s: frafall ti kohorter
fr = pd.read_csv(TREN / 'frafall_kohorter.csv')
fr = fr.groupby(['cohort_year', 'age'], as_index=False).n_active.sum()
fig, ax = plt.subplots(figsize=(S_W, S_H))
for c, g in fr.groupby('cohort_year'):
    g = g.sort_values('age'); base = g[g.age == 13].n_active.values[0]
    pct = g.n_active / base * 100
    farge, lw, z = ('#c9ced4', 1.4, 1)
    if c == 2013: farge, lw, z = (BLUE, 2.6, 3)
    if c == 2019: farge, lw, z = (ORANGE, 2.6, 3)
    if c == 2022: farge, lw, z = (GREEN, 2.6, 3)
    ax.plot(g.age, pct, '-', color=farge, lw=lw, zorder=z, marker='o' if lw > 2 else None, ms=4)
    if lw > 2:
        ax.annotate(f"{c}-kullet", (g.age.values[-1], pct.values[-1]), xytext=(5, 0), textcoords='offset points',
                    color=farge, fontweight='bold', va='center', fontsize=8.5)
ax.set_ylim(0, 105); ax.set_xlim(12.8, 20.6); ax.set_xticks(range(13, 20))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} %")); ax.set_xlabel('Alder')
tittel_s(fig, 'Frafallet er som før',
         'Andel av 13-åringene som fortsatt konkurrerer ved hver alder. Ti årskull, nesten samme kurve.')
fig.tight_layout(rect=(0, 0, 1, 0.87)); fig.savefig(OUT / 'fig6s_frafall.png', dpi=220); plt.close(fig)

# fig7s: kule G15
ku = pd.read_csv(TREN / 'kast_hekk_aldersklasser.csv')
ku = ku[(ku.family == 'Kule') & (ku.age_class == '15 år') & (ku.gender == 'M')].sort_values('yr')
fig, ax = plt.subplots(figsize=(S_W, S_H))
ax.plot(ku.yr, ku.top10_avg_fmt, 'o-', color=RED, lw=2.6, ms=6, mfc='white', mew=2)
ax.annotate(f"{no_num(ku.top10_avg_fmt.iloc[0], 2)} m", (ku.yr.iloc[0], ku.top10_avg_fmt.iloc[0]), xytext=(-2, 9),
            textcoords='offset points', color=RED, fontweight='bold', fontsize=9)
ax.annotate(f"{no_num(ku.top10_avg_fmt.iloc[-1], 2)} m", (ku.yr.iloc[-1], ku.top10_avg_fmt.iloc[-1]), xytext=(-30, 9),
            textcoords='offset points', color=RED, fontweight='bold', fontsize=9)
ax.set_ylim(10, 16); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f} m"))
ax.set_xticks(range(2013, 2026, 2))
tittel_s(fig, 'Samme kule, to meter kortere', 'Snittet av de ti beste 15-årige guttene i kule (4 kg), utendørs, 2013–2025.')
fig.tight_layout(rect=(0, 0, 1, 0.87)); fig.savefig(OUT / 'fig7s_kule.png', dpi=220); plt.close(fig)
print('spaltefigurer OK')
