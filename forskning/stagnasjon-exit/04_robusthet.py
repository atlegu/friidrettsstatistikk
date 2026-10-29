"""
04_robusthet.py — A1 «Stagnasjon før exit»: forhåndsdefinert robusthet (ANALYSEPLAN.md §6).

KJØRES IKKE FØR OSF-REGISTRERING (samme sperre som 03_modeller.py).

Innhold: eksponeringsvarianter, covid-følsomhet, k>=2, utfallsvarianter,
kohortreplikasjon A/B, klubbklynger (robuste SE og GEE), landmark-Cox og E-verdi.
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from lifelines import CoxPHFitter

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables" / "robusthet"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

M1_KOL = ["gender", "birth_year", "region", "log_klubbstorrelse",
          "niva_w1_z", "vol1314_g", "vol1516_g", "k13", "k15"]
KATEGORISKE = ["gender", "birth_year", "region"]


def sperre():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kjor", "--post-registration", action="store_true", dest="kjor")
    if not ap.parse_args().kjor or not (HERE / "FRIGITT_FOR_MODELLERING.txt").exists():
        sys.exit("STOPP: robusthetsanalysene kjøres først når planen er frigitt "
                 "(se 03_modeller.py og ANALYSEPLAN.md §7).")


def last():
    d = pd.read_csv(DATA / "analysedata.csv")
    d["region"] = d["region"].fillna("ukjent")
    d["log_klubbstorrelse"] = d["log_klubbstorrelse"].fillna(d["log_klubbstorrelse"].median())
    prim = d[d["kohort_primar"] & d["skaarbar"] & ~d["liten_gruppecelle"]].copy()
    for v in ["vol1314", "vol1516"]:
        mu, sd = prim[v].mean(), prim[v].std()
        d[v + "_g"] = (d[v] - mu) / sd
        prim[v + "_g"] = (prim[v] - mu) / sd
    return d, prim.dropna(subset=["delta_z", "niva_w1_z"])


def design(d, kolonner):
    kat = [k for k in KATEGORISKE if k in kolonner]
    X = pd.get_dummies(d[kolonner], columns=kat, drop_first=True, dtype=float)
    return sm.add_constant(X.astype(float), has_constant="add")


def eksponerings_or(d, eksponering, utfall="senior", cov_type="nonrobust", grupper=None):
    dd = d.dropna(subset=[eksponering]).copy()
    X = design(dd, M1_KOL + [eksponering])
    if cov_type == "cluster":
        m = sm.Logit(dd[utfall], X).fit(disp=0, cov_type="cluster",
                                        cov_kwds={"groups": dd[grupper].fillna("ukjent")})
    else:
        m = sm.Logit(dd[utfall], X).fit(disp=0)
    ci = m.conf_int().loc[eksponering]
    return {"eksponering": eksponering, "utfall": utfall, "n": len(dd),
            "hendelser": int(dd[utfall].sum()), "OR": float(np.exp(m.params[eksponering])),
            "KI_lav": float(np.exp(ci[0])), "KI_hoy": float(np.exp(ci[1])),
            "p": float(m.pvalues[eksponering])}


def e_verdi(or_est, p0):
    """E-verdi for H1-OR; vanlig utfall -> OR konverteres til RR før formelen."""
    rr = or_est / (1 - p0 + p0 * or_est)
    if rr < 1:
        rr = 1 / rr
    return float(rr + np.sqrt(rr * (rr - 1)))


def main():
    sperre()
    TAB.mkdir(parents=True, exist_ok=True)
    alle, prim = last()
    rader = []

    # 1) Eksponeringsvarianter (primærutvalg, utfall senior)
    for eksp in ["delta_z", "delta_max_z", "delta_all_z", "delta_vind_z",
                 "delta_bg2_z", "delta_nk_1314_z"]:
        rader.append({**eksponerings_or(prim, eksp), "analyse": "eksponeringsvariant"})

    # 2) Covid: uten født 2004-2005, og interaksjon med covid_w2
    uten = prim[~prim["birth_year"].isin([2004, 2005])]
    rader.append({**eksponerings_or(uten, "delta_z"), "analyse": "uten_covid_kull"})
    pc = prim.copy()
    pc["covid_w2"] = pc["covid_w2"].astype(float)
    pc["delta_x_covid"] = pc["delta_z"] * pc["covid_w2"]
    X = design(pc, M1_KOL + ["delta_z", "covid_w2", "delta_x_covid"])
    m = sm.Logit(pc["senior"], X).fit(disp=0)
    ci = m.conf_int().loc["delta_x_covid"]
    rader.append({"analyse": "covid_interaksjon", "eksponering": "delta_x_covid",
                  "utfall": "senior", "n": len(pc), "hendelser": int(pc["senior"].sum()),
                  "OR": float(np.exp(m.params["delta_x_covid"])),
                  "KI_lav": float(np.exp(ci[0])), "KI_hoy": float(np.exp(ci[1])),
                  "p": float(m.pvalues["delta_x_covid"])})

    # 3) k >= 2 i begge vinduer
    k2 = prim[(prim["k13"] >= 2) & (prim["k15"] >= 2)]
    rader.append({**eksponerings_or(k2, "delta_z"), "analyse": "k_minst_2"})

    # 4) Utfallsvarianter
    for utfall in ["senior_min1", "senior_20_21"]:
        rader.append({**eksponerings_or(prim, "delta_z", utfall=utfall),
                      "analyse": "utfallsvariant"})
    a18 = alle[alle["skaarbar"] & ~alle["liten_gruppecelle"]].dropna(
        subset=["delta_z", "niva_w1_z"])
    rader.append({**eksponerings_or(a18, "delta_z", utfall="aktiv18"),
                  "analyse": "utfallsvariant_inkl_2006"})

    # 5) Kohortreplikasjon
    for k in ["A", "B"]:
        rader.append({**eksponerings_or(prim[prim["kohort"] == k], "delta_z"),
                      "analyse": f"kohort_{k}"})

    # 6) Klubbklynger: klusterrobuste SE og GEE med utvekslbar korrelasjon
    rader.append({**eksponerings_or(prim, "delta_z", cov_type="cluster", grupper="club_id"),
                  "analyse": "klubb_klusterrobust"})
    Xg = design(prim, M1_KOL + ["delta_z"])
    gee = sm.GEE(prim["senior"], Xg, groups=prim["club_id"].fillna("ukjent"),
                 family=sm.families.Binomial(),
                 cov_struct=sm.cov_struct.Exchangeable()).fit()
    cig = gee.conf_int().loc["delta_z"]
    rader.append({"analyse": "klubb_gee", "eksponering": "delta_z", "utfall": "senior",
                  "n": len(prim), "hendelser": int(prim["senior"].sum()),
                  "OR": float(np.exp(gee.params["delta_z"])),
                  "KI_lav": float(np.exp(cig[0])), "KI_hoy": float(np.exp(cig[1])),
                  "p": float(gee.pvalues["delta_z"])})

    res = pd.DataFrame(rader)
    res.to_csv(TAB / "robusthet_or.csv", index=False)

    # 7) Landmark-Cox: klokke fra fylte 17; sensur for utøvere aktive i 2025/2026
    cx = prim.copy()
    cx["aktiv_naa"] = (cx["birth_year"] + cx["siste_alder"]) >= 2025
    cx["tid"] = np.maximum(cx["siste_alder"] - 16, 0.1)
    cx["hendelse"] = (~cx["aktiv_naa"]).astype(int)
    kov = ["delta_z", "niva_w1_z", "vol1314_g", "vol1516_g", "k13", "k15"]
    cd = cx[["tid", "hendelse"] + kov].assign(kvinne=(cx["gender"] == "F").astype(float))
    cph = CoxPHFitter().fit(cd, duration_col="tid", event_col="hendelse")
    cph.summary.reset_index().to_csv(TAB / "cox_landmark.csv", index=False)
    logger.info(f"Cox: HR per SD fremgang = {np.exp(cph.params_['delta_z']):.3f}")

    # 8) E-verdi for H1
    h1 = res[(res["analyse"] == "eksponeringsvariant") & (res["eksponering"] == "delta_z")].iloc[0]
    p0 = prim["senior"].mean()
    pd.DataFrame([{
        "OR": h1["OR"], "utfallsandel": round(float(p0), 3),
        "E_verdi_punkt": round(e_verdi(h1["OR"], p0), 2),
        "E_verdi_KI_grense": round(e_verdi(h1["KI_lav"] if h1["OR"] > 1 else h1["KI_hoy"], p0), 2),
    }]).to_csv(TAB / "e_verdi.csv", index=False)

    logger.info(f"ferdig; tabeller i {TAB}/")


if __name__ == "__main__":
    main()
