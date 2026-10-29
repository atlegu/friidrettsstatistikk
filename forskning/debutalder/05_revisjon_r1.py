"""
05_revisjon_r1.py — A3: analyser til revisjon etter referee-runde 1.

Retter og supplerer (jf. manus/REFEREE_RUNDE1.md):
  R1-1: H3-landmark reestimert med aktivitet I 17-årssesongen (alder == 17),
        ikke «>=1 resultat ved >=17» (som betinget på fremtiden).
  R1-2: LRT kategorisk mot lineær debutalder (formell test av U-formen).
  R1-3: 17+-sensitivitet begrenset til debut 17-19 + aldersfordeling i 17+.
  R2-3: seniorkonvertering per debutalder x kjønn + kjønnsinteraksjon.
  R1-4: retention-k med per-k-nevnere og Wilson-KI.
  R1-6: full koeffisienttabell for primærmodellen + covid-flagg-variant.

03_modeller.py står urørt som runde 1-dokumentasjon.
Output: tables/modeller/r1_*.csv
"""

import importlib.util
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.proportion import proportion_confint

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables" / "modeller"

spec = importlib.util.spec_from_file_location("m03", HERE / "03_modeller.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

JUST = ["gender", "birth_year", "region", "log_klubbstorrelse"]


def main():
    d = pd.read_csv(DATA / "analysedata.csv")
    d["region"] = d["region"].fillna("ukjent")
    d["log_klubbstorrelse"] = d["log_klubbstorrelse"].fillna(d["log_klubbstorrelse"].median())
    d["debut_kat"] = pd.Categorical(d["debut_alder"].clip(upper=17), categories=range(10, 18))
    arsvol = pd.read_csv(DATA / "arsvolum.csv")
    prim = d[d["kohort_primar"] & d["debut_10_16"]].copy()

    # ---- R1-1: riktig landmark — aktiv i selve 17-årssesongen -------------------------
    aktive17 = set(arsvol.loc[arsvol["alder"] == 17, "athlete_id"])
    prim["aktiv_i_17"] = prim["athlete_id"].isin(aktive17)
    gamle = prim[prim["aktiv17"] == 1]
    nye = prim[prim["aktiv_i_17"]]
    info = []
    info.append({"mål": "landmark gammel def (>=1 res ved >=17)", "n": len(gamle),
                 "seniorer": int(gamle["senior"].sum())})
    info.append({"mål": "landmark ny def (aktiv i 17-årssesongen)", "n": len(nye),
                 "seniorer": int(nye["senior"].sum())})
    info.append({"mål": "seniorer UTENFOR ny landmark (idle ved 17, tilbake senere)",
                 "n": int(prim.loc[~prim["aktiv_i_17"], "senior"].sum()), "seniorer": ""})
    lm = nye.copy()
    lm["vol_16_17_z"] = (lm["vol_16_17"].fillna(0) - lm["vol_16_17"].fillna(0).mean()) \
        / lm["vol_16_17"].fillna(0).std()
    rader = [m03.logit_rader(lm, ["debut_alder", "gender", "birth_year"], "senior",
                             "r1_H3_uten_volum"),
             m03.logit_rader(lm, ["debut_alder", "vol_16_17_z", "gender", "birth_year"],
                             "senior", "r1_H3_med_volum")]
    pd.concat(rader).to_csv(TAB / "r1_h3_landmark.csv", index=False)
    pd.DataFrame(info).to_csv(TAB / "r1_h3_landmark_info.csv", index=False)
    for r in rader:
        t = r[r["variabel"] == "debut_alder"].iloc[0]
        logger.info(f"{t['analyse']}: OR {t['OR']:.3f} [{t['KI_lav']:.3f}, {t['KI_hoy']:.3f}] "
                    f"(n={t['n']}, hendelser={t['hendelser']})")

    # ---- R1-2: LRT kategorisk mot lineær ----------------------------------------------
    Xl = m03.design(prim, ["debut_alder"] + JUST)
    Xk = m03.design(prim, ["debut_kat"] + JUST)
    ml = sm.Logit(prim["senior"], Xl).fit(disp=0)
    mk = sm.Logit(prim["senior"], Xk).fit(disp=0)
    lr = 2 * (mk.llf - ml.llf)
    df = Xk.shape[1] - Xl.shape[1]
    from scipy import stats as scst
    p = float(1 - scst.chi2.cdf(lr, df))
    pd.DataFrame([{"llf_linear": ml.llf, "llf_kategorisk": mk.llf, "LR": round(lr, 2),
                   "df": df, "p": f"{p:.2e}" if p < 0.001 else round(p, 4)}]).to_csv(
        TAB / "r1_lrt.csv", index=False)
    logger.info(f"LRT U-form: LR={lr:.1f}, df={df}, p={p:.2e}")

    # ---- R1-3: 17+ -> debut 17-19, uten utfallsoverlapp --------------------------------
    d1719 = d[d["kohort_primar"] & d["debut_alder"].between(10, 19)].copy()
    d1719["debut_kat2"] = pd.Categorical(
        np.where(d1719["debut_alder"] <= 16, d1719["debut_alder"].astype(int), 17),
        categories=list(range(10, 18)))
    fordeling = (d[d["kohort_primar"] & (d["debut_alder"] >= 17)]
                 .groupby(d["debut_alder"].clip(upper=20)).size())
    r = m03.logit_rader(d1719.drop(columns=["debut_kat"]).rename(columns={"debut_kat2": "debut_kat"}),
                        ["debut_kat"] + JUST, "senior", "r1_debut_17_19")
    r.to_csv(TAB / "r1_debut1719.csv", index=False)
    pd.DataFrame({"debut_alder": fordeling.index, "n": fordeling.values}).to_csv(
        TAB / "r1_debut17plus_fordeling.csv", index=False)
    t = r[r["variabel"].astype(str).str.endswith("_17")].iloc[0]
    logger.info(f"debut 17-19 vs 10: OR {t['OR']:.2f} [{t['KI_lav']:.2f}, {t['KI_hoy']:.2f}]")

    # ---- R2-3: kjønn — konvertering per debutalder x kjønn + interaksjon ---------------
    kj = (prim.groupby(["debut_alder", "gender"])["senior"]
          .agg(n="size", hendelser="sum", andel="mean").reset_index())
    lo, hi = proportion_confint(kj["hendelser"], kj["n"], method="wilson")
    kj["andel_pst"] = (kj["andel"] * 100).round(2)
    kj["ki"] = [f"{l*100:.1f}–{h*100:.1f}" for l, h in zip(lo, hi)]
    kj.drop(columns="andel").to_csv(TAB / "r1_kjonn_konvertering.csv", index=False)
    pi = prim.copy()
    pi["kvinne"] = (pi["gender"] == "F").astype(float)
    pi["debut_x_kvinne"] = pi["debut_alder"] * pi["kvinne"]
    ri = m03.logit_rader(pi, ["debut_alder", "kvinne", "debut_x_kvinne",
                              "birth_year", "region", "log_klubbstorrelse"],
                         "senior", "r1_kjonnsinteraksjon")
    ri.to_csv(TAB / "r1_kjonn_interaksjon.csv", index=False)
    ti = ri[ri["variabel"] == "debut_x_kvinne"].iloc[0]
    logger.info(f"debut x kvinne: OR {ti['OR']:.3f} [{ti['KI_lav']:.3f}, {ti['KI_hoy']:.3f}]")

    # ---- R1-4: retention-k med nevnere og Wilson-KI ------------------------------------
    aktiv_sett = set(zip(arsvol["athlete_id"], arsvol["alder"]))
    rader_k = []
    for da, g in prim.groupby("debut_alder"):
        for k in range(0, 6):
            mulig = g[g["birth_year"] + da + k <= 2025]
            if len(mulig) == 0:
                continue
            treff = sum((a, da + k) in aktiv_sett for a in mulig["athlete_id"])
            l, h = proportion_confint(treff, len(mulig), method="wilson")
            rader_k.append({"debut_alder": int(da), "k": k, "n": len(mulig),
                            "aktive": treff, "andel": round(treff / len(mulig), 4),
                            "ki_lav": round(float(l), 4), "ki_hoy": round(float(h), 4)})
    pd.DataFrame(rader_k).to_csv(TAB / "r1_retention_ci.csv", index=False)

    # ---- R1-6: full koeffisienttabell + covid-flagg ------------------------------------
    Xf = m03.design(prim, ["debut_kat"] + JUST)
    mf = sm.Logit(prim["senior"], Xf).fit(disp=0)
    ci = mf.conf_int()
    pd.DataFrame({"variabel": Xf.columns, "OR": np.exp(mf.params.values),
                  "KI_lav": np.exp(ci[0].values), "KI_hoy": np.exp(ci[1].values),
                  "p": mf.pvalues.values}).round(4).to_csv(
        TAB / "r1_h1_full_koeffisienter.csv", index=False)
    pc = prim.copy()
    pc["covid_debut"] = pc["covid_debut"].astype(float)
    rc = m03.logit_rader(pc, ["debut_alder", "covid_debut"] + JUST, "senior",
                         "r1_med_covid_flagg")
    rc.to_csv(TAB / "r1_covid_flagg.csv", index=False)

    logger.info(f"ferdig; r1-tabeller i {TAB}/")


if __name__ == "__main__":
    main()
