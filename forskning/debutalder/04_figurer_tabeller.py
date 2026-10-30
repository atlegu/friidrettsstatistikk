"""
04_figurer_tabeller.py — A3 «Debutalder»: manusfigurer og -tabeller (engelsk).

Samme visuelle språk som A1/frafallsartikkelen. Kjøres etter 03.

Output:
  figures/fig1_debut_age_by_cohort.png     debutaldersfordeling per fødselskohort
  figures/fig2_senior_by_debut_age.png     seniorandel per debutalder (Wilson-KI)
  figures/fig3_retention_k.png             andel aktiv k år etter debut (figur 3 i trykk)
  tables/manus/table1_characteristics.csv
  tables/manus/table2_h1.csv  table3_h2_h3.csv  table4_robustness.csv
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

HERE = Path(__file__).parent
DATA = HERE / "data_private"
FIG = HERE / "figures"
TABM = HERE / "tables" / "manus"
MOD = HERE / "tables" / "modeller"
FIG.mkdir(exist_ok=True)
TABM.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GRONN, ROD, GRAA, BLAA = "#1b6e1b", "#b22222", "#666666", "#1f4e79"
plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titlesize": 13})


def fmt(or_, lo, hi, des=2):
    return f"{or_:.{des}f} ({lo:.{des}f}–{hi:.{des}f})"


def last():
    d = pd.read_csv(DATA / "analysedata.csv")
    prim = d[d["kohort_primar"] & d["debut_10_16"]].copy()
    return d, prim


def fig1(d):
    g = d[d["debut_10_16"]]
    ford = (g.groupby(["birth_year", "debut_alder"]).size().rename("n").reset_index()
            .pivot(index="birth_year", columns="debut_alder", values="n").fillna(0))
    andel = ford.div(ford.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    farger = plt.cm.viridis(np.linspace(0.1, 0.9, 7))
    bunn = np.zeros(len(andel))
    for i, da in enumerate(range(10, 17)):
        if da not in andel.columns:
            continue
        ax.bar(andel.index, andel[da], bottom=bunn, color=farger[i],
               label=f"Debut at {da}", width=0.75)
        bunn += andel[da].to_numpy()
    ax.set_xlabel("Birth cohort")
    ax.set_ylabel("Share of debutants (%)")
    ax.set_title("Competition debut age by birth cohort (debut ages 10–16)")
    ax.legend(ncol=4, frameon=False, fontsize=8.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    fig.savefig(FIG / "fig1_debut_age_by_cohort.png", bbox_inches="tight")
    plt.close(fig)


def fig2(prim):
    st = prim.groupby("debut_alder")["senior"].agg(["mean", "count", "sum"])
    lo, hi = proportion_confint(st["sum"], st["count"], method="wilson")
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.errorbar(st.index, st["mean"] * 100, yerr=[st["mean"] * 100 - lo * 100,
                hi * 100 - st["mean"] * 100], fmt="o-", color=BLAA, lw=2.4, ms=8,
                capsize=4)
    for x, (m, n) in zip(st.index, zip(st["mean"], st["count"])):
        ax.annotate(f"n={n:,}", (x, m * 100), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=8, color=GRAA)
    ax.set_xlabel("Age at first registered competition")
    ax.set_ylabel("Active as senior, age ≥ 20 (%)")
    ax.set_title("Senior conversion by competition debut age (born 2001–2005)")
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_senior_by_debut_age.png", bbox_inches="tight")
    plt.close(fig)


def fig3():
    rk = pd.read_csv(MOD / "retention_k.csv")
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    farger = plt.cm.viridis(np.linspace(0.1, 0.9, 7))
    for i, da in enumerate(range(10, 17)):
        g = rk[rk["debut_alder"] == da]
        if g.empty:
            continue
        ax.plot(g["k"], g["andel_aktiv"] * 100, marker="o", color=farger[i],
                lw=2, ms=5, label=f"Debut at {da}")
    ax.set_xlabel("Years since debut season")
    ax.set_ylabel("Still competing (%)")
    ax.set_title("Retention after debut, by debut age (born 2001–2005)")
    ax.legend(ncol=4, frameon=False, fontsize=8.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    fig.savefig(FIG / "fig3_retention_k.png", bbox_inches="tight")
    plt.close(fig)


def med_iqr(s):
    return f"{s.median():.0f} ({s.quantile(0.25):.0f}–{s.quantile(0.75):.0f})"


def tabeller(prim):
    grupper = [("Debut 10–11", prim[prim["debut_alder"].between(10, 11)]),
               ("Debut 12–13", prim[prim["debut_alder"].between(12, 13)]),
               ("Debut 14–16", prim[prim["debut_alder"].between(14, 16)])]
    rader = []

    def rad(navn, fn):
        rader.append({"Characteristic": navn, **{n: fn(g) for n, g in grupper}})

    rad("n", lambda g: f"{len(g):,}")
    rad("Female, %", lambda g: f"{(g['gender'] == 'F').mean() * 100:.1f}")
    rad("Exact birth date available, %", lambda g: f"{g['kvartal'].notna().mean() * 100:.1f}")
    rad("Born Q1, % of those with birth date",
        lambda g: f"{(g['kvartal'] == 1).sum() / max(g['kvartal'].notna().sum(), 1) * 100:.1f}")
    rad("Born Q4, % of those with birth date",
        lambda g: f"{(g['kvartal'] == 4).sum() / max(g['kvartal'].notna().sum(), 1) * 100:.1f}")
    rad("Competition days, debut season, median (IQR)", lambda g: med_iqr(g["vol_debutaar"]))
    rad("Career length, seasons, median (IQR)", lambda g: med_iqr(g["karriere_aar"]))
    rad("Debut season 2020–2021, %", lambda g: f"{g['covid_debut'].mean() * 100:.1f}")
    pd.DataFrame(rader).to_csv(TABM / "table1_characteristics.csv", index=False)

    h1 = pd.read_csv(MOD / "h1_debutalder.csv")
    ut = []
    for _, t in h1[h1["analyse"] == "H1_kategorisk"].iterrows():
        ut.append({"Term": t["variabel"].replace("debut_kat_", "Debut at "),
                   "OR (95% CI)": fmt(t["OR"], t["KI_lav"], t["KI_hoy"])})
    tr = h1[(h1["analyse"] == "H1_trend")].iloc[0]
    ut.append({"Term": "Linear trend, per +1 year of debut age",
               "OR (95% CI)": fmt(tr["OR"], tr["KI_lav"], tr["KI_hoy"], 3)})
    pd.DataFrame(ut).to_csv(TABM / "table2_h1.csv", index=False)

    cox = pd.read_csv(MOD / "h2_cox.csv")
    h3 = pd.read_csv(MOD / "h3_landmark.csv")
    ut = [{"Analysis": "Age-scale Cox, HR per +1 year of debut age",
           "Estimate": fmt(np.exp(cox.loc[cox['covariate'] == 'debut_alder', 'coef'].iloc[0]),
                           np.exp(cox.loc[cox['covariate'] == 'debut_alder',
                                          'coef lower 95%'].iloc[0]),
                           np.exp(cox.loc[cox['covariate'] == 'debut_alder',
                                          'coef upper 95%'].iloc[0]), 3)}]
    for merk, lab in [("H3_uten_volum", "Landmark at 17: OR per +1 year, unadjusted for volume"),
                      ("H3_med_volum", "Landmark at 17: OR per +1 year, adjusted for days at 16–17")]:
        t = h3[(h3["analyse"] == merk) & (h3["variabel"] == "debut_alder")].iloc[0]
        ut.append({"Analysis": lab, "Estimate": fmt(t["OR"], t["KI_lav"], t["KI_hoy"], 3)})
    pd.DataFrame(ut).to_csv(TABM / "table3_h2_h3.csv", index=False)

    rob = pd.read_csv(MOD / "robusthet.csv")
    ut = [{"Analysis": t["analyse"], "Term": t["variabel"], "n": f"{int(t['n']):,}",
           "Events": f"{int(t['hendelser']):,}",
           "OR (95% CI)": fmt(t["OR"], t["KI_lav"], t["KI_hoy"], 3)}
          for _, t in rob.iterrows() if t["variabel"] in ("debut_alder", "debut_x_kvartal")
          or t["variabel"].startswith("debut_kat_17")]
    pd.DataFrame(ut).to_csv(TABM / "table4_robustness.csv", index=False)


def main():
    d, prim = last()
    fig1(d)
    fig2(prim)
    fig3()
    tabeller(prim)
    logger.info(f"3 figurer i {FIG}/ (figur 4 lages i 05b_revisjon_r2.py), 4 tabeller i {TABM}/")


if __name__ == "__main__":
    main()
