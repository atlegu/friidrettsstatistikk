"""
02_deskriptiv.py - Deskriptive figurer for 13-14-årslekene 2012-2025.

Inn: data/lekene_2012_2025.csv (fra 01_uttrekk.py; `verdi` = sekunder/meter, tolket i felles.py)
Ut:  figures/fig1_deltakelse.png ... fig8_stav.png, tables/*.csv

Kappgang er utelatt (lite interessant for artikkelen). Stav har små felt (8-23 per
klasse og år) og får senket n-krav, glidende 3-årsvinduer for gjentakere og en egen
dybdefigur (fig 8).

Farge = kjønn (blå gutter, oransje jenter; palett validert), linjestil = klasse
(13 år stiplet, 14 år heltrukket). Tidsøvelser plottes med invertert y-akse slik
at "opp = bedre" gjelder i alle paneler.
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
FIG = HERE / "figures"; FIG.mkdir(exist_ok=True)
TAB = HERE / "tables"; TAB.mkdir(exist_ok=True)

# --- design tokens (dataviz reference palette, light mode) ---
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
COL = {"G": "#2a78d6", "J": "#eb6834"}
STYLE = {13: dict(ls="--", marker="o"), 14: dict(ls="-", marker="s")}
GROUPS = ["G13", "G14", "J13", "J14"]
LABEL = {"G13": "Gutter 13", "G14": "Gutter 14", "J13": "Jenter 13", "J14": "Jenter 14"}
YEARS = list(range(2012, 2026))
MIN_N = 10        # minste felt for median
MIN_N_TOPP = 20   # minste felt for 90. persentil (ellers = én-to utøvere)
MIN_N_STAV = 8    # stavfeltene er 8-23; egne regler i fig 3, 5 og 8

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "lines.linewidth": 2, "lines.markersize": 5.5, "legend.frameon": False,
})

SHARED = [("60m", "60 m", "time"), ("200m", "200 m", "time"), ("600m", "600 m", "time"),
          ("1500m", "1500 m", "time"), ("lengde", "Lengde", "distance"), ("hoyde", "Høyde", "height"),
          ("tresteg", "Tresteg", "distance"), ("stav", "Stav", "height")]

# Klassespesifikke familier: (panel-tittel, {gruppe: øvelseskode eller None})
FAMILIES = [
    ("Kule", {"G13": "kule_3kg", "G14": "kule_4kg", "J13": "kule_2kg", "J14": "kule_3kg"}),
    ("Spyd", {"G13": "spyd_400g", "G14": "spyd_600g", "J13": "spyd_400g", "J14": "spyd_400g"}),
    ("Diskos", {"G13": "diskos_750g", "G14": "diskos_1kg", "J13": "diskos_600g", "J14": "diskos_750g"}),
    ("Slegge", {"G13": "slegge_30kg_1195cm", "G14": "slegge_40kg/1195cm",
                "J13": "slegge_20kg/110cm", "J14": "slegge_30kg_1195cm"}),
    ("60 m hekk", {"G13": "60mh_76_2cm", "G14": None, "J13": "60mh_76_2cm", "J14": "60mh_76_2cm"}),
    ("80 m hekk", {"G13": None, "G14": "80mh_84cm", "J13": None, "J14": None}),
    ("200 m hekk", {"G13": "200mh_68cm", "G14": "200mh_76_2cm", "J13": "200mh_68cm", "J14": "200mh_76_2cm"}),
]
SPEC = {"kule_3kg": "3 kg", "kule_4kg": "4 kg", "kule_2kg": "2 kg", "spyd_400g": "400 g", "spyd_600g": "600 g",
        "diskos_750g": "750 g", "diskos_1kg": "1 kg", "diskos_600g": "600 g", "slegge_30kg_1195cm": "3 kg",
        "slegge_40kg/1195cm": "4 kg", "slegge_20kg/110cm": "2 kg", "60mh_76_2cm": "76,2 cm",
        "80mh_84cm": "84 cm", "200mh_68cm": "68 cm", "200mh_76_2cm": "76,2 cm"}


def load():
    d = pd.read_csv(HERE / "data" / "lekene_2012_2025.csv", low_memory=False, parse_dates=["dato"])
    n0 = len(d)
    d = d[~d["manuell"].fillna(False).astype(bool)].copy()
    d = d[d["verdi"].notna() & (d["verdi"] > 0)]
    logger.info(f"{len(d)} resultater ({n0 - len(d)} manuelle tider fjernet), {d.athlete_id.nunique()} utøvere")
    return d


# ---------- små hjelpere ----------

def covid_band(ax):
    ax.axvspan(2019.6, 2021.4, color=GRID, alpha=0.6, lw=0, zorder=0)


def style_year_axis(ax):
    ax.set_xticks([2012, 2015, 2018, 2021, 2024])
    ax.set_xlim(2011.5, 2025.5)


def header(fig, title, subtitle=None):
    """Tittel og undertittel med fast avstand i tommer; returnerer topp for tight_layout-rect."""
    h = fig.get_size_inches()[1]
    fig.suptitle(title, x=0.01, y=1 - 0.08 / h, ha="left", va="top", fontsize=12, color=INK, fontweight="bold")
    if subtitle:
        fig.text(0.01, 1 - 0.36 / h, subtitle, ha="left", va="top", fontsize=8, color=INK2)
        return 1 - 0.62 / h
    return 1 - 0.38 / h


def spread(vals: dict, gap):
    """Skyver direkte-etiketter fra hverandre (min. avstand `gap` i dataenheter), beholder tyngdepunktet."""
    keys = sorted(vals, key=vals.get)
    y = [vals[k] for k in keys]
    for i in range(1, len(y)):
        y[i] = max(y[i], y[i - 1] + gap)
    shift = (sum(y) - sum(vals.values())) / len(y)
    return {k: v - shift for k, v in zip(keys, y)}


def spec_line(codes):
    """Kompakt spesifikasjonslinje: '3 kg: G13, J14 · 4 kg: G14 · 2 kg: J13'."""
    by = {}
    for g, c in codes.items():
        if c:
            by.setdefault(SPEC[c], []).append(g)
    if len(by) == 1:
        (s, gs), = by.items()
        return f"{s} for alle klasser" if len(gs) == 4 else f"{s} ({', '.join(gs)})"
    return " · ".join(f"{s}: {', '.join(gs)}" for s, gs in by.items())


def unit(rtype):
    return {"time": "sekunder (opp = bedre)", "distance": "meter", "height": "meter"}[rtype]


def series(d, code, group, q, rtype, min_n=MIN_N):
    """Kvantil q ("beste q-andel") per år for gruppe; NaN der n < min_n."""
    sub = d[(d.ovelse == code) & (d.klasse_kjonn == group)]
    out = []
    for y in YEARS:
        v = sub.loc[sub.yr == y, "verdi"]
        if len(v) < min_n:
            out.append(np.nan); continue
        qq = (1 - q) if rtype == "time" else q   # for tider er "topp" den lave halen
        out.append(v.quantile(qq))
    return np.array(out)


def plot_group_lines(ax, d, codes, q, rtype, y_label, min_n=MIN_N):
    for g in GROUPS:
        code = codes[g] if isinstance(codes, dict) else codes
        if code is None:
            continue
        y = series(d, code, g, q, rtype, min_n)
        ax.plot(YEARS, y, color=COL[g[0]], label=LABEL[g], **STYLE[int(g[1:])])
    if rtype == "time":
        ax.invert_yaxis()
    ax.set_ylabel(y_label)
    covid_band(ax); style_year_axis(ax)


def bottom_legend(fig, ax, ncol=4):
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=ncol, bbox_to_anchor=(0.5, -0.01))


# ---------- figurer ----------

def fig_deltakelse(d):
    part = d.groupby(["yr", "klasse_kjonn"])["athlete_id"].nunique().unstack()
    part.to_csv(TAB / "deltakelse.csv")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for g in GROUPS:
        ax.plot(part.index, part[g], color=COL[g[0]], label=LABEL[g], **STYLE[int(g[1:])])
    pos = spread({g: part[g].iloc[-1] for g in GROUPS}, gap=9)
    for g in GROUPS:
        ax.text(2025.35, pos[g], LABEL[g], color=INK2, va="center", fontsize=8)
    covid_band(ax); style_year_axis(ax); ax.set_xlim(2011.5, 2027)
    ax.set_ylabel("Antall utøvere"); ax.set_ylim(0, None)
    ax.set_title("Deltakelse ved lekene 2012–2025, etter klasse og kjønn", loc="left", color=INK, fontweight="bold")
    ax.legend(loc="lower left", ncol=2)
    fig.tight_layout(); fig.savefig(FIG / "fig1_deltakelse.png", dpi=300); plt.close(fig)
    logger.info("lagret fig1_deltakelse.png")


def fig_shared(d, q, fname, title, min_n):
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.8))
    for ax, (code, name, rtype) in zip(axes.flat, SHARED):
        mn = min(min_n, MIN_N) if code == "stav" else min_n   # stav: små felt, ellers tomt panel
        plot_group_lines(ax, d, code, q, rtype, unit(rtype), mn)
        ax.set_title(name if code != "stav" or mn == min_n else f"{name} (n ≥ {mn})",
                     loc="left", color=INK, fontweight="bold")
    bottom_legend(fig, axes.flat[0])
    note = f"Punkt vises kun der n ≥ {min_n}"
    if min_n > MIN_N:
        note += f"; for stav n ≥ {MIN_N}, der 90. persentil tilsvarer de én til to beste"
    top = header(fig, title, f"Grått felt = covid-årene 2020–2021. {note}.")
    fig.tight_layout(rect=(0, 0.04, 1, top))
    fig.savefig(FIG / fname, dpi=300); plt.close(fig)
    logger.info(f"lagret {fname}")


def fig_families(d, q, fname, title):
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.8))
    for ax, (name, codes) in zip(axes.flat, FAMILIES):
        rtype = "time" if "hekk" in name else "distance"
        plot_group_lines(ax, d, codes, q, rtype, unit(rtype))
        ax.set_title(name, loc="left", color=INK, fontweight="bold", pad=16)
        ax.text(0, 1.02, spec_line(codes), transform=ax.transAxes, fontsize=7.5, color=INK2, va="bottom")
    for ax in axes.flat[len(FAMILIES):]:
        ax.axis("off")
    bottom_legend(fig, axes.flat[0])
    top = header(fig, title, "Redskap/hekkehøyde er konstant innen hver serie; nivåene mellom klasser "
                             "med ulik spesifikasjon er ikke sammenlignbare. Punkt vises kun der n ≥ 10.")
    fig.tight_layout(rect=(0, 0.04, 1, top))
    fig.savefig(FIG / fname, dpi=300); plt.close(fig)
    logger.info(f"lagret {fname}")


def fig_gjentakere(d):
    """Median forbedring 13->14 for samme utøver, samme øvelse (prosent), per overgangsår."""
    rows = []
    for code, name, rtype in SHARED:
        sub = d[d.ovelse == code][["athlete_id", "yr", "klasse", "sex", "verdi"]]
        a13 = sub[sub.klasse == 13].rename(columns={"verdi": "v13", "yr": "yr13"})
        a14 = sub[sub.klasse == 14].rename(columns={"verdi": "v14", "yr": "yr14"})
        m = a13.merge(a14, on=["athlete_id", "sex"])
        m = m[m.yr14 == m.yr13 + 1]
        if rtype == "time":
            m["forb"] = 100 * (m.v13 - m.v14) / m.v13      # % raskere
        else:
            m["forb"] = 100 * (m.v14 - m.v13) / m.v13      # % lenger/høyere
        vindu = 1 if code == "stav" else 0                 # stav: glidende 3-årsvindu (små felt)
        for sex in ["G", "J"]:
            ms = m[m.sex == sex]
            for yr in YEARS[1:]:
                grp = ms[ms.yr14.between(yr - vindu, yr + vindu)]
                if len(grp) >= MIN_N:
                    rows.append(dict(ovelse=name, yr=yr, sex=sex, n=len(grp), median_forb=grp.forb.median(),
                                     vindu=f"{2 * vindu + 1} år"))
    t = pd.DataFrame(rows); t.to_csv(TAB / "gjentakere_forbedring.csv", index=False)
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.8))
    for ax, (code, name, rtype) in zip(axes.flat, SHARED):
        for sex in ["G", "J"]:
            s = t[(t.ovelse == name) & (t.sex == sex)].set_index("yr").reindex(YEARS[1:])
            ax.plot(YEARS[1:], s.median_forb, color=COL[sex], marker="o",
                    label="Gutter" if sex == "G" else "Jenter")
        ax.axhline(0, color=AXIS, lw=1)
        covid_band(ax); style_year_axis(ax); ax.set_xlim(2012.5, 2025.5)
        ax.set_title(name if code != "stav" else f"{name} (glidende 3-årsvindu)",
                     loc="left", color=INK, fontweight="bold")
        ax.set_ylabel("% forbedring 13→14")
    bottom_legend(fig, axes.flat[0], ncol=2)
    top = header(fig, "Utviklingstakt: samme utøvers forbedring fra 13 til 14 år (median, %)",
                 "Utøvere som deltok i samme øvelse to år på rad; x-aksen er året som 14-åring. "
                 "Punkt kun der n ≥ 10; stav bruker overgangene i tre påfølgende år.")
    fig.tight_layout(rect=(0, 0.04, 1, top))
    fig.savefig(FIG / "fig5_gjentakere.png", dpi=300); plt.close(fig)
    logger.info("lagret fig5_gjentakere.png")


def fig_sammensetning(d):
    u = d.drop_duplicates(["athlete_id", "yr"]).copy()
    u["avvik"] = u["alder_aar"] - u["klasse"]
    age = u.groupby(["yr", "klasse_kjonn"])["avvik"].mean().unstack()
    # Forventet avvik hvis fødselsdagene var jevnt fordelt over året (stevnet holdes i august)
    u["forventet"] = u["dato"].dt.dayofyear / 365.25 - 0.5
    forv = u.groupby("yr")["forventet"].mean()
    q1 = u.groupby(["yr", "klasse_kjonn"])["fodt_kvartal"].apply(lambda s: 100 * (s == 1).mean()).unstack()
    age.assign(jevn_fordeling=forv).to_csv(TAB / "sammensetning_alder.csv"); q1.to_csv(TAB / "sammensetning_q1.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for g in GROUPS:
        axes[0].plot(age.index, age[g], color=COL[g[0]], label=LABEL[g], **STYLE[int(g[1:])])
        axes[1].plot(q1.index, q1[g], color=COL[g[0]], label=LABEL[g], **STYLE[int(g[1:])])
    axes[0].plot(forv.index, forv.values, color=MUTED, lw=1.2, ls=":", label="Forventet ved jevn fødselsfordeling")
    axes[0].set_ylabel("År over 13,0 / 14,0 (gjennomsnitt)")
    axes[0].set_title("Eksakt alder på stevnedagen, avvik fra klassealder", loc="left", color=INK, fontweight="bold")
    axes[1].set_ylabel("Andel født 1. kvartal (%)")
    axes[1].set_title("Relativ alder: andel født januar–mars", loc="left", color=INK, fontweight="bold")
    axes[1].axhline(25, color=AXIS, lw=1)
    axes[1].text(2025.3, 25.3, "25 % = jevn fordeling", color=MUTED, fontsize=7.5, va="bottom", ha="right")
    for ax in axes:
        covid_band(ax); style_year_axis(ax)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.01))
    top = header(fig, "Sammensetningen av feltet, 2012–2025")
    fig.tight_layout(rect=(0, 0.06, 1, top))
    fig.savefig(FIG / "fig6_sammensetning.png", dpi=300); plt.close(fig)
    logger.info("lagret fig6_sammensetning.png")


def fig_ovelser_per_utover(d):
    n = d.groupby(["yr", "klasse_kjonn", "athlete_id"]).size().reset_index(name="k")
    m = n.groupby(["yr", "klasse_kjonn"])["k"].mean().unstack()
    m.to_csv(TAB / "ovelser_per_utover.csv")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for g in GROUPS:
        ax.plot(m.index, m[g], color=COL[g[0]], label=LABEL[g], **STYLE[int(g[1:])])
    covid_band(ax); style_year_axis(ax); ax.set_ylim(0, None)
    ax.set_ylabel("Øvelser per utøver (gjennomsnitt)")
    ax.set_title("Hvor mange øvelser stiller hver utøver i?", loc="left", color=INK, fontweight="bold")
    ax.legend(ncol=2, loc="lower left")
    fig.tight_layout(); fig.savefig(FIG / "fig7_ovelser_per_utover.png", dpi=300); plt.close(fig)
    logger.info("lagret fig7_ovelser_per_utover.png")


def fig_stav(d):
    """Stav i dybden: feltene er 8-23, så medianen suppleres med beste fjerdedel og beste hopp,
    og antall utøvere per år står i panelet."""
    from matplotlib.lines import Line2D
    s = d[d.ovelse == "stav"]
    rows = []
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), sharey=True)
    for ax, g in zip(axes.flat, GROUPS):
        sub = s[s.klasse_kjonn == g]
        st = (sub.groupby("yr")["verdi"]
                 .agg(n="size", median="median", p75=lambda v: v.quantile(0.75), beste="max")
                 .reindex(YEARS))
        st["n"] = st["n"].fillna(0).astype(int)
        rows += [dict(gruppe=g, yr=y, **r) for y, r in st.round(3).iterrows()]
        ok = st["n"] >= MIN_N_STAV
        c = COL[g[0]]
        ax.plot(YEARS, st["median"].where(ok), color=c, ls="-", marker="o")
        ax.plot(YEARS, st["p75"].where(ok), color=c, ls="--", marker="s")
        ax.plot(YEARS, st["beste"], color=c, ls="none", marker="D", mfc=SURFACE, mew=1.5, ms=6)
        for y, k in zip(YEARS, st["n"]):
            ax.text(y, 0.015, str(k), transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=7, color=MUTED)
        ax.set_title(LABEL[g], loc="left", color=INK, fontweight="bold")
        covid_band(ax); style_year_axis(ax)
    lo = s.groupby(["yr", "klasse_kjonn"])["verdi"].median().min()
    axes.flat[0].set_ylim(lo - 0.45, s["verdi"].max() + 0.15)
    for ax in axes[:, 0]:
        ax.set_ylabel("meter")
    hs = [Line2D([], [], color=INK2, ls="-", marker="o"),
          Line2D([], [], color=INK2, ls="--", marker="s"),
          Line2D([], [], color=INK2, ls="none", marker="D", mfc=SURFACE, mew=1.5, ms=6)]
    fig.legend(hs, ["Median", "Beste fjerdedel (75. persentil)", "Beste hopp"],
               loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01))
    top = header(fig, "Stav i dybden: små felt krever flere mål enn medianen",
                 f"Linjer vises der n ≥ {MIN_N_STAV}; tallene nederst i hvert panel er antall utøvere per år. "
                 "Beste hopp er ett enkelt resultat og svinger deretter.")
    fig.tight_layout(rect=(0, 0.04, 1, top))
    fig.savefig(FIG / "fig8_stav.png", dpi=300); plt.close(fig)
    pd.DataFrame(rows).to_csv(TAB / "stav_per_aar.csv", index=False)
    logger.info("lagret fig8_stav.png")


# ---------- tabeller ----------

def alle_serier():
    """(kode, navn, resultattype, gruppe) for alle øvelser i figurene."""
    combos = [(code, name, rtype, g) for code, name, rtype in SHARED for g in GROUPS]
    for name, codes in FAMILIES:
        rtype = "time" if "hekk" in name else "distance"
        combos += [(c, f"{name} ({SPEC[c]})", rtype, g) for g, c in codes.items() if c]
    return combos


def tabell_kvantiler(d):
    rows = []
    for code, name, rtype, g in alle_serier():
        sub = d[(d.ovelse == code) & (d.klasse_kjonn == g)]
        n = sub.groupby("yr").size().reindex(YEARS, fill_value=0)
        med = series(d, code, g, 0.5, rtype, MIN_N)
        p75 = series(d, code, g, 0.75, rtype, MIN_N)
        p90 = series(d, code, g, 0.9, rtype, MIN_N if code == "stav" else MIN_N_TOPP)
        for yr, k, a, b, c in zip(YEARS, n, med, p75, p90):
            rows.append(dict(ovelse=name, kode=code, gruppe=g, yr=yr, n=int(k),
                             median=None if np.isnan(a) else round(a, 3),
                             p75=None if np.isnan(b) else round(b, 3),
                             p90=None if np.isnan(c) else round(c, 3)))
    pd.DataFrame(rows).to_csv(TAB / "kvantiler_per_aar.csv", index=False)


def main():
    d = load()
    fig_deltakelse(d)
    fig_shared(d, 0.5, "fig2_median_fellesovelser.png",
               "Bredden: medianresultat per år i øvelser alle fire klasser konkurrerer i", MIN_N)
    fig_shared(d, 0.9, "fig3_p90_fellesovelser.png",
               "Toppen: beste 10 % (90. persentil) per år i de samme øvelsene", MIN_N_TOPP)
    fig_families(d, 0.5, "fig4_median_klassespesifikke.png",
                 "Bredden i klassespesifikke øvelser (kast og hekk): median per år")
    fig_gjentakere(d)
    fig_sammensetning(d)
    fig_ovelser_per_utover(d)
    fig_stav(d)
    tabell_kvantiler(d)
    logger.info("ferdig")


if __name__ == "__main__":
    main()
