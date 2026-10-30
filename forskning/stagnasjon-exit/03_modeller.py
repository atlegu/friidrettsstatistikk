"""
03_modeller.py — A1 «Stagnasjon før exit»: H1-H3 (ANALYSEPLAN.md §5).

KJØRES IKKE FØR OSF-REGISTRERING. Sperre: krever filen OSF_REGISTRERT.txt
(med registrerings-URL på første linje) OG flagget --post-registration.

Primærutvalg: kohort_primar & skaarbar & ~liten_gruppecelle (født 1998-2005).
Utfall: senior (>=2 OK-resultater i samme kalenderår ved alder >=20).
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables" / "modeller"
SEED = 20261029

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# region er NA for alle (meets.krets utfylt for <1 % av stevnene) -> konstant «ukjent», gir null
# dummykolonner og påvirker ingen estimater (audit 30.10.2026, A1-1); står igjen for sporbarhet.
M0_KOL = ["gender", "birth_year", "region", "log_klubbstorrelse"]
M1_KOL = M0_KOL + ["niva_w1_z", "vol1314_g", "vol1516_g", "k13", "k15"]
M2_KOL = M1_KOL + ["delta_z"]
KATEGORISKE = ["gender", "birth_year", "region"]


def sperre():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kjor", "--post-registration", action="store_true", dest="kjor")
    args = ap.parse_args()
    marker = HERE / "FRIGITT_FOR_MODELLERING.txt"
    if not args.kjor or not marker.exists():
        sys.exit("STOPP: H1-H3 kjøres først når planen er frigitt (ANALYSEPLAN.md §7).\n"
                 "Opprett FRIGITT_FOR_MODELLERING.txt (OSF-URL eller dokumentert beslutning) "
                 "og kjør med --kjor.")
    logger.info(f"frigitt: {marker.read_text().strip().splitlines()[0]}")


def last_primaer():
    d = pd.read_csv(DATA / "analysedata.csv")
    d = d[d["kohort_primar"] & d["skaarbar"] & ~d["liten_gruppecelle"]].copy()
    d["region"] = d["region"].fillna("ukjent")
    d["log_klubbstorrelse"] = d["log_klubbstorrelse"].fillna(d["log_klubbstorrelse"].median())
    for v in ["vol1314", "vol1516"]:   # volum: global SD i primærutvalget (jf. OSF §3)
        d[v + "_g"] = (d[v] - d[v].mean()) / d[v].std()
    d = d.dropna(subset=["delta_z", "niva_w1_z"])
    logger.info(f"primærutvalg i modellene: {len(d)} ({int(d['senior'].sum())} seniorer)")
    return d


def design(d, kolonner):
    kat = [k for k in KATEGORISKE if k in kolonner]
    X = pd.get_dummies(d[kolonner], columns=kat, drop_first=True, dtype=float)
    return sm.add_constant(X, has_constant="add")


def logit_or(d, kolonner, utfall="senior", cov_type="nonrobust", grupper=None):
    X = design(d, kolonner)
    kw = {"cov_type": cov_type}
    if grupper is not None:
        kw["cov_kwds"] = {"groups": d[grupper].fillna("ukjent")}
    m = sm.Logit(d[utfall], X).fit(disp=0, **({} if cov_type == "nonrobust" else kw))
    ci = m.conf_int()
    ut = pd.DataFrame({"variabel": X.columns, "koef": m.params.values,
                       "OR": np.exp(m.params.values),
                       "KI_lav": np.exp(ci[0].values), "KI_hoy": np.exp(ci[1].values),
                       "p": m.pvalues.values})
    return m, ut


def cv_auc(d, kolonner, utfall="senior", n_splits=5, n_repeats=20):
    """Gj.sn. AUC per repetisjon (stratifisert k-fold), pluss out-of-fold-prediksjoner
    fra første repetisjon til kalibrering."""
    X = design(d, kolonner).drop(columns="const").to_numpy()
    y = d[utfall].to_numpy()
    rskf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=SEED)
    fold_auc, oof = [], np.full(len(y), np.nan)
    for i, (tr, te) in enumerate(rskf.split(X, y)):
        mod = LogisticRegression(C=1e6, max_iter=5000).fit(X[tr], y[tr])
        p = mod.predict_proba(X[te])[:, 1]
        fold_auc.append(roc_auc_score(y[te], p))
        if i < n_splits:
            oof[te] = p
    per_rep = np.array(fold_auc).reshape(n_repeats, n_splits).mean(axis=1)
    return per_rep, oof


def kalibrering(y, p):
    logit_p = np.log(p / (1 - p))
    m = sm.Logit(y, sm.add_constant(logit_p)).fit(disp=0)
    return {"kalibreringsslope": float(m.params[1]),
            "brier": float(brier_score_loss(y, p))}


def main():
    sperre()
    TAB.mkdir(parents=True, exist_ok=True)
    d = last_primaer()
    oppsummering = {"n": len(d), "seniorer": int(d["senior"].sum())}

    # ---- H1: M0 -> M1 -> M2 -----------------------------------------------------------
    rader = []
    for navn, kolonner in [("M0", M0_KOL), ("M1", M1_KOL), ("M2", M2_KOL)]:
        m, ut = logit_or(d, kolonner)
        ut.insert(0, "modell", navn)
        ut["pseudo_r2"] = m.prsquared
        rader.append(ut)
    pd.concat(rader).to_csv(TAB / "h1_or.csv", index=False)
    h1 = rader[-1].query("variabel == 'delta_z'").iloc[0]
    oppsummering["H1_OR_per_SD"] = round(float(h1["OR"]), 3)
    oppsummering["H1_KI"] = [round(float(h1["KI_lav"]), 3), round(float(h1["KI_hoy"]), 3)]
    logger.info(f"H1: OR per SD = {h1['OR']:.2f} [{h1['KI_lav']:.2f}, {h1['KI_hoy']:.2f}]")

    auc1, _ = cv_auc(d, M1_KOL)
    auc2, oof2 = cv_auc(d, M2_KOL)
    diff = auc2 - auc1
    pd.DataFrame({
        "modell": ["M1", "M2", "M2-M1"],
        "cv_auc": [auc1.mean(), auc2.mean(), diff.mean()],
        "p2_5": [np.percentile(auc1, 2.5), np.percentile(auc2, 2.5), np.percentile(diff, 2.5)],
        "p97_5": [np.percentile(auc1, 97.5), np.percentile(auc2, 97.5), np.percentile(diff, 97.5)],
    }).to_csv(TAB / "h1_auc.csv", index=False)
    oppsummering["H1_delta_AUC"] = round(float(diff.mean()), 4)

    kal = kalibrering(d["senior"].to_numpy(), np.clip(oof2, 1e-6, 1 - 1e-6))
    pd.DataFrame([kal]).to_csv(TAB / "kalibrering.csv", index=False)

    # ---- H2: interaksjon med fødselskvartal --------------------------------------------
    dq = d.dropna(subset=["kvartal"]).copy()
    dq["kvartal_c"] = dq["kvartal"].astype(float) - 2.5
    dq["delta_x_kvartal"] = dq["delta_z"] * dq["kvartal_c"]
    _, ut = logit_or(dq, M2_KOL + ["kvartal_c", "delta_x_kvartal"])
    ut.insert(0, "modell", "H2_interaksjon")
    strat = []
    for navn, del_d in [("Q1-Q2", dq[dq["kvartal"] <= 2]), ("Q3-Q4", dq[dq["kvartal"] >= 3])]:
        _, u = logit_or(del_d, M2_KOL)
        u.insert(0, "modell", f"H2_strata_{navn}")
        strat.append(u[u["variabel"] == "delta_z"])
    pd.concat([ut] + strat).to_csv(TAB / "h2_interaksjon.csv", index=False)
    h2 = ut.query("variabel == 'delta_x_kvartal'").iloc[0]
    oppsummering["H2_interaksjon_OR"] = round(float(h2["OR"]), 3)
    oppsummering["H2_KI"] = [round(float(h2["KI_lav"]), 3), round(float(h2["KI_hoy"]), 3)]
    logger.info(f"H2: interaksjons-OR = {h2['OR']:.3f} [{h2['KI_lav']:.3f}, {h2['KI_hoy']:.3f}] "
                f"(n = {len(dq)})")

    # ---- H3: volum + fremgang mot volum + nivå -----------------------------------------
    felles = ["gender", "vol1314_g", "vol1516_g", "k13", "k15"]
    auc_frem, _ = cv_auc(d, felles + ["delta_z"])
    auc_niva, _ = cv_auc(d, felles + ["niva_w1_z"])
    d3 = auc_frem - auc_niva
    pd.DataFrame({
        "modell": ["volum+fremgang", "volum+niva", "differanse"],
        "cv_auc": [auc_frem.mean(), auc_niva.mean(), d3.mean()],
        "p2_5": [np.percentile(auc_frem, 2.5), np.percentile(auc_niva, 2.5), np.percentile(d3, 2.5)],
        "p97_5": [np.percentile(auc_frem, 97.5), np.percentile(auc_niva, 97.5), np.percentile(d3, 97.5)],
    }).to_csv(TAB / "h3_auc.csv", index=False)
    oppsummering["H3_AUC_diff"] = round(float(d3.mean()), 4)

    with open(TAB / "oppsummering.json", "w") as f:
        json.dump(oppsummering, f, indent=2, ensure_ascii=False)
    logger.info(f"ferdig; tabeller i {TAB}/")


if __name__ == "__main__":
    main()
