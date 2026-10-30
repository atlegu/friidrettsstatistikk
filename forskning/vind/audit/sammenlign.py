"""
sammenlign.py — A6-audit fase 3: R-reimplementasjonen mot de publiserte estimeringsfilene.

Sammenligner audit/r_out/* mot tables/estimering/r1_* (og flyt.json) og skriver
PASS/AVVIK per størrelse. Toleranser: utvalg eksakt; koeffisienter/KI 2e-4 i
naturlig enhet (tabellpresisjon er 1e-3); prosent 2e-3; SD-kvantiteter 2e-3.
"""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
EST = HERE.parent / "tables" / "estimering"
R = HERE / "r_out"

feil = []


def sjekk(navn, a, b, tol):
    d = abs(float(a) - float(b))
    ok = d <= tol
    if not ok:
        feil.append(f"{navn}: python={a} R={b} (diff {d:.2e} > {tol})")
    return ok


def hoved():
    r = pd.read_csv(R / "hoved.csv")
    p = pd.read_csv(EST / "r1_hoved_meet.csv")
    n = 0
    for _, rr in r.iterrows():
        merk = "hoved_meet" if rr["analyse"] == "hoved" else "hoved_meet_pst"
        t = p[(p["analyse"] == merk) & (p["event"] == rr["event"])]
        if not len(t):
            feil.append(f"hoved {rr['event']}/{merk}: mangler i python-filen")
            continue
        t = t.iloc[0]
        tol = 2e-4 if merk == "hoved_meet" else 2e-3
        for k_r, k_p in [("gevinst", "gevinst_per_ms"), ("ki_lav", "ki_lav"), ("ki_hoy", "ki_hoy")]:
            sjekk(f"hoved {rr['event']} {merk} {k_p}", t[k_p], rr[k_r], tol)
        sjekk(f"hoved {rr['event']} {merk} n", t["n"], rr["n"], 0)
        sjekk(f"hoved {rr['event']} {merk} celler", t["celler"], rr["celler"], 0)
        n += 1
    return n


def alder():
    r = pd.read_csv(R / "alder.csv")
    p = pd.read_csv(EST / "r1_alder_meet.csv")
    n = 0
    for _, rr in r.iterrows():
        t = p[(p["event"] == rr["event"]) & (p["kjonn"] == rr["kjonn"])
              & (p["aldersband"] == rr["aldersband"]) & (p["enhet"] == rr["enhet"])]
        if not len(t):
            feil.append(f"alder {rr['event']} {rr['kjonn']} {rr['aldersband']} {rr['enhet']}: mangler")
            continue
        t = t.iloc[0]
        tol = 2e-3 if rr["enhet"] == "%" else (2e-2 if rr["enhet"] == "cm" else 2e-4)
        for k_r, k_p in [("gevinst", "gevinst_per_ms"), ("ki_lav", "ki_lav"), ("ki_hoy", "ki_hoy")]:
            sjekk(f"alder {rr['event']} {rr['kjonn']} {rr['aldersband']} {rr['enhet']} {k_p}",
                  t[k_p], rr[k_r], tol)
        n += 1
    # R skal også ha funnet nøyaktig de samme radene (ingen manglende hos R)
    r_nokler = set(zip(r["event"], r["kjonn"], r["aldersband"], r["enhet"]))
    for _, t in p[p["event"].isin(r["event"].unique())].iterrows():
        if (t["event"], t["kjonn"], t["aldersband"], t["enhet"]) not in r_nokler:
            feil.append(f"alder: python-rad uten R-motstykke: {t['event']} {t['kjonn']} "
                        f"{t['aldersband']} {t['enhet']}")
    return n


def asym():
    r = pd.read_csv(R / "asym.csv")
    p = pd.read_csv(EST / "r1_asym_meet.csv")
    n = 0
    for _, rr in r.iterrows():
        t = p[p["event"] == rr["event"]]
        if not len(t):
            continue
        t = t.iloc[0]
        tid = rr["event"] in {"60m", "80m", "100m", "150m", "200m"}
        tol = 2e-4 if tid else 2e-2
        sjekk(f"asym {rr['event']} medvind", t["medvind"], rr["medvind"], tol)
        sjekk(f"asym {rr['event']} motvind", t["motvind"], rr["motvind"], tol)
        sjekk(f"asym {rr['event']} p_lik", t["p_lik_meet"], rr["p_lik"], 2e-3)
        if "ratio_drag" in rr and not pd.isna(rr["ratio_drag"]):
            sjekk(f"asym {rr['event']} drag-forhold", t["ratio_drag_estimator"], rr["ratio_drag"], 1e-3)
            sjekk(f"asym {rr['event']} drag medvind", t["drag_medvind"], rr["drag_medvind"], 2e-4)
            sjekk(f"asym {rr['event']} drag motvind", t["drag_motvind"], rr["drag_motvind"], 2e-4)
            sjekk(f"asym {rr['event']} drag kvad", t["drag_kvad"], rr["drag_kvad"], 2e-5)
        n += 1
    return n


def vindu():
    r = pd.read_csv(R / "vindu.csv")
    p = pd.read_csv(EST / "r1_vindu_medvind.csv")
    n = 0
    for _, rr in r.iterrows():
        t = p[(p["event"] == rr["event"]) & (p["kjonn"] == rr["kjonn"])
              & (p["aldersband"] == rr["aldersband"])]
        if not len(t):
            feil.append(f"vindu {rr['event']} {rr['kjonn']} {rr['aldersband']}: mangler i python")
            continue
        t = t.iloc[0]
        sjekk(f"vindu {rr['event']} {rr['kjonn']} {rr['aldersband']} medvind",
              t["medvind_s_per_ms"], rr["medvind"], 2e-4)
        sjekk(f"vindu ... {rr['aldersband']} motvind", t["motvind_s_per_ms"], rr["motvind"], 2e-4)
        sjekk(f"vindu ... {rr['aldersband']} fordel2ms", t["fordel_2ms_s"], rr["fordel_2ms"], 1e-3)
        sjekk(f"vindu ... {rr['aldersband']} sd_pool", t["sd_poolet_adj"], rr["sd_pool"], 2e-3)
        sjekk(f"vindu ... {rr['aldersband']} fordel_i_sd", t["fordel_i_sd"], rr["fordel_i_sd"], 2e-2)
        sjekk(f"vindu ... {rr['aldersband']} fordel 0-2", t["fordel_0_2_s"], rr["fordel_0_2"], 1e-3)
        sjekk(f"vindu ... {rr['aldersband']} robust skala", t["skala_robust"], rr["skala_robust"], 2e-3)
        sjekk(f"vindu ... {rr['aldersband']} fordel 0-2 / robust", t["fordel_0_2_i_robust_skala"],
              rr["fordel_0_2_robust"], 2e-2)
        n += 1
    if len(r) != len(p):
        feil.append(f"vindu: radantall R={len(r)} python={len(p)}")
    return n


def hekk():
    r = pd.read_csv(R / "hekk.csv")
    p = pd.read_csv(EST / "r1_hekk_meet.csv")
    n = 0
    for _, rr in r.iterrows():
        t = p[(p["kode"] == rr["kode"]) & (p["kjonn"] == rr["kjonn"])]
        if not len(t):
            feil.append(f"hekk {rr['kode']} {rr['kjonn']}: mangler i python")
            continue
        t = t.iloc[0]
        sjekk(f"hekk {rr['kode']} {rr['kjonn']} gevinst", t["gevinst_s_per_ms"], rr["gevinst"], 2e-4)
        sjekk(f"hekk {rr['kode']} {rr['kjonn']} ki_lav", t["ki_lav"], rr["ki_lav"], 2e-4)
        sjekk(f"hekk {rr['kode']} {rr['kjonn']} ki_hoy", t["ki_hoy"], rr["ki_hoy"], 2e-4)
        sjekk(f"hekk {rr['kode']} {rr['kjonn']} snitt_tid", t["snitt_tid_s"], rr["snitt_tid"], 5e-3)
        sjekk(f"hekk {rr['kode']} {rr['kjonn']} n", t["n"], rr["n"], 0)
        n += 1
    if len(r) != len(p):
        feil.append(f"hekk: radantall R={len(r)} python={len(p)}")
    return n


def utvalg():
    u = pd.read_csv(R / "utvalg_per_ovelse.csv")
    flyt = json.loads((HERE.parent / "data_private" / "flyt.json").read_text())
    n = 0
    sjekk("utvalg: analyserader totalt", flyt["rader_analyseklar"], int(u["r_rader"].sum()), 0)
    sjekk("utvalg: rader i celler >=2", flyt["rader_i_celler_min2"], int(u["r_min2"].sum()), 0)
    sjekk("utvalg: celler >=2", flyt["celler_min2"], int(u["r_celler2"].sum()), 0)
    for _, rr in u.iterrows():
        sjekk(f"utvalg {rr['event_code']} rader", rr["ak_rader"], rr["r_rader"], 0)
        sjekk(f"utvalg {rr['event_code']} min2", rr["ak_min2"], rr["r_min2"], 0)
        n += 1
    m = pd.read_csv(R / "utvalg_multisett.csv").iloc[0]
    sjekk("utvalg multisett: avvikende nøkler", 0, m["avvikende_nokler"], 0)
    sjekk("utvalg multisett: rader kun i R", 0, m["rader_kun_R"], 0)
    sjekk("utvalg multisett: rader kun i analyseklar", 0, m["rader_kun_ak"], 0)
    return n


def tertil():
    r = pd.read_csv(R / "tertil.csv")
    p = pd.read_csv(EST / "r1_tertil_adj.csv")
    n = 0
    for _, rr in r.iterrows():
        t = p[(p["event"] == rr["event"]) & (p["tertil"] == rr["tertil"])]
        if not len(t):
            feil.append(f"tertil {rr['event']} {rr['tertil']}: mangler i python")
            continue
        t = t.iloc[0]
        tid = rr["event"] in {"60m", "80m", "100m", "150m", "200m"}
        tol = 2e-4 if tid else 2e-2
        for k_r, k_p in [("gevinst", "gevinst_per_ms"), ("ki_lav", "ki_lav"), ("ki_hoy", "ki_hoy")]:
            sjekk(f"tertil {rr['event']} {rr['tertil']} {k_p}", t[k_p], rr[k_r], tol)
        sjekk(f"tertil {rr['event']} {rr['tertil']} n", t["n"], rr["n"], 0)
        sjekk(f"tertil {rr['event']} {rr['tertil']} celler", t["celler"], rr["celler"], 0)
        n += 1
    if len(r) != len(p):
        feil.append(f"tertil: radantall R={len(r)} python={len(p)}")
    return n


def deskriptiv():
    b = pd.read_csv(R / "bunching.csv").iloc[0]
    p = pd.read_csv(EST / "r1_bunching.csv").set_index("intervall")["andel"]
    for k_r, k_p in [("i16_18", "[1.6,1.8]"), ("i18_20", "(1.8,2.0]"), ("i20_22", "(2.0,2.2]"),
                     ("i22_24", "(2.2,2.4]"), ("null", "eksakt 0.0"), ("to", "eksakt 2.0")]:
        sjekk(f"bunching {k_p}", p[k_p], b[k_r], 1e-5)
    ps = pd.read_csv(R / "per_sekund.csv").set_index("event_code")
    pp = pd.read_csv(EST / "r1_per_sekund.csv").set_index("event")
    for k in pp.index:
        sjekk(f"per sekund {k} snitt", pp.loc[k, "snitt_tid_s"], ps.loc[k, "snitt"], 5e-3)
        sjekk(f"per sekund {k} rate", pp.loc[k, "per_sekund"], ps.loc[k, "per_sekund"], 1e-5)
    mv = pd.read_csv(R / "manglende_vind.csv").set_index("gruppe")
    pm = pd.read_csv(EST / "r1_missingvind_storrelse.csv")
    for i, (_, t) in enumerate(pm.iterrows(), start=1):
        sjekk(f"manglende vind størrelsestertil {i}", t["mean"], mv.loc[f"str_tertil_{i}", "andel"], 1e-4)
        sjekk(f"manglende vind størrelsestertil {i} n", t["count"], mv.loc[f"str_tertil_{i}", "n"], 0)
    niv = pd.read_csv(EST / "r1_missingvind_nivaa.csv").iloc[0]
    sjekk("manglende vind alle ute", niv["mean"], mv.loc["alle_ute", "andel"], 1e-4)
    sjekk("manglende vind alle ute n", niv["count"], mv.loc["alle_ute", "n"], 0)
    ii = pd.read_csv(R / "innendors.csv").set_index("event_code")["N"]
    pi = pd.read_csv(EST / "r1_innendors_per_ovelse.csv").set_index("event_code")["innendorsrader"]
    for k in pi.index:
        sjekk(f"innendørsrader {k}", pi[k], ii[k], 0)
    return 6 + len(pp) + len(pm) + 1 + len(pi)


def kvad():
    r = pd.read_csv(R / "kvad.csv")
    p = pd.read_csv(EST / "r1_kvad_meet.csv")
    for _, rr in r.iterrows():
        t = p[p["event"] == rr["event"]].iloc[0]
        for k in ["beta_lin", "se_lin", "beta_kvad", "se_kvad"]:
            sjekk(f"kvad {rr['event']} {k}", t[k], rr[k], 2e-6)
        sjekk(f"kvad {rr['event']} n", t["n"], rr["n"], 0)
    return len(r)


def stevne_fe():
    r = pd.read_csv(R / "stevne_fe_alder.csv")
    p = pd.read_csv(EST / "r2_stevne_fe_alder.csv")
    for _, rr in r.iterrows():
        t = p[(p["event"] == rr["event"]) & (p["kjonn"] == rr["kjonn"]) & (p["aldersband"] == rr["aldersband"])]
        if not len(t):
            feil.append(f"stevne-FE {rr['event']} {rr['kjonn']} {rr['aldersband']}: mangler i python")
            continue
        t = t.iloc[0]
        sjekk(f"stevne-FE {rr['event']} {rr['kjonn']} {rr['aldersband']} estimat", t["stevne_fe_s"], rr["stevne_fe"], 2e-4)
        # KI: i nesten mettede to-veis-celler (200 m gutter 10-11: 1 301 resultater, 498 celler, 526
        # stevner) tar Python ut månedsdummyer som numerisk absorbert, mens fixest beholder dem; tre
        # regressorer i forskjell gir 0,2 % ulik SE. Toleransen 1e-3 dekker dette.
        for k_r, k_p in [("ki_lav", "stevne_fe_ki_lav"), ("ki_hoy", "stevne_fe_ki_hoy")]:
            sjekk(f"stevne-FE {rr['event']} {rr['kjonn']} {rr['aldersband']} {k_p}", t[k_p], rr[k_r], 1e-3)
        sjekk(f"stevne-FE {rr['event']} {rr['kjonn']} {rr['aldersband']} n", t["n"], rr["n"], 0)
    if len(r) != len(p):
        feil.append(f"stevne-FE: radantall R={len(r)} python={len(p)}")
    return len(r)


def main():
    deler = [("utvalg", utvalg), ("hoved", hoved), ("alder", alder),
             ("asym", asym), ("vindu", vindu), ("hekk", hekk),
             ("tertil", tertil), ("deskriptiv", deskriptiv), ("kvad", kvad), ("stevne-FE", stevne_fe)]
    for navn, fn in deler:
        n = fn()
        print(f"{navn}: {n} enheter sammenlignet")
    if feil:
        print(f"\nAVVIK ({len(feil)}):")
        for f in feil:
            print("  -", f)
        sys.exit(1)
    print("\nALLE SAMMENLIGNINGER PASSERTE")


if __name__ == "__main__":
    main()
