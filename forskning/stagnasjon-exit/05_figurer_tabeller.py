"""
05_figurer_tabeller.py — A1 «Stagnasjon før exit»: manusfigurer og -tabeller.

Kjøres ETTER 03/04 (leser modelltabellene). Engelske etiketter (manus til
Sports Medicine - Open); visuell stil som frafallsartikkelens figurer
(grønn = retainers, rød = dropouts, IQR-skygge, n i bunnforklaringen).

Output:
  figures/fig1_performance_by_age.png      medianprestasjon per alder, retainers mot dropouts
  figures/fig2_exit_aligned.png            within-utøver endring T-3..T0 (prestasjon og volum)
  figures/fig3_retention_by_progression.png  seniorandel per fremgangskvintil x volumtertil
  figures/fig4_km_progression.png          Kaplan-Meier per fremgangstertil
  tables/manus/table1_characteristics.csv  baseline/landmark-karakteristika etter utfall
  tables/manus/table2_models.csv           hovedmodeller (OR, AUC, kalibrering)
  tables/manus/table3_h2_h3.csv            interaksjon, strata og H3
  tables/manus/table4_robustness.csv       robusthetsanalysene, formatert
  tables/manus/tableS_cox.csv              landmark-Cox
"""

import json
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter

HERE = Path(__file__).parent
DATA = HERE / "data_private"
FIG = HERE / "figures"
TABM = HERE / "tables" / "manus"
FIG.mkdir(exist_ok=True)
TABM.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE.parent))
from a1_tyrving import beregn_tyrving_poeng, parse_tyrving_xls  # noqa: E402
from rens_felles import fjern_kopier  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GRONN, ROD, GRAA = "#1b6e1b", "#b22222", "#666666"
RNG = np.random.default_rng(20261029)
plt.rcParams.update({"figure.dpi": 300, "savefig.dpi": 300, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.titlesize": 13})


def mean3(p):
    return float(np.mean(sorted(p, reverse=True)[:3])) if len(p) else np.nan


def fmt(or_, lo, hi, des=2):
    return f"{or_:.{des}f} ({lo:.{des}f}–{hi:.{des}f})"


def boot_median_ci(x, n=2000):
    x = np.asarray(x)
    med = np.median(x)
    boots = [np.median(RNG.choice(x, size=len(x), replace=True)) for _ in range(n)]
    return med, np.percentile(boots, 2.5), np.percentile(boots, 97.5)


def last_grunnlag():
    base = pd.read_csv(DATA / "analysedata.csv")
    base["prim"] = base["kohort_primar"] & base["skaarbar"] & ~base["liten_gruppecelle"]
    base["aktiv_naa"] = (base["birth_year"] + base["siste_alder"]) >= 2025

    r = pd.read_csv(DATA / "resultater.csv", parse_dates=["date"], low_memory=False)
    r, _ = fjern_kopier(r)
    r = r.drop(columns=["birth_year"], errors="ignore").merge(
        base[["athlete_id", "birth_year", "gender", "hovedgruppe"]], on="athlete_id", how="inner")
    r["alder"] = r["date"].dt.year - r["birth_year"]
    r = r[(r["status"] == "OK") & r["alder"].between(13, 19)].copy()
    r["manuell"] = r["is_manual_time"].astype(str) == "True"

    # sesongverdier: konkurransedager (alle øvelser) og mean3 Tyrving i hovedgruppen
    dager = (r.groupby(["athlete_id", "alder"])["date"].nunique()
             .rename("dager").reset_index())
    sc = r[~r["manuell"] & (r["event_category"] == r["hovedgruppe"])].copy()
    tab = parse_tyrving_xls()
    sc["tyrving"] = [beregn_tyrving_poeng(pv, kode, rt, kj, al, tab)
                     for pv, kode, rt, kj, al in zip(sc["performance_value"], sc["event_code"],
                                                     sc["result_type"], sc["gender"], sc["alder"])]
    sc = sc[sc["tyrving"].notna()]
    ty = (sc.groupby(["athlete_id", "alder"])["tyrving"].agg(list).map(mean3)
          .rename("tyrving_m3").reset_index())
    sesong = dager.merge(ty, on=["athlete_id", "alder"], how="left")
    return base, sesong


# ---------------------------------------------------------------------------- figur 1
def fig1(base, sesong):
    prim = base[base["prim"]]
    s = sesong.merge(prim[["athlete_id", "senior"]], on="athlete_id", how="inner")
    s = s[s["tyrving_m3"].notna() & s["alder"].between(13, 18)]
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    figdata = []
    for verdi, farge, mark, navn in [(1, GRONN, "o", "Active seniors (≥2 results in a year at ≥20)"),
                                     (0, ROD, "s", "Not active seniors")]:
        g = s[s["senior"] == verdi]
        st = g.groupby("alder")["tyrving_m3"].agg(
            median="median", q1=lambda x: x.quantile(0.25), q3=lambda x: x.quantile(0.75))
        figdata.append(st.assign(senior=verdi,
                                 n=g.groupby("alder")["athlete_id"].nunique()).reset_index())
        n0 = int(g.loc[g["alder"] == 13, "athlete_id"].nunique())
        ax.plot(st.index, st["median"], color=farge, marker=mark, lw=2.8, ms=8,
                label=f"{navn} (n = {n0:,} at 13)")
        ax.fill_between(st.index, st["q1"], st["q3"], color=farge, alpha=0.13)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Age-graded points in main event group\n(mean of 3 best; median, IQR shaded)")
    ax.set_title("Age-graded performance by age and senior-retention status")
    ax.text(0.015, 0.03, "Flat = keeping pace with age norms; athletes competing in the main group that season",
            transform=ax.transAxes, fontsize=8.5, color=GRAA)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_performance_by_age.png", bbox_inches="tight")
    plt.close(fig)
    pd.concat(figdata).to_csv(TABM / "fig1_data.csv", index=False)


# ---------------------------------------------------------------------------- figur 2
def fig2(base, sesong):
    prim = base[base["prim"]]
    exits = prim[(~prim["aktiv_naa"]) & prim["siste_alder"].between(16, 19)]
    piv_t = sesong.pivot(index="athlete_id", columns="alder", values="tyrving_m3")
    piv_d = sesong.pivot(index="athlete_id", columns="alder", values="dager")

    rader_t, rader_d = [], []
    for _, u in exits.iterrows():
        aldre = [int(u["siste_alder"]) - k for k in (3, 2, 1, 0)]
        if aldre[0] < 13 or u["athlete_id"] not in piv_t.index:
            continue
        tv = [piv_t.at[u["athlete_id"], a] if a in piv_t.columns else np.nan for a in aldre]
        dg = [piv_d.at[u["athlete_id"], a] if a in piv_d.columns else np.nan for a in aldre]
        if not any(np.isnan(tv)):
            rader_t.append([tv[k] - tv[0] for k in range(4)])
        if not any(np.isnan(dg)):
            rader_d.append([dg[k] - dg[0] for k in range(4)])
    T = np.array(rader_t)
    D = np.array(rader_d)

    fig, akser = plt.subplots(1, 2, figsize=(10.5, 4.8), sharex=True)
    figdata = []
    for ax, M, navn, enhet in [(akser[0], T, "Age-graded performance", "points vs. own level at T−3"),
                               (akser[1], D, "Competition volume", "days vs. own level at T−3")]:
        med, lo, hi = zip(*[boot_median_ci(M[:, k]) for k in range(4)])
        figdata += [{"panel": navn, "t": f"T-{3 - k}", "median": med[k], "ki_lav": lo[k],
                     "ki_hoy": hi[k], "n": len(M), "n_kandidater": len(exits)} for k in range(4)]
        ax.axhline(0, color=GRAA, lw=1, ls="--")
        ax.plot(range(4), med, color=ROD, marker="s", lw=2.8, ms=8)
        ax.fill_between(range(4), lo, hi, color=ROD, alpha=0.18)
        ax.set_xticks(range(4), ["T−3", "T−2", "T−1", "T0\n(final season)"])
        ax.set_title(navn)
        ax.set_ylabel(f"Within-athlete change ({enhet})\nmedian, bootstrap 95% CI")
    fig.suptitle(f"The slide before exit: within-athlete change over the four last active seasons\n"
                 f"(dropouts with final season at ages 16–19; performance n = {len(T):,}, "
                 f"volume n = {len(D):,})", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_exit_aligned.png", bbox_inches="tight")
    plt.close(fig)
    pd.DataFrame(figdata).to_csv(TABM / "fig2_data.csv", index=False)
    return len(T), len(D)


# ---------------------------------------------------------------------------- figur 3
def fig3(base):
    p = base[base["prim"]].copy()
    p["kvintil"] = pd.qcut(p["delta_z"], 5, labels=[1, 2, 3, 4, 5])
    p["voltert"] = pd.qcut(p["vol1516"].rank(method="first"), 3,
                           labels=["Low volume 15–16", "Mid volume 15–16",
                                   "High volume 15–16"])
    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    farger = {"Low volume 15–16": ROD, "Mid volume 15–16": GRAA,
              "High volume 15–16": GRONN}
    figdata = []
    for navn, g in p.groupby("voltert", observed=True):
        andel = g.groupby("kvintil", observed=True)["senior"].mean() * 100
        ax.plot(andel.index.astype(int), andel.values, marker="o", lw=2.6, ms=7,
                color=farger[str(navn)], label=f"{navn} (n = {len(g):,})")
        figdata += [{"voltertil": str(navn), "kvintil": int(q), "andel_pst": a_,
                     "n_tertil": len(g), "vol_min": int(g["vol1516"].min()),
                     "vol_maks": int(g["vol1516"].max())} for q, a_ in andel.items()]
    pd.DataFrame(figdata).to_csv(TABM / "fig3_data.csv", index=False)
    ax.set_xlabel("Progression quintile, ages 13–14 → 15–16 (1 = largest decline)")
    ax.set_ylabel("Active as senior, age ≥ 20 (%)")
    ax.set_title("Senior retention by performance progression and competition volume")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_retention_by_progression.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------- figur 4
def fig4(base):
    p = base[base["prim"]].copy()
    p["tertil"] = pd.qcut(p["delta_z"], 3, labels=["Lowest progression tertile",
                                                   "Middle tertile", "Highest progression tertile"])
    p["tid"] = np.maximum(p["siste_alder"] - 16, 0.1)
    p["hendelse"] = (~p["aktiv_naa"]).astype(int)
    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    farger = [ROD, GRAA, GRONN]
    for (navn, g), farge in zip(p.groupby("tertil", observed=True), farger):
        KaplanMeierFitter().fit(g["tid"], g["hendelse"],
                                label=f"{navn} (n = {len(g):,})").plot_survival_function(
            ax=ax, color=farge, lw=2.4, ci_alpha=0.12)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Proportion still competing")
    ax.set_title("Continued participation after the landmark, by progression tertile")
    ticks = np.arange(0, 11, 2)
    ax.set_xticks(ticks, [str(int(t + 16)) for t in ticks])
    ax.legend(frameon=False, fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_km_progression.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------- tabeller
def med_iqr(s):
    return f"{s.median():.0f} ({s.quantile(0.25):.0f}–{s.quantile(0.75):.0f})"


def tabell1(base):
    p = base[base["prim"]]
    grupper = [("All", p), ("Senior retainers", p[p["senior"] == 1]),
               ("Future dropouts", p[p["senior"] == 0])]
    rader = []

    def rad(navn, fn):
        rader.append({"Characteristic": navn, **{n: fn(g) for n, g in grupper}})

    rad("n", lambda g: f"{len(g):,}")
    rad("Female, %", lambda g: f"{(g['gender'] == 'F').mean() * 100:.1f}")
    rad("Cohort A (born 1998–2001), %", lambda g: f"{(g['kohort'] == 'A').mean() * 100:.1f}")
    for gruppe in ["sprint", "jumps", "middle_distance", "throws"]:
        rad(f"Main event group: {gruppe.replace('_', ' ')}, %",
            lambda g, x=gruppe: f"{(g['hovedgruppe'] == x).mean() * 100:.1f}")
    rad("Born Q1, %", lambda g: f"{(g['kvartal'] == 1).mean() * 100:.1f}")
    rad("Born Q4, %", lambda g: f"{(g['kvartal'] == 4).mean() * 100:.1f}")
    rad("Competition days 13–14, median (IQR)", lambda g: med_iqr(g["vol1314"]))
    rad("Competition days 15–16, median (IQR)", lambda g: med_iqr(g["vol1516"]))
    rad("Scored results in main group 13–14 (k13), median (IQR)", lambda g: med_iqr(g["k13"]))
    rad("Scored results in main group 15–16 (k15), median (IQR)", lambda g: med_iqr(g["k15"]))
    rad("Age-graded points 13–14, median (IQR)", lambda g: med_iqr(g["niva_w1"]))
    rad("Age-graded points 15–16, median (IQR)", lambda g: med_iqr(g["niva_w2"]))
    rad("Progression, points, median (IQR)", lambda g: med_iqr(g["delta"]))
    pd.DataFrame(rader).to_csv(TABM / "table1_characteristics.csv", index=False)


def inverter(or_, lo, hi):
    return 1 / or_, 1 / hi, 1 / lo


def tabell2():
    m = pd.read_csv(HERE / "tables" / "modeller" / "h1_or.csv")
    auc = pd.read_csv(HERE / "tables" / "modeller" / "h1_auc.csv")
    kal = pd.read_csv(HERE / "tables" / "modeller" / "kalibrering.csv")
    navn = {"delta_z": "Progression 13–14 → 15–16, per SD",
            "niva_w1_z": "Performance level 13–14, per SD",
            "vol1314_g": "Competition days 13–14, per SD",
            "vol1516_g": "Competition days 15–16, per SD",
            "k13": "Scored results 13–14 (per result)",
            "k15": "Scored results 15–16 (per result)"}
    rader = []
    for var, lab in navn.items():
        rad = {"Predictor": lab}
        for modell in ["M1", "M2"]:
            t = m[(m["modell"] == modell) & (m["variabel"] == var)]
            rad[modell] = fmt(*t.iloc[0][["OR", "KI_lav", "KI_hoy"]]) if len(t) else "—"
        rader.append(rad)
    for modell in ["M1", "M2"]:   # kvinne-OR fra mann-dummyen
        t = m[(m["modell"] == modell) & (m["variabel"] == "gender_M")]
        if len(t):
            o, lo, hi = inverter(*t.iloc[0][["OR", "KI_lav", "KI_hoy"]])
            d = next((r for r in rader if r["Predictor"] == "Female (vs. male)"), None)
            if d is None:
                rader.append({"Predictor": "Female (vs. male)", modell: fmt(o, lo, hi)})
            else:
                d[modell] = fmt(o, lo, hi)
    a = {r["modell"]: r for _, r in auc.iterrows()}
    rader += [
        {"Predictor": "Cross-validated AUC",
         "M1": f"{a['M1']['cv_auc']:.3f}", "M2": f"{a['M2']['cv_auc']:.3f}"},
        {"Predictor": "ΔAUC M2 − M1 (95% interval)", "M1": "",
         "M2": f"{a['M2-M1']['cv_auc']:.3f} ({a['M2-M1']['p2_5']:.3f}–{a['M2-M1']['p97_5']:.3f})"},
        {"Predictor": "Calibration slope / Brier (M2)", "M1": "",
         "M2": f"{kal['kalibreringsslope'][0]:.2f} / {kal['brier'][0]:.3f}"},
    ]
    pd.DataFrame(rader).to_csv(TABM / "table2_models.csv", index=False)


def tabell3():
    h2 = pd.read_csv(HERE / "tables" / "modeller" / "h2_interaksjon.csv")
    h3 = pd.read_csv(HERE / "tables" / "modeller" / "h3_auc.csv")
    rader = []
    i = h2[(h2["modell"] == "H2_interaksjon") & (h2["variabel"] == "delta_x_kvartal")].iloc[0]
    rader.append({"Analysis": "Progression × birth-quarter trend (OR)",
                  "Estimate": fmt(i["OR"], i["KI_lav"], i["KI_hoy"], 3), "p": f"{i['p']:.2f}"})
    for s, lab in [("H2_strata_Q1-Q2", "Progression per SD, born Q1–Q2"),
                   ("H2_strata_Q3-Q4", "Progression per SD, born Q3–Q4")]:
        t = h2[h2["modell"] == s].iloc[0]
        rader.append({"Analysis": lab, "Estimate": fmt(t["OR"], t["KI_lav"], t["KI_hoy"]),
                      "p": f"{t['p']:.1e}"})
    for _, t in h3.iterrows():
        lab = {"volum+fremgang": "CV-AUC: sex + volume + progression",
               "volum+niva": "CV-AUC: sex + volume + level",
               "differanse": "Difference (progression − level)"}[t["modell"]]
        rader.append({"Analysis": lab,
                      "Estimate": f"{t['cv_auc']:.4f} ({t['p2_5']:.4f}–{t['p97_5']:.4f})",
                      "p": ""})
    pd.DataFrame(rader).to_csv(TABM / "table3_h2_h3.csv", index=False)


def tabell4():
    r = pd.read_csv(HERE / "tables" / "robusthet" / "robusthet_or.csv")
    ev = pd.read_csv(HERE / "tables" / "robusthet" / "e_verdi.csv").iloc[0]
    navn = {
        ("eksponeringsvariant", "delta_z"): "Primary: Δ mean of 3 best (main group)",
        ("eksponeringsvariant", "delta_max_z"): "Exposure: season best (maximum)",
        ("eksponeringsvariant", "delta_all_z"): "Exposure: mean of all results",
        ("eksponeringsvariant", "delta_vind_z"): "Exposure: wind-legal marks only",
        ("eksponeringsvariant", "delta_bg2_z"): "Exposure: best event group at 15–16",
        ("eksponeringsvariant", "delta_nk_1314_z"): "Specification check: Δ within 13→14",
        ("uten_covid_kull", "delta_z"): "Excluding cohorts born 2004–2005 (COVID window)",
        ("covid_interaksjon", "delta_x_covid"): "Progression × COVID-window interaction",
        ("k_minst_2", "delta_z"): "≥2 scored results in both windows",
        ("utfallsvariant", "delta_z"): None,  # håndteres under
        ("utfallsvariant_inkl_2006", "delta_z"): "Outcome: active at ≥18 (cohorts incl. 2006)",
        ("kohort_A", "delta_z"): "Cohort A (born 1998–2001)",
        ("kohort_B", "delta_z"): "Cohort B (born 2002–2005)",
        ("klubb_klusterrobust", "delta_z"): "Club-clustered robust SE",
        ("klubb_gee", "delta_z"): "GEE with exchangeable club correlation",
    }
    rader = []
    for _, t in r.iterrows():
        lab = navn.get((t["analyse"], t["eksponering"]))
        if t["analyse"] == "utfallsvariant":
            lab = {"senior_min1": "Outcome: ≥1 result at age ≥20",
                   "senior_20_21": "Outcome: ≥2 results in a year, ages 20–21"}[t["utfall"]]
        if lab is None:
            continue
        rader.append({"Analysis": lab, "n": f"{t['n']:,}", "Events": f"{t['hendelser']:,}",
                      "OR (95% CI)": fmt(t["OR"], t["KI_lav"], t["KI_hoy"])})
    rader.append({"Analysis": "E-value for the primary OR (CI bound)", "n": "", "Events": "",
                  "OR (95% CI)": f"{ev['E_verdi_punkt']:.2f} ({ev['E_verdi_KI_grense']:.2f})"})
    pd.DataFrame(rader).to_csv(TABM / "table4_robustness.csv", index=False)


def tabell_cox():
    c = pd.read_csv(HERE / "tables" / "robusthet" / "cox_landmark.csv")
    navn = {"delta_z": "Progression, per SD", "niva_w1_z": "Level 13–14, per SD",
            "vol1314_g": "Competition days 13–14, per SD",
            "vol1516_g": "Competition days 15–16, per SD",
            "k13": "Scored results 13–14", "k15": "Scored results 15–16",
            "kvinne": "Female (vs. male)"}
    rader = [{"Covariate": navn.get(t["covariate"], t["covariate"]),
              "HR (95% CI)": fmt(t["exp(coef)"], t["exp(coef) lower 95%"],
                                 t["exp(coef) upper 95%"])} for _, t in c.iterrows()]
    pd.DataFrame(rader).to_csv(TABM / "tableS_cox.csv", index=False)


def main():
    base, sesong = last_grunnlag()
    fig1(base, sesong)
    n_t, n_d = fig2(base, sesong)
    fig3(base)
    fig4(base)
    tabell1(base)
    tabell2()
    tabell3()
    tabell4()
    tabell_cox()
    logger.info(f"4 figurer i {FIG}/ (fig2: prestasjon n={n_t}, volum n={n_d}); "
                f"5 tabeller i {TABM}/")


if __name__ == "__main__":
    main()
