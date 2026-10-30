r"""
07_manustabeller.py — A1: manustabellene 1–4 og S1 som LaTeX, rett fra modell- og datafilene.

Ingen tall skrives for hånd (audit 30.10.2026): tabellene \input-es i manus/main.tex.
Avrunding skjer én gang, ved visning, fra full presisjon.
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
MOD = HERE / "tables" / "modeller"
ROB = HERE / "tables" / "robusthet"
TABM = HERE / "tables" / "manus"
UT = HERE / "manus"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def tusen(n):
    return f"{int(n):,}".replace(",", "\\,")


def tall(x, d):
    s = f"{x:.{d}f}"
    return "$-$" + s[1:] if s.startswith("-") else s


def ki(o, lo, hi, d=2):
    return f"{tall(o, d)} ({tall(lo, d)}--{tall(hi, d)})"


def p_tekst(p):
    return "$<$.001" if p < 0.001 else f"{p:.2f}"


def tabular(hode, rader, kolfmt, midtlinjer=()):
    linjer = [f"\\begin{{tabular}}{{{kolfmt}}}", "\\toprule", " & ".join(hode) + " \\\\", "\\midrule"]
    for i, r in enumerate(rader):
        if i in midtlinjer:
            linjer.append("\\midrule")
        linjer.append(" & ".join(r) + " \\\\")
    linjer += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(linjer) + "\n"


def prim_utvalg():
    d = pd.read_csv(DATA / "analysedata.csv")
    return d[d["kohort_primar"] & d["skaarbar"] & ~d["liten_gruppecelle"]].copy()


def med_iqr(s):
    return (f"{tall(s.median(), 0)} ({tall(s.quantile(0.25), 0)}--{tall(s.quantile(0.75), 0)})")


def t1():
    p = prim_utvalg()
    grupper = [p, p[p["senior"] == 1], p[p["senior"] == 0]]
    rader = [["n"] + [tusen(len(g)) for g in grupper],
             ["Female, \\%"] + [f"{(g['gender'] == 'F').mean() * 100:.1f}" for g in grupper],
             ["Cohort A (born 1998--2001), \\%"] + [f"{(g['kohort'] == 'A').mean() * 100:.1f}" for g in grupper]]
    for kode, navn in [("sprint", "sprints"), ("jumps", "jumps"), ("middle_distance", "middle distance"),
                       ("throws", "throws")]:
        rader.append([f"Main event group: {navn}, \\%"]
                     + [f"{(g['hovedgruppe'] == kode).mean() * 100:.1f}" for g in grupper])
    rader.append(["Born Q1, \\% of those with a birth date"] + [f"{(g.loc[g['kvartal'].notna(), 'kvartal'] == 1).mean() * 100:.1f}" for g in grupper])
    rader.append(["Born Q4, \\% of those with a birth date"] + [f"{(g.loc[g['kvartal'].notna(), 'kvartal'] == 4).mean() * 100:.1f}" for g in grupper])
    for kol, navn in [("vol1314", "Competition days 13--14"), ("vol1516", "Competition days 15--16"),
                      ("k13", "Scored results 13--14 ($k_{13}$)"), ("k15", "Scored results 15--16 ($k_{15}$)"),
                      ("niva_w1", "Age-graded points 13--14"), ("niva_w2", "Age-graded points 15--16"),
                      ("delta", "Progression, points"),
                      ("delta_lik", "Progression at equal numbers of results, points")]:
        rader.append([f"{navn}, median (IQR)"] + [med_iqr(g[kol]) for g in grupper])
    rader.append(["Negative progression, \\%"] + [f"{(g['delta'] < 0).mean() * 100:.1f}" for g in grupper])
    rader.append(["Negative progression at equal numbers of results, \\%"]
                 + [f"{(g['delta_lik'] < 0).mean() * 100:.1f}" for g in grupper])
    return tabular(["Characteristic", "All", "Senior retainers", "Future dropouts"], rader, "lccc")


def t2():
    m = pd.read_csv(MOD / "h1_or.csv")
    auc = pd.read_csv(MOD / "h1_auc.csv").set_index("modell")
    kal = pd.read_csv(MOD / "kalibrering.csv").iloc[0]
    dl = pd.read_csv(MOD / "r1_delong.csv").set_index("kontrast").loc["M2_minus_M1"]
    navn = [("delta_z", "Progression 13--14 $\\to$ 15--16, per SD"),
            ("niva_w1_z", "Performance level 13--14, per SD"),
            ("vol1314_g", "Competition days 13--14, per SD"),
            ("vol1516_g", "Competition days 15--16, per SD"),
            ("k13", "Scored results 13--14, per result"),
            ("k15", "Scored results 15--16, per result")]
    rader = []
    for var, lab in navn:
        rad = [lab]
        for modell in ["M1", "M2"]:
            t = m[(m["modell"] == modell) & (m["variabel"] == var)]
            rad.append(ki(*t.iloc[0][["OR", "KI_lav", "KI_hoy"]]) if len(t) else "---")
        rader.append(rad)
    rad = ["Female (vs.\\ male)"]
    for modell in ["M1", "M2"]:
        t = m[(m["modell"] == modell) & (m["variabel"] == "gender_M")].iloc[0]
        rad.append(ki(1 / t["OR"], 1 / t["KI_hoy"], 1 / t["KI_lav"]))
    rader.append(rad)
    rader.append(["Cross-validated AUC", f"{auc.loc['M1', 'cv_auc']:.3f}", f"{auc.loc['M2', 'cv_auc']:.3f}"])
    rader.append(["$\\Delta$AUC M2 $-$ M1, DeLong 95\\,\\% CI",
                  f"\\multicolumn{{2}}{{c}}{{{dl['diff']:.3f} ({dl['ki_lav']:.3f}--{dl['ki_hoy']:.3f}); "
                  f"repetition spread {auc.loc['M2-M1', 'p2_5']:.3f}--{auc.loc['M2-M1', 'p97_5']:.3f}}}"])
    rader.append(["Calibration slope / Brier (M2)",
                  f"\\multicolumn{{2}}{{c}}{{{kal['kalibreringsslope']:.2f} / {kal['brier']:.3f}}}"])
    tekst = tabular(["Predictor", "M1", "M2"], rader, "lcc", midtlinjer=(7,))
    return tekst.replace(" & \\multicolumn", " & \\multicolumn")


def t3():
    h2 = pd.read_csv(MOD / "h2_interaksjon.csv")
    h3 = pd.read_csv(MOD / "h3_auc.csv").set_index("modell")
    med = pd.read_csv(MOD / "r1_mediering.csv").set_index("modell")
    dl = pd.read_csv(MOD / "r1_delong.csv").set_index("kontrast").loc["volum+fremgang_minus_volum+niva"]
    n_q = int(med.loc["uten_delta", "n"])
    i = h2[(h2["modell"] == "H2_interaksjon") & (h2["variabel"] == "delta_x_kvartal")].iloc[0]
    rader = [[f"Progression $\\times$ birth-quarter trend, OR per quarter (n = {tusen(n_q)})",
              ki(i["OR"], i["KI_lav"], i["KI_hoy"], 3), p_tekst(i["p"])]]
    for s, lab in [("H2_strata_Q1-Q2", "Progression per SD, born Q1--Q2"),
                   ("H2_strata_Q3-Q4", "Progression per SD, born Q3--Q4")]:
        t = h2[(h2["modell"] == s) & (h2["variabel"] == "delta_z")].iloc[0]
        rader.append([lab, ki(t["OR"], t["KI_lav"], t["KI_hoy"]), p_tekst(t["p"])])
    r2 = pd.read_csv(MOD / "r2_mediering.csv").set_index("storrelse")
    for nokkel, lab in [("a_sti_ubetinget_SD_per_kvartal", "Progression on birth quarter, SD per quarter, unadjusted"),
                        ("a_sti_betinget_M1_SD_per_kvartal",
                         "Progression on birth quarter, adjusted for level, volume, $k$ and covariates")]:
        o = r2.loc[nokkel]
        rader.append([lab, f"{tall(o['estimat'], 3)} ({tall(o['ki_lav'], 3)}--{tall(o['ki_hoy'], 3)})",
                      p_tekst(o["p"])])
    o = r2.loc["kvartal_OR_bare_M0"]
    rader.append(["Birth quarter and senior activity, sex, cohort and club size only (OR per quarter)",
                  ki(o["estimat"], o["ki_lav"], o["ki_hoy"]), p_tekst(o["p"])])
    n_p = len(prim_utvalg())
    rader.append([f"CV-AUC: sex + volume + $k$ + progression (n = {tusen(n_p)})",
                  f"{h3.loc['volum+fremgang', 'cv_auc']:.3f} (repetition spread "
                  f"{h3.loc['volum+fremgang', 'p2_5']:.3f}--{h3.loc['volum+fremgang', 'p97_5']:.3f})", ""])
    rader.append(["CV-AUC: sex + volume + $k$ + level",
                  f"{h3.loc['volum+niva', 'cv_auc']:.3f} (repetition spread "
                  f"{h3.loc['volum+niva', 'p2_5']:.3f}--{h3.loc['volum+niva', 'p97_5']:.3f})", ""])
    rader.append(["Difference (progression $-$ level), DeLong 95\\,\\% CI",
                  f"{tall(dl['diff'], 3)} ({tall(dl['ki_lav'], 3)} to {tall(dl['ki_hoy'], 3)})",
                  f"{dl['p']:.2f}"])
    return tabular(["Analysis", "Estimate", "$p$"], rader, "lcc", midtlinjer=(6,))


def t4():
    r = pd.read_csv(ROB / "robusthet_or.csv")
    ev = pd.read_csv(ROB / "e_verdi.csv").iloc[0]
    sw = pd.read_csv(MOD / "r1_switcher_flyt.csv", index_col=0)["verdi"]

    def rad(an, eks=None, utf=None):
        t = r[(r["analyse"] == an) & ((r["eksponering"] == eks) if eks else True)
              & ((r["utfall"] == utf) if utf else True)].iloc[0]
        return [tusen(t["n"]), tusen(t["hendelser"]), ki(t["OR"], t["KI_lav"], t["KI_hoy"])]

    r2 = pd.read_csv(MOD / "r2_h1_folsomhet.csv").set_index("analyse")

    def r2rad(an, d=2):
        t = r2.loc[an]
        return [tusen(t["n"]), tusen(t["hendelser"]), ki(t["OR"], t["KI_lav"], t["KI_hoy"], d)]

    lo, hi = float(sw["inklusiv_KI_lav"]), float(sw["inklusiv_KI_hoy"])
    rader = [
        ["Primary: $\\Delta$ mean of 3 best, main event group"] + rad("eksponeringsvariant", "delta_z"),
        ["Exposure: season best (maximum)"] + rad("eksponeringsvariant", "delta_max_z"),
        ["Exposure: mean of all results"] + rad("eksponeringsvariant", "delta_all_z"),
        ["Exposure: wind-legal marks only"] + rad("eksponeringsvariant", "delta_vind_z"),
        ["Exposure: equal numbers of results in both windows"] + r2rad("like_mange_resultater"),
        ["Exposure: event-equated points"] + r2rad("ovelsesjusterte_poeng"),
        ["Exposure: outdoor marks only"] + r2rad("bare_utendors"),
        # gruppekonsistent (nivå og antall i beste gruppe) som hovedrad; planens variant under
        # (Atles beslutning 30.10.2026)
        ["Exposure: best event group at 15--16, inclusive sample", tusen(sw["kons_n"]),
         tusen(sw["kons_hendelser"]), ki(float(sw["kons_OR"]), float(sw["kons_KI_lav"]), float(sw["kons_KI_hoy"]))],
        ["\\quad level and counts from the main group (analysis plan)", tusen(sw["inklusiv_n"]),
         tusen(sw["inklusiv_hendelser"]), ki(float(sw["inklusiv_OR"]), lo, hi)],
        ["Splines for result counts and competition days"] + r2rad("splines_k_og_volum"),
        ["Earlier level given later level, per 100 points"] + r2rad("tidlig_niva_per_100p_gitt_senere"),
        ["Specification check: $\\Delta$ within ages 13$\\to$14"] + rad("eksponeringsvariant", "delta_nk_1314_z"),
        ["Excluding cohorts born 2004--2005 (COVID window)"] + rad("uten_covid_kull"),
        ["Progression $\\times$ COVID-window interaction"] + rad("covid_interaksjon"),
        ["$\\geq$2 scored results in both windows"] + rad("k_minst_2"),
        ["$\\geq$3 scored results in both windows"] + r2rad("k13_og_k15_minst_3"),
        ["Athletes still competing after age 16"] + r2rad("aktiv_etter_16"),
        ["Outcome: $\\geq$1 result at age $\\geq$20"] + rad("utfallsvariant", utf="senior_min1"),
        ["Outcome: $\\geq$2 results in a year, ages 20--21"] + rad("utfallsvariant", utf="senior_20_21"),
        ["Outcome: active at $\\geq$18 (cohorts incl.\\ 2006)"] + rad("utfallsvariant_inkl_2006"),
        ["Cohort A (born 1998--2001)"] + rad("kohort_A"),
        ["Cohort B (born 2002--2005)"] + rad("kohort_B"),
        ["Club-clustered robust SE"] + rad("klubb_klusterrobust"),
        ["GEE, exchangeable club correlation"] + rad("klubb_gee"),
        ["E-value for the primary OR (CI bound)", "", "",
         f"{ev['E_verdi_punkt']:.2f} ({ev['E_verdi_KI_grense']:.2f})"],
    ]
    return tabular(["Analysis", "n", "Events", "OR (95\\,\\% CI)"], rader, "lccc")


def s1():
    flyt = json.loads((DATA / "flyt.json").read_text())
    r = pd.read_csv(ROB / "robusthet_or.csv")
    a18 = int(r[r["analyse"] == "utfallsvariant_inkl_2006"]["n"].iloc[0])
    f2 = pd.read_csv(TABM / "fig2_data.csv").groupby("panel")["n"].first()
    sw = pd.read_csv(MOD / "r1_switcher_flyt.csv", index_col=0)["verdi"]
    med = pd.read_csv(MOD / "r1_mediering.csv").set_index("modell")
    rader = [
        ["Athletes born 1998--2006 in the registry extract", tusen(flyt["utovere_fodt_1998_2006"])],
        ["With $\\geq$1 approved result at age 13--14", tusen(flyt["ok_resultat_13_14"])],
        ["Also competing at ages 15--16 (landmark condition)", tusen(flyt["landmark_13_14_og_15_16"])],
        ["With known sex", tusen(flyt["landmark_med_kjonn"])],
        ["\\quad born 2006 (used only for the activity-at-$\\geq$18 outcome)",
         tusen(flyt["landmark_med_kjonn"] - flyt["landmark_fodt_1998_2005"])],
        ["Born 1998--2005", tusen(flyt["landmark_fodt_1998_2005"])],
        ["\\quad excluded: no scorable main-group points in both windows",
         tusen(flyt["uten_skaarbar_tyrving_i_hovedgruppen"])],
        ["\\quad excluded: sex $\\times$ event-group cells with $<$20 athletes",
         tusen(flyt["ekskludert_gruppecelle_under_20"])],
        ["Primary sample (born 1998--2005)", tusen(flyt["primaerutvalg_fodt_1998_2005"])],
        ["\\quad active seniors", tusen(flyt["primaerutvalg_seniorer"])],
        ["\\quad with exact birth date (H2 analyses)", tusen(med.loc["uten_delta", "n"])],
        ["Exit-aligned trajectory subsamples (performance / volume)",
         f"{tusen(f2['Age-graded performance'])} / {tusen(f2['Competition volume'])}"],
        ["Inclusive best-group exposure sample", tusen(sw["kons_n"])],
        ["Activity-at-$\\geq$18 outcome sample (primary sample plus born 2006)", tusen(a18)],
    ]
    return tabular(["Step", "n"], rader, "lr")


def main():
    for navn, fn in [("t1", t1), ("t2", t2), ("t3", t3), ("t4", t4), ("s1", s1)]:
        (UT / f"{navn}.tex").write_text(fn())
    logger.info(f"t1–t4 og s1 skrevet til {UT}/")


if __name__ == "__main__":
    main()
