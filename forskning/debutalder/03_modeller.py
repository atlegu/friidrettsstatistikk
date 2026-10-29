"""
03_modeller.py — A3 «Debutalder»: H1-H3 og robusthet (ANALYSEPLAN.md §5).

Kjøres ETTER at analyseplanen er committet (b2b717a). Primærutvalg:
født 2001-2005, debutalder 10-16, kjent kjønn.

Output: tables/modeller/h1_debutalder.csv, h2_cox.csv, h3_landmark.csv,
        robusthet.csv, retention_k.csv, oppsummering.json
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from lifelines import CoxPHFitter

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables" / "modeller"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

JUST = ["gender", "birth_year", "region", "log_klubbstorrelse"]
KAT = ["gender", "birth_year", "region", "debut_kat"]


def design(d, kolonner):
    kat = [k for k in KAT if k in kolonner]
    X = pd.get_dummies(d[kolonner], columns=kat, drop_first=True, dtype=float)
    X = X.loc[:, (X != 0).any(axis=0)]   # fjern tomme kategorier (f.eks. debut 17 i 10-16-utvalget)
    return sm.add_constant(X.astype(float), has_constant="add")


def logit_rader(d, kolonner, utfall, merk, cov_type="nonrobust", grupper=None):
    X = design(d, kolonner)
    if cov_type == "cluster":
        m = sm.Logit(d[utfall], X).fit(disp=0, cov_type="cluster",
                                       cov_kwds={"groups": d[grupper].fillna("ukjent")})
    else:
        m = sm.Logit(d[utfall], X).fit(disp=0)
    ci = m.conf_int()
    ut = pd.DataFrame({"analyse": merk, "utfall": utfall, "n": len(d),
                       "hendelser": int(d[utfall].sum()), "variabel": X.columns,
                       "OR": np.exp(m.params.values),
                       "KI_lav": np.exp(ci[0].values), "KI_hoy": np.exp(ci[1].values),
                       "p": m.pvalues.values})
    return ut[ut["variabel"].str.startswith(("debut", "kvartal"))]


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(DATA / "analysedata.csv")
    d["region"] = d["region"].fillna("ukjent")
    d["log_klubbstorrelse"] = d["log_klubbstorrelse"].fillna(d["log_klubbstorrelse"].median())
    d["debut_kat"] = pd.Categorical(d["debut_alder"].clip(upper=17), categories=range(10, 18))
    prim = d[d["kohort_primar"] & d["debut_10_16"]].copy()
    opp = {"n_prim": len(prim), "seniorer": int(prim["senior"].sum())}
    logger.info(f"primærutvalg {len(prim)} ({opp['seniorer']} seniorer)")

    # ---- H1: kategorisk (ref 10) og lineær trend ---------------------------------------
    rader = [logit_rader(prim, ["debut_kat"] + JUST, "senior", "H1_kategorisk"),
             logit_rader(prim, ["debut_alder"] + JUST, "senior", "H1_trend"),
             logit_rader(prim, ["debut_alder"] + JUST, "senior", "H1_trend_klubbrobust",
                         cov_type="cluster", grupper="club_id")]
    h1 = pd.concat(rader)
    h1.to_csv(TAB / "h1_debutalder.csv", index=False)
    tr = h1[(h1["analyse"] == "H1_trend") & (h1["variabel"] == "debut_alder")].iloc[0]
    opp["H1_OR_per_aar"] = round(float(tr["OR"]), 3)
    opp["H1_KI"] = [round(float(tr["KI_lav"]), 3), round(float(tr["KI_hoy"]), 3)]
    logger.info(f"H1 trend: OR per +1 års debutalder = {tr['OR']:.3f} "
                f"[{tr['KI_lav']:.3f}, {tr['KI_hoy']:.3f}]")

    # ---- H2: Cox med alder som tidsskala og forsinket inntreden ------------------------
    cx = prim.copy()
    cx["slutt_alder"] = np.maximum(cx["siste_alder"], cx["debut_alder"]) + 0.5
    cx["hendelse"] = (~cx["aktiv_naa"].astype(bool)).astype(int)
    cx["kvinne"] = (cx["gender"] == "F").astype(float)
    cx["kohort_c"] = cx["birth_year"] - cx["birth_year"].mean()
    kov = ["debut_alder", "kvinne", "kohort_c", "log_klubbstorrelse"]
    cd = cx[["slutt_alder", "hendelse", "debut_alder"] + kov[1:]].copy()
    cd["inn_alder"] = cx["debut_alder"].astype(float)
    cph = CoxPHFitter().fit(cd, duration_col="slutt_alder", event_col="hendelse",
                            entry_col="inn_alder")
    cph.summary.reset_index().to_csv(TAB / "h2_cox.csv", index=False)
    hr = float(np.exp(cph.params_["debut_alder"]))
    lo, hi = np.exp(cph.confidence_intervals_.loc["debut_alder"])
    opp["H2_HR_per_aar"] = round(hr, 3)
    opp["H2_KI"] = [round(float(lo), 3), round(float(hi), 3)]
    logger.info(f"H2 alders-Cox: HR per +1 års debutalder = {hr:.3f} [{lo:.3f}, {hi:.3f}]")

    # ---- H3: landmark ved 17 -----------------------------------------------------------
    lm = prim[(prim["aktiv17"] == 1) & (prim["debut_alder"] <= 16)].copy()
    lm["vol_16_17_z"] = (lm["vol_16_17"].fillna(0) - lm["vol_16_17"].fillna(0).mean()) \
        / lm["vol_16_17"].fillna(0).std()
    rader3 = [logit_rader(lm, ["debut_alder", "gender", "birth_year"], "senior",
                          "H3_uten_volum"),
              logit_rader(lm, ["debut_alder", "vol_16_17_z", "gender", "birth_year"], "senior",
                          "H3_med_volum")]
    h3 = pd.concat(rader3)
    h3.to_csv(TAB / "h3_landmark.csv", index=False)
    for merk in ["H3_uten_volum", "H3_med_volum"]:
        t = h3[(h3["analyse"] == merk) & (h3["variabel"] == "debut_alder")].iloc[0]
        opp[merk] = f"{t['OR']:.3f} [{t['KI_lav']:.3f}, {t['KI_hoy']:.3f}] (n={int(t['n'])})"
        logger.info(f"{merk}: OR per år = {t['OR']:.3f} [{t['KI_lav']:.3f}, {t['KI_hoy']:.3f}]")

    # ---- Robusthet ---------------------------------------------------------------------
    rob = []
    rob.append(logit_rader(prim[~prim["covid_debut"]], ["debut_alder"] + JUST,
                           "senior", "uten_covid_debut"))
    rob.append(logit_rader(prim, ["debut_alder"] + JUST, "senior_min1", "utfall_min1"))
    d1716 = d[d["kohort_primar"] & d["debut_alder"].between(10, 14)].copy()
    rob.append(logit_rader(d1716, ["debut_alder"] + JUST, "aktiv17", "utfall_aktiv17_debut_10_14"))
    prim["vol_debutaar_z"] = (prim["vol_debutaar"].fillna(0) - prim["vol_debutaar"].fillna(0).mean()) \
        / prim["vol_debutaar"].fillna(0).std()
    rob.append(logit_rader(prim, ["debut_alder", "vol_debutaar_z"] + JUST, "senior",
                           "betinget_debutvolum"))
    for navn, maske in [("kohort_2001_2003", prim["birth_year"].between(2001, 2003)),
                        ("kohort_2004_2005", prim["birth_year"].between(2004, 2005))]:
        rob.append(logit_rader(prim[maske], ["debut_alder"] + JUST, "senior", navn))
    med17 = d[d["kohort_primar"] & d["debut_alder"].between(10, 17)].copy()
    rob.append(logit_rader(med17, ["debut_kat"] + JUST, "senior", "med_debut_17plus"))
    pq = prim.dropna(subset=["kvartal"]).copy()
    pq["kvartal_c"] = pq["kvartal"].astype(float) - 2.5
    pq["debut_x_kvartal"] = pq["debut_alder"] * pq["kvartal_c"]
    rob.append(logit_rader(pq, ["debut_alder", "kvartal_c", "debut_x_kvartal"] + JUST,
                           "senior", "kvartal_interaksjon_eksplorativ"))
    pd.concat(rob).to_csv(TAB / "robusthet.csv", index=False)

    # ---- Retention k år etter debut per debutalder -------------------------------------
    arsvol = pd.read_csv(DATA / "arsvolum.csv")
    aktiv_sett = set(zip(arsvol["athlete_id"], arsvol["alder"]))
    rader_k = []
    for da, g in prim.groupby("debut_alder"):
        for k in range(0, 6):
            mulig = g[g["birth_year"] + da + k <= 2025]   # bare fullt observerbare år
            if len(mulig) == 0:
                continue
            andel = np.mean([(a, da + k) in aktiv_sett
                             for a in mulig["athlete_id"]])
            rader_k.append({"debut_alder": int(da), "k": k, "n": len(mulig),
                            "andel_aktiv": round(float(andel), 4)})
    pd.DataFrame(rader_k).to_csv(TAB / "retention_k.csv", index=False)

    with open(TAB / "oppsummering.json", "w") as f:
        json.dump(opp, f, indent=2, ensure_ascii=False)
    logger.info(f"ferdig; tabeller i {TAB}/")


if __name__ == "__main__":
    main()
