"""
sammenlign.py — A1-audit fase 3: R-reimplementasjonen mot de publiserte modellfilene.

Toleranser: utvalg/tellinger eksakt; variabelverdier (radkontroll) 1e-6;
logit-OR/KI 2e-4 (region er konstant i A1, så modellene skal være identiske);
klyngede/Cox/E-verdi 2e-3–0.02. CV-baserte størrelser dekkes av delong_bro.
Revisjon r2 (30.10.2026): like mange resultater per utøver (1e-6), følsomhetsmodellene,
mediering, nivåtertiler, kjønn og exit-banene (prestasjon i fire varianter og volum).
"""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
TAB = HERE.parent / "tables"
R = HERE / "r_out"
feil = []


def sjekk(navn, py, rv, tol):
    try:
        d = abs(float(py) - float(rv))
    except (TypeError, ValueError):
        feil.append(f"{navn}: uleselig ({py!r} mot {rv!r})")
        return
    if d > tol:
        feil.append(f"{navn}: python={py} R={rv} (diff {d:.2e} > {tol})")


VARMAP = {"gender_M": "genderM", "log_klubbstorrelse": "log_klubb_f",
          "delta_x_kvartal": "dxq", "delta_x_niva": "dxn", "delta_x_kvinne": "dxk",
          "delta_nk_1314_z": "delta_nk_z", "delta_x_covid": "dxc", "const": "(Intercept)"}


def rvar(v):
    if v in VARMAP:
        return VARMAP[v]
    if v.startswith("birth_year_"):
        return "bk" + v.split("_")[-1]
    return v


def or_sjekk(py_df, py_sel, r_df, r_sel, navn, tol=2e-4, med_n=True):
    t = py_df.loc[py_sel]
    rr = r_df.loc[r_sel]
    if not len(t) or not len(rr):
        feil.append(f"{navn}: mangler rad (py {len(t)}, R {len(rr)})")
        return
    t, rr = t.iloc[0], rr.iloc[0]
    sjekk(f"{navn} OR", t["OR"], rr["OR"], tol)
    sjekk(f"{navn} KI_lav", t["KI_lav"], rr["KI_lav"], tol)
    sjekk(f"{navn} KI_hoy", t["KI_hoy"], rr["KI_hoy"], tol)
    if med_n and "n" in t.index and not pd.isna(t.get("n")):
        sjekk(f"{navn} n", t["n"], rr["n"], 0)


def main():
    u = pd.read_csv(R / "utvalg.csv").iloc[0]
    flyt = json.loads((HERE.parent / "data_private" / "flyt.json").read_text())
    opps = json.loads((TAB / "modeller" / "oppsummering.json").read_text())
    for navn, fasit in [("landmark", flyt["landmark_13_14_og_15_16"]),
                        ("landmark_med_kjonn", flyt["landmark_med_kjonn"]),
                        ("uten_fodselsdato", flyt["landmark_uten_fodselsdato"]),
                        ("uten_skaarbar", flyt["uten_skaarbar_tyrving_i_hovedgruppen"]),
                        ("ekskl_smaacelle", flyt["ekskludert_gruppecelle_under_20"]),
                        ("n_prim_for_dropna", flyt["primaerutvalg_fodt_1998_2005"]),
                        ("n_prim_modeller", opps["n"]), ("seniorer", opps["seniorer"])]:
        sjekk(f"utvalg {navn}", fasit, u[navn], 0)
    rk = pd.read_csv(R / "radkontroll.csv").iloc[0]
    for k in ["kun_R", "kun_py", "ulik_vol", "ulik_k", "ulik_senior"]:
        sjekk(f"radkontroll {k}", 0, rk[k], 0)
    sjekk("radkontroll max_diff_delta", 0, rk["max_diff_delta"], 1e-6)
    sjekk("radkontroll max_diff_niva", 0, rk["max_diff_niva"], 1e-6)

    lg = pd.read_csv(R / "logit.csv")
    h1 = pd.read_csv(TAB / "modeller" / "h1_or.csv")
    for modell, varer in [("M0", ["gender_M", "log_klubbstorrelse"]),
                          ("M1", ["niva_w1_z", "vol1314_g", "vol1516_g", "k13", "k15"]),
                          ("M2", ["delta_z", "niva_w1_z", "vol1314_g", "vol1516_g",
                                  "k13", "k15", "gender_M"]
                           + [f"birth_year_{y}" for y in range(1999, 2006)])]:
        for v in varer:
            or_sjekk(h1, (h1["modell"] == modell) & (h1["variabel"] == v),
                     lg, (lg["analyse"] == modell) & (lg["variabel"] == rvar(v)),
                     f"{modell} {v}", med_n=False)

    h2 = pd.read_csv(TAB / "modeller" / "h2_interaksjon.csv")
    for v in ["delta_z", "kvartal_c", "delta_x_kvartal"]:
        or_sjekk(h2, (h2["modell"] == "H2_interaksjon") & (h2["variabel"] == v),
                 lg, (lg["analyse"] == "H2_interaksjon") & (lg["variabel"] == rvar(v)),
                 f"H2 {v}", med_n=False)
    for s, rs in [("H2_strata_Q1-Q2", "H2_strata_Q1-Q2"), ("H2_strata_Q3-Q4", "H2_strata_Q3-Q4")]:
        or_sjekk(h2, (h2["modell"] == s) & (h2["variabel"] == "delta_z"),
                 lg, (lg["analyse"] == rs) & (lg["variabel"] == "delta_z"),
                 f"{s}", med_n=False)

    md = pd.read_csv(TAB / "modeller" / "r1_mediering.csv")
    for pym, rm in [("uten_delta", "med_uten_delta"), ("med_delta", "med_med_delta")]:
        t = md[md["modell"] == pym].iloc[0]
        rr = lg[(lg["analyse"] == rm) & (lg["variabel"] == "kvartal_c")].iloc[0]
        sjekk(f"mediering {pym} OR", t["OR_per_kvartal"], rr["OR"], 2e-4)
        sjekk(f"mediering {pym} KI_lav", t["KI_lav"], rr["KI_lav"], 2e-4)
        sjekk(f"mediering {pym} KI_hoy", t["KI_hoy"], rr["KI_hoy"], 2e-4)
    t = md[md["modell"] == "delta_z_paa_kvartal_c_OLS"].iloc[0]
    rr = lg[lg["analyse"] == "delta_z_paa_kvartal"].iloc[0]
    sjekk("mediering OLS beta", t["OR_per_kvartal"], rr["OR"], 1e-4)
    sjekk("mediering OLS KI_lav", t["KI_lav"], rr["KI_lav"], 2e-3)
    sjekk("mediering OLS KI_hoy", t["KI_hoy"], rr["KI_hoy"], 2e-3)

    mo = pd.read_csv(TAB / "modeller" / "r1_moderasjon.csv")
    for an, v, ran, rv_ in [("nivainteraksjon", "delta_z", "nivainteraksjon", "delta_z"),
                            ("nivainteraksjon", "delta_x_niva", "nivainteraksjon", "dxn"),
                            ("kjonnsinteraksjon", "delta_z", "kjonnsinteraksjon", "delta_z"),
                            ("kjonnsinteraksjon", "delta_x_kvinne", "kjonnsinteraksjon", "dxk")]:
        or_sjekk(mo, (mo["analyse"] == an) & (mo["variabel"] == v),
                 lg, (lg["analyse"] == ran) & (lg["variabel"] == rv_), f"{an} {v}", med_n=False)
    for t_ in ["lav", "midt", "hoy"]:
        or_sjekk(mo, (mo["analyse"] == f"nivastrata_{t_}") & (mo["variabel"] == "delta_z"),
                 lg, (lg["analyse"] == f"nivastrata_{t_}") & (lg["variabel"] == "delta_z"),
                 f"nivastrata {t_}")
    for kj in ["M", "F"]:
        or_sjekk(mo, (mo["analyse"] == f"kjonnsstrata_{kj}") & (mo["variabel"] == "delta_z"),
                 lg, (lg["analyse"] == f"kjonnsstrata_{kj}") & (lg["variabel"] == "delta_z"),
                 f"kjonnsstrata {kj}")
    for q in ["dq_Q2", "dq_Q3", "dq_Q4", "dq_Q5"]:
        or_sjekk(mo, (mo["analyse"] == "delta_kvintiler_vs_Q1") & (mo["variabel"] == q),
                 lg, (lg["analyse"] == "kvintiler") & (lg["variabel"] == q),
                 f"kvintil {q}", med_n=False)
    for k in ["A", "B"]:
        or_sjekk(mo, (mo["analyse"] == f"fast_vindu_kohort_{k}") & (mo["variabel"] == "delta_z"),
                 lg, (lg["analyse"] == f"fast_vindu_{k}") & (lg["variabel"] == "delta_z"),
                 f"fast vindu {k}", med_n=False)

    sw = pd.read_csv(TAB / "modeller" / "r1_switcher_flyt.csv", index_col=0)["verdi"]
    rr = lg[(lg["analyse"] == "switcher_inklusiv") & (lg["variabel"] == "delta_bg2_z")].iloc[0]
    sjekk("switcher n", sw["inklusiv_n"], rr["n"], 0)
    sjekk("switcher hendelser", sw["inklusiv_hendelser"], rr["hendelser"], 0)
    sjekk("switcher OR", sw["inklusiv_OR"], rr["OR"], 1e-3)
    lo, hi = str(sw["inklusiv_KI"]).replace("–", "-").split("-")
    sjekk("switcher KI_lav", lo, rr["KI_lav"], 1e-3)
    sjekk("switcher KI_hoy", hi, rr["KI_hoy"], 1e-3)

    rob = pd.read_csv(TAB / "robusthet" / "robusthet_or.csv")
    kart = [("eksponeringsvariant", "delta_z", "eksvar_delta_z", "delta_z"),
            ("eksponeringsvariant", "delta_max_z", "eksvar_delta_max_z", "delta_max_z"),
            ("eksponeringsvariant", "delta_all_z", "eksvar_delta_all_z", "delta_all_z"),
            ("eksponeringsvariant", "delta_vind_z", "eksvar_delta_vind_z", "delta_vind_z"),
            ("eksponeringsvariant", "delta_bg2_z", "eksvar_delta_bg2_z", "delta_bg2_z"),
            ("eksponeringsvariant", "delta_nk_1314_z", "eksvar_delta_nk_z", "delta_nk_z"),
            ("uten_covid_kull", "delta_z", "uten_covid_kull", "delta_z"),
            ("covid_interaksjon", "delta_x_covid", "covid_interaksjon", "dxc"),
            ("k_minst_2", "delta_z", "k_minst_2", "delta_z"),
            ("kohort_A", "delta_z", "kohort_A", "delta_z"),
            ("kohort_B", "delta_z", "kohort_B", "delta_z")]
    for an, eks, ran, rv_ in kart:
        sel = (rob["analyse"] == an) & (rob["eksponering"] == eks)
        or_sjekk(rob.rename(columns={"eksponering": "variabel"}), sel,
                 lg, (lg["analyse"] == ran) & (lg["variabel"] == rv_), f"rob {an} {eks}")
    for utf, ran in [("senior_min1", "utfall_min1"), ("senior_20_21", "utfall_20_21")]:
        sel = (rob["analyse"] == "utfallsvariant") & (rob["utfall"] == utf)
        or_sjekk(rob.rename(columns={"eksponering": "variabel"}), sel,
                 lg, (lg["analyse"] == ran) & (lg["variabel"] == "delta_z"),
                 f"rob utfall {utf}")
    sel = rob["analyse"] == "utfallsvariant_inkl_2006"
    or_sjekk(rob.rename(columns={"eksponering": "variabel"}), sel,
             lg, (lg["analyse"] == "aktiv18_inkl_2006") & (lg["variabel"] == "delta_z"),
             "rob aktiv18")

    cox_py = pd.read_csv(TAB / "robusthet" / "cox_landmark.csv")
    cox_r = pd.read_csv(R / "cox.csv")
    for v in ["delta_z", "niva_w1_z", "vol1314_g", "vol1516_g", "k13", "k15", "kvinne"]:
        t = cox_py[cox_py["covariate"] == v].iloc[0]
        rr = cox_r[cox_r["variabel"] == v].iloc[0]
        sjekk(f"cox {v} HR", t["exp(coef)"], rr["HR"], 2e-3)
        sjekk(f"cox {v} KI_lav", t["exp(coef) lower 95%"], rr["KI_lav"], 2e-3)
        sjekk(f"cox {v} KI_hoy", t["exp(coef) upper 95%"], rr["KI_hoy"], 2e-3)

    ev_py = pd.read_csv(TAB / "robusthet" / "e_verdi.csv").iloc[0]
    ev_r = pd.read_csv(R / "everdi.csv").iloc[0]
    sjekk("E-verdi punkt", ev_py["E_verdi_punkt"], ev_r["E_punkt"], 0.02)
    sjekk("E-verdi grense", ev_py["E_verdi_KI_grense"], ev_r["E_grense"], 0.02)

    sd_py = pd.read_csv(TAB / "modeller" / "r1_sd_og_andeler.csv", index_col=0)["verdi"]
    sd_r = pd.read_csv(R / "sd_andeler.csv").iloc[0]
    sjekk("sd delta", sd_py["sd_delta_poeng_pooled"], sd_r["sd_delta"], 0.2)
    lo, hi = str(sd_py["sd_delta_poeng_cellespenn"]).replace("–", "-").split("-")
    sjekk("sd delta cellemin", lo, sd_r["sd_delta_min"], 1)
    sjekk("sd delta cellemaks", hi, sd_r["sd_delta_max"], 1)
    sjekk("sd niva", sd_py["sd_niva_poeng"], sd_r["sd_niva"], 0.2)
    sjekk("sd vol1314", sd_py["sd_vol1314_dager"], sd_r["sd_v1314"], 0.1)
    sjekk("sd vol1516", sd_py["sd_vol1516_dager"], sd_r["sd_v1516"], 0.1)
    sjekk("negativ delta dropouts", sd_py["andel_negativ_delta_dropouts"], sd_r["neg_drop"], 1e-3)
    sjekk("negativ delta retainers", sd_py["andel_negativ_delta_retainers"], sd_r["neg_ret"], 1e-3)
    sjekk("kvartal Q1", sd_py["kvartal_Q1"], sd_r["q1"], 1e-3)
    sjekk("kvartal Q4", sd_py["kvartal_Q4"], sd_r["q4"], 1e-3)

    # ---- revisjon r2 (audit 30.10.2026): alle størrelser er deterministiske, også like mange
    # resultater (eksakt forventning), så toleransene er de samme som over
    ad = pd.read_csv(HERE.parent / "data_private" / "analysedata.csv", low_memory=False)
    prim = ad[ad["kohort_primar"] & ad["skaarbar"] & ~ad["liten_gruppecelle"]]
    rl = pd.read_csv(HERE.parent / "data_private" / "r_delta_lik_rader.csv")
    mm = prim[["athlete_id", "delta_lik"]].merge(rl, on="athlete_id", how="outer", indicator=True)
    sjekk("like mange: rader bare i én implementasjon", 0, (mm["_merge"] != "both").sum(), 0)
    sjekk("like mange: maks |Δ_lik py − R|", 0, (mm["delta_lik_x"] - mm["delta_lik_y"]).abs().max(), 1e-6)
    dl = pd.read_csv(R / "delta_lik.csv").set_index("senior")
    for s in [0, 1]:
        g = prim.loc[prim["senior"] == s, "delta_lik"]
        sjekk(f"like mange median senior={s}", g.median(), dl.at[s, "median_lik"], 1e-6)
        sjekk(f"like mange andel negativ senior={s}", (g < 0).mean(), dl.at[s, "andel_neg_lik"], 1e-12)

    fs = pd.read_csv(TAB / "modeller" / "r2_h1_folsomhet.csv")
    for an, ran, rv_ in [("like_mange_resultater", "r2_like_mange", "delta_lik_z"),
                         ("k13_og_k15_minst_3", "r2_k_minst_3", "delta_z"),
                         ("splines_k_og_volum", "r2_splines", "delta_z"),
                         ("bare_utendors", "r2_bare_utendors", "dx_z"),
                         ("ovelsesjusterte_poeng", "r2_ovelsesjustert", "dx_z"),
                         ("tidlig_niva_per_100p_gitt_senere", "r2_l1l2", "l1"),
                         ("senere_niva_per_100p_gitt_tidlig", "r2_l1l2", "l2")]:
        sel_r = (lg["analyse"] == ran) & (lg["variabel"] == rv_)
        or_sjekk(fs, fs["analyse"] == an, lg, sel_r, f"r2 {an}")
        sjekk(f"r2 {an} hendelser", fs.loc[fs["analyse"] == an, "hendelser"].iloc[0],
              lg.loc[sel_r, "hendelser"].iloc[0], 0)

    mr = pd.read_csv(TAB / "modeller" / "r2_mediering.csv").set_index("storrelse")
    for st, ran, tol in [("a_sti_ubetinget_SD_per_kvartal", "delta_z_paa_kvartal", 1e-6),
                         ("a_sti_betinget_M1_SD_per_kvartal", "r2_a_sti_betinget", 1e-6),
                         ("niva_1314_SD_per_kvartal", "r2_niva_per_kvartal", 1e-6),
                         ("kvartal_OR_bare_M0", "r2_kvartal_M0", 2e-4)]:
        t, rr = mr.loc[st], lg[(lg["analyse"] == ran) & (lg["variabel"] == "kvartal_c")].iloc[0]
        sjekk(f"r2 {st}", t["estimat"], rr["OR"], tol)
        sjekk(f"r2 {st} ki_lav", t["ki_lav"], rr["KI_lav"], tol)
        sjekk(f"r2 {st} ki_hoy", t["ki_hoy"], rr["KI_hoy"], tol)
        sjekk(f"r2 {st} n", t["n"], rr["n"], 0)

    nt = pd.read_csv(TAB / "modeller" / "r2_nivatertiler.csv")
    ntr = pd.read_csv(R / "nivatertiler.csv")
    for utv, pre, inter in [("alle", "nivastrata_", "nivainteraksjon"),
                            ("k_minst_3", "r2_nivastrata_k3_", "r2_nivainteraksjon_k3")]:
        for t_ in ["lav", "midt", "hoy"]:
            sel = (nt["utvalg"] == utv) & (nt["tertil"] == t_)
            or_sjekk(nt, sel, lg, (lg["analyse"] == pre + t_) & (lg["variabel"] == "delta_z"), f"r2 nivå {utv} {t_}")
            rt = ntr[(ntr["utvalg"] == utv) & (ntr["ntert"] == t_)].iloc[0]
            sjekk(f"r2 nivå {utv} {t_} median k15", nt.loc[sel, "median_k15"].iloc[0], rt["median_k15"], 0)
            sjekk(f"r2 nivå {utv} {t_} sd Δz", nt.loc[sel, "sd_delta_z"].iloc[0], rt["sd_delta_z"], 1e-9)
        or_sjekk(nt, (nt["utvalg"] == utv) & (nt["tertil"] == "interaksjon"),
                 lg, (lg["analyse"] == inter) & (lg["variabel"] == "dxn"), f"r2 nivåinteraksjon {utv}")

    kj = pd.read_csv(TAB / "modeller" / "r2_kjonn.csv").set_index("gruppe")
    for g in ["menn", "kvinner"]:
        rr = lg[lg["analyse"] == f"r2_kjonn_{g}"].iloc[0]
        for kol in ["OR", "KI_lav", "KI_hoy"]:
            sjekk(f"r2 kjønn {g} {kol}", kj.at[g, kol], rr[kol], 2e-4)
        sjekk(f"r2 kjønn {g} p interaksjon", kj.at[g, "p_interaksjon"], rr["p"], 1e-4)

    f2 = pd.read_csv(TAB / "manus" / "fig2_data.csv")
    eb = pd.read_csv(R / "exit_baner.csv").set_index("t")
    ev = pd.read_csv(R / "exit_volum.csv").set_index("t")
    for panel, rdf, kol in [("Age-graded performance", eb, "lik"), ("ujustert", eb, "raa"),
                            ("sesongmedian", eb, "med"), ("antall_resultater", eb, "k"),
                            ("Competition volume", ev, "dager")]:
        p = f2[f2["panel"] == panel].set_index("t")
        for t_ in ["T-3", "T-2", "T-1", "T-0"]:
            sjekk(f"exit {panel} {t_} median", p.at[t_, "median"], rdf.at[t_, kol], 1e-6)
            sjekk(f"exit {panel} {t_} n", p.at[t_, "n"], rdf.at[t_, "n"], 0)
    sjekk("exit kandidater", f2["n_kandidater"].iloc[0], ev["n_kandidater"].iloc[0], 0)

    if feil:
        print(f"AVVIK ({len(feil)}):")
        for f in feil:
            print("  -", f)
        sys.exit(1)
    print("ALLE SAMMENLIGNINGER PASSERTE (klubb_klusterrobust og klubb_gee dekkes ikke av R "
          "— klyngemetode-implementasjoner; dokumentert i DATA_AUDIT)")


if __name__ == "__main__":
    main()
