"""
sammenlign.py — A3-audit fase 3: R-reimplementasjonen mot de publiserte modelltabellene.

Toleranser: utvalg eksakt; OR/KI 1e-3; LRT 0.1 på LR; Cox 2e-3; retention eksakt
på tellere/nevnere og 2e-4 på andeler/KI.
"""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
TAB = HERE.parent / "tables" / "modeller"
R = HERE / "r_out"
feil = []


def sjekk(navn, py, rv, tol):
    d = abs(float(py) - float(rv))
    if d > tol:
        feil.append(f"{navn}: python={py} R={rv} (diff {d:.2e} > {tol})")


def or_sjekk(py_df, py_analyse, py_var, r_df, r_analyse, r_var, navn, tol=1e-3, n_tol=0):
    t = py_df[(py_df["analyse"] == py_analyse) & (py_df["variabel"] == py_var)]
    rr = r_df[(r_df["analyse"] == r_analyse) & (r_df["variabel"] == r_var)]
    if not len(t) or not len(rr):
        feil.append(f"{navn}: mangler rad (py {len(t)}, R {len(rr)})")
        return
    t, rr = t.iloc[0], rr.iloc[0]
    sjekk(f"{navn} OR", t["OR"], rr["OR"], tol)
    sjekk(f"{navn} KI_lav", t["KI_lav"], rr["KI_lav"], tol)
    sjekk(f"{navn} KI_hoy", t["KI_hoy"], rr["KI_hoy"], tol)
    if "n" in t and n_tol == 0:
        sjekk(f"{navn} n", t["n"], rr["n"], 0)


def main():
    u = pd.read_csv(R / "utvalg.csv").iloc[0]
    flyt = json.loads((HERE.parent / "data_private" / "flyt.json").read_text())
    sjekk("utvalg n_prim", flyt["primaerutvalg_fodt_2001_2005_debut_10_16"], u["n_prim_R"], 0)
    sjekk("utvalg seniorer", flyt["primaerutvalg_seniorer"], u["seniorer_R"], 0)
    for k in ["kun_R", "kun_py", "ulik_debutalder", "ulik_senior"]:
        sjekk(f"utvalg {k}", 0, u[k], 0)

    lg = pd.read_csv(R / "logit.csv")
    h1 = pd.read_csv(TAB / "h1_debutalder.csv")
    for alder in range(11, 17):
        or_sjekk(h1, "H1_kategorisk", f"debut_kat_{alder}", lg, "H1_kategorisk",
                 f"debut_kat{alder}", f"H1 debut {alder}")
    or_sjekk(h1, "H1_trend", "debut_alder", lg, "H1_trend", "debut_alder", "H1 trend")

    lrt_py = pd.read_csv(TAB / "r1_lrt.csv").iloc[0]
    lrt_r = lg[lg["analyse"] == "LRT"].iloc[0]
    sjekk("LRT LR", lrt_py["LR"], lrt_r["OR"], 0.1)
    sjekk("LRT df", lrt_py["df"], lrt_r["KI_lav"], 0)

    h3 = pd.read_csv(TAB / "r1_h3_landmark.csv")
    or_sjekk(h3, "r1_H3_uten_volum", "debut_alder", lg, "r1_H3_uten_volum", "debut_alder",
             "H3 uten volum")
    or_sjekk(h3, "r1_H3_med_volum", "debut_alder", lg, "r1_H3_med_volum", "debut_alder",
             "H3 med volum")
    info = pd.read_csv(TAB / "r1_h3_landmark_info.csv")
    ny = info[info["mål"].str.contains("ny def")].iloc[0]
    idle = info[info["mål"].str.contains("UTENFOR")].iloc[0]
    inf_r = lg[lg["analyse"] == "landmark_info"].set_index("variabel")["OR"]
    sjekk("landmark n", ny["n"], inf_r["n_ny"], 0)
    sjekk("landmark seniorer", ny["seniorer"], inf_r["seniorer_ny"], 0)
    sjekk("landmark idle17-tilbake", idle["n"], inf_r["idle17_tilbake"], 0)

    d17 = pd.read_csv(TAB / "r1_debut1719.csv")
    or_sjekk(d17, "r1_debut_17_19", "debut_kat_17", lg, "r1_debut_17_19", "debut_kat17",
             "debut 17-19")

    ki = pd.read_csv(TAB / "r1_kjonn_interaksjon.csv")
    or_sjekk(ki, "r1_kjonnsinteraksjon", "debut_x_kvinne", lg, "r1_kjonnsinteraksjon", "dxk",
             "kjønnsinteraksjon")

    rob = pd.read_csv(TAB / "robusthet.csv")
    for navn, r_navn, var in [("uten_covid_debut", "uten_covid_debut", "debut_alder"),
                              ("utfall_min1", "utfall_min1", "debut_alder"),
                              ("betinget_debutvolum", "betinget_debutvolum", "debut_alder"),
                              ("kohort_2001_2003", "kohort_2001_2003", "debut_alder"),
                              ("kohort_2004_2005", "kohort_2004_2005", "debut_alder")]:
        or_sjekk(rob, navn, var, lg, r_navn, var, f"robusthet {navn}")

    cox_py = pd.read_csv(TAB / "h2_cox.csv")
    cox_r = pd.read_csv(R / "cox.csv")
    t = cox_py[cox_py["covariate"] == "debut_alder"].iloc[0]
    rr = cox_r[cox_r["variabel"] == "debut_alder"].iloc[0]
    sjekk("Cox HR debut_alder", t["exp(coef)"], rr["HR"], 2e-3)
    sjekk("Cox KI_lav", t["exp(coef) lower 95%"], rr["KI_lav"], 2e-3)
    sjekk("Cox KI_hoy", t["exp(coef) upper 95%"], rr["KI_hoy"], 2e-3)

    rk_py = pd.read_csv(TAB / "r1_retention_ci.csv")
    rk_r = pd.read_csv(R / "retention.csv")
    m = rk_py.merge(rk_r, on=["debut_alder", "k"], suffixes=("_py", "_r"))
    if len(m) != len(rk_py) or len(m) != len(rk_r):
        feil.append(f"retention: radantall py={len(rk_py)} R={len(rk_r)} felles={len(m)}")
    for _, t in m.iterrows():
        pre = f"retention {t['debut_alder']} k={t['k']}"
        sjekk(f"{pre} n", t["n_py"], t["n_r"], 0)
        sjekk(f"{pre} aktive", t["aktive_py"], t["aktive_r"], 0)
        sjekk(f"{pre} andel", t["andel_py"], t["andel_r"], 2e-4)
        sjekk(f"{pre} ki_lav", t["ki_lav_py"], t["ki_lav_r"], 2e-4)
        sjekk(f"{pre} ki_hoy", t["ki_hoy_py"], t["ki_hoy_r"], 2e-4)

    # ---- revisjon r2 (audit 30.10.2026) ----
    va_py = pd.read_csv(TAB / "r2_varighet_andeler.csv")
    va_r = pd.read_csv(R / "varighet_andeler.csv")
    m = va_py.merge(va_r, on=["D", "debut_alder"], suffixes=("_py", "_r"))
    if len(m) != len(va_py) or len(m) != len(va_r):
        feil.append(f"varighet: radantall py={len(va_py)} R={len(va_r)} felles={len(m)}")
    for _, t in m.iterrows():
        sjekk(f"varighet D={t['D']} debut {t['debut_alder']} n", t["n_py"], t["n_r"], 0)
        sjekk(f"varighet D={t['D']} debut {t['debut_alder']} hendelser", t["hendelser_py"], t["hendelser_r"], 0)
    vm = pd.read_csv(TAB / "r2_varighet_modeller.csv")
    for D in (4, 5, 6):
        or_sjekk(vm, f"varighet_{D}", "debut_alder", lg, f"varighet_{D}", "debut_alder", f"varighet {D} trend")
        for alder in range(11, 17):
            or_sjekk(vm, f"varighet_{D}_kategorisk", f"debut_kat_{alder}", lg, f"varighet_{D}_kategorisk",
                     f"debut_kat{alder}", f"varighet {D} debut {alder}")
    u01 = pd.read_csv(TAB / "r2_uten_2001.csv")
    or_sjekk(u01, "uten_2001_trend", "debut_alder", lg, "uten_2001_trend", "debut_alder", "uten 2001 trend")
    for alder in range(11, 17):
        or_sjekk(u01, "uten_2001_kategorisk", f"debut_kat_{alder}", lg, "uten_2001_kategorisk",
                 f"debut_kat{alder}", f"uten 2001 debut {alder}")
    ukj = pd.read_csv(TAB / "r2_ukjent_kjonn.csv")
    or_sjekk(ukj, "med_ukjent_kjonn_trend", "debut_alder", lg, "med_ukjent_kjonn_trend", "debut_alder",
             "ukjent kjønn trend")
    da_py = pd.read_csv(TAB / "r2_andel_etter_alder.csv")
    da_r = pd.read_csv(R / "andel_alder.csv")
    m = da_py.merge(da_r, on=["alder", "gruppe"], suffixes=("_py", "_r"))
    if len(m) != len(da_py) or len(m) != len(da_r):
        feil.append(f"andel etter alder: radantall py={len(da_py)} R={len(da_r)} felles={len(m)}")
    for _, t in m.iterrows():
        sjekk(f"andel {t['gruppe']} alder {t['alder']} n", t["n_py"], t["n_r"], 0)
        sjekk(f"andel {t['gruppe']} alder {t['alder']} aktive", t["aktive_py"], t["aktive_r"], 0)

    u10 = pd.read_csv(R / "debut_under10.csv").iloc[0, 0]
    print(f"A3-2: utøvere med første resultat før fylte 10: {u10}")

    if feil:
        print(f"\nAVVIK ({len(feil)}):")
        for f in feil:
            print("  -", f)
        sys.exit(1)
    print("ALLE SAMMENLIGNINGER PASSERTE")


if __name__ == "__main__":
    main()
