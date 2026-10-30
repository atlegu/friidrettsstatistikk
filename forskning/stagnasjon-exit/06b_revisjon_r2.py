"""
06b_revisjon_r2.py — A1: analysene etter dataauditen 30.10.2026 (endringsrapporten, punkt 6–13).

  - H1-følsomhet: fremgang med like mange resultater (delta_lik, bygget i 01_variabler.py),
    splines for antall resultater og volum, >= 3 poengsatte resultater i begge vinduer, bare
    utendørsresultater, øvelsesjusterte poeng (Tyrving-poengene er ikke sammenlignbare på tvers
    av øvelser: øvelsesforskyvningen innen utøversesong trekkes fra, innen kjønn x gruppe).
  - Regresjon mot middelet: tidligere nivå gitt senere nivå (OR per 100 poeng).
  - Mediering: a-stien ubetinget og betinget på M1-kovariatene, og kvartalsassosiasjonen i M0
    (uten nivå og volum, som fødselskvartalet selv påvirker).
  - Nivåtertiler i hele utvalget og med k13 >= 3 og k15 >= 3, med interaksjonen.
  - Kjønn i én modell (interaksjonsmodellen): OR for menn og kvinner.

(Exit-banene med like mange resultater lages i 05_figurer_tabeller.py, E-verdien i 04_robusthet.py.)

Output: tables/modeller/r2_*.csv
"""

import importlib.util
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

HERE = Path(__file__).parent
DATA = HERE / "data_private"
MOD = HERE / "tables" / "modeller"
sys.path.insert(0, str(HERE.parent))
from a1_tyrving import beregn_tyrving_poeng, parse_tyrving_xls  # noqa: E402
from rens_felles import fjern_kopier  # noqa: E402

spec = importlib.util.spec_from_file_location("m03", HERE / "03_modeller.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def mean3(p):
    return float(np.mean(sorted(p, reverse=True)[:3])) if len(p) else np.nan


def poengrader(base):
    """Poengsatte OK-resultater 13–16 år i utøverens hovedgruppe (elektronisk), med innendørsflagg."""
    r = pd.read_csv(DATA / "resultater.csv", parse_dates=["date"], low_memory=False)
    r, _ = fjern_kopier(r)
    r = r.drop(columns=["birth_year"]).merge(base[["athlete_id", "birth_year", "gender", "hovedgruppe"]],
                                             on="athlete_id")
    r["alder"] = r["date"].dt.year - r["birth_year"]
    r = r[(r["status"] == "OK") & r["alder"].between(13, 16)
          & (r["is_manual_time"].astype(str) != "True") & (r["event_category"] == r["hovedgruppe"])].copy()
    me = pd.read_csv(DATA / "meets.csv").rename(columns={"id": "meet_id"})
    r = r.merge(me[["meet_id", "indoor"]], on="meet_id", how="left")
    r["inne"] = r["indoor"].astype(str) == "True"
    tab = parse_tyrving_xls()
    r["p"] = [beregn_tyrving_poeng(pv, k, rt, g, a, tab) for pv, k, rt, g, a in
              zip(r["performance_value"], r["event_code"], r["result_type"], r["gender"], r["alder"])]
    return r[r["p"].notna()].copy()


def standardiser(d, kol):
    g = d.groupby(["gender", "hovedgruppe"])[kol]
    return (d[kol] - g.transform("mean")) / g.transform("std")


def or_rad(analyse, d, kol, ekstra=None):
    dd = d.dropna(subset=[kol]).copy()
    _, ut = m03.logit_or(dd, list(m03.M1_KOL) + [kol] + (ekstra or []))
    t = ut[ut["variabel"] == kol].iloc[0]
    return {"analyse": analyse, "OR": t["OR"], "KI_lav": t["KI_lav"], "KI_hoy": t["KI_hoy"],
            "n": len(dd), "hendelser": int(dd["senior"].sum())}


def delta_fra(sc, base):
    a = sc[sc["alder"] <= 14].groupby("athlete_id")["p"].agg(list).map(mean3)
    b = sc[sc["alder"] >= 15].groupby("athlete_id")["p"].agg(list).map(mean3)
    return base["athlete_id"].map(b - a)


def ovelsessett(ev, celle):
    """Sammenhengende sett av øvelser som deler minst én utøversesong (union-find)."""
    forelder = {e: e for e in ev.unique()}

    def rot(e):
        while forelder[e] != e:
            forelder[e] = forelder[forelder[e]]
            e = forelder[e]
        return e
    for koder in ev.groupby(celle.to_numpy()).unique():
        for e in koder[1:]:
            forelder[rot(e)] = rot(koder[0])
    return ev.map(rot)


def ovelsesjustert(sc):
    """Trekk fra øvelsesforskyvningen (FE for utøversesong + øvelse, innen kjønn x gruppe).

    Forskyvningene er bare identifisert mellom øvelser som deler utøversesonger. Guttenes
    kastredskaper skifter ved 16 år, så kast menn faller i to slike sett (4 og 9 koder; audit
    30.10.2026). Hvert sett sentreres så snittpoengene i settet bevares, i stedet for en
    vilkårlig normering (minste norm i lstsq, utelatt kolonne i R)."""
    sc = sc.copy()
    sc["just"] = np.nan
    for _, g in sc.groupby(["gender", "hovedgruppe"]):
        ov = pd.get_dummies(g["event_code"], dtype=float)
        if ov.shape[1] < 2:
            sc.loc[g.index, "just"] = g["p"]
            continue
        ref = g["event_code"].value_counts().sort_index().idxmax()
        ov = ov.drop(columns=[ref])
        celle = g["athlete_id"] + "_" + g["alder"].astype(str)
        yd = g["p"] - g.groupby(celle)["p"].transform("mean")
        Xd = ov - ov.groupby(celle).transform("mean")
        b = np.linalg.lstsq(Xd.to_numpy(), yd.to_numpy(), rcond=None)[0]
        forsk = pd.Series(b, index=ov.columns).reindex(g["event_code"]).fillna(0).to_numpy()
        sett = ovelsessett(g["event_code"], celle).to_numpy()
        forsk = forsk - pd.Series(forsk).groupby(sett).transform("mean").to_numpy()
        sc.loc[g.index, "just"] = g["p"] - forsk
    return sc.assign(p=sc["just"])


def folsomhet(d, sc):
    rader = [or_rad("primaer", d, "delta_z"), or_rad("like_mange_resultater", d, "delta_lik_z"),
             or_rad("k13_og_k15_minst_3", d[(d["k13"] >= 3) & (d["k15"] >= 3)], "delta_z")]
    f = ("senior ~ C(gender) + C(birth_year) + log_klubbstorrelse + niva_w1_z + delta_z"
         " + bs(k13, df=4) + bs(k15, df=4) + bs(vol1314_g, df=4) + bs(vol1516_g, df=4)")
    m = smf.logit(f, data=d).fit(disp=0)
    ci = m.conf_int().loc["delta_z"]
    rader.append({"analyse": "splines_k_og_volum", "OR": np.exp(m.params["delta_z"]), "KI_lav": np.exp(ci[0]),
                  "KI_hoy": np.exp(ci[1]), "n": len(d), "hendelser": int(d["senior"].sum())})
    ids = set(d["athlete_id"])
    for navn, s2 in [("bare_utendors", sc[~sc["inne"]]), ("ovelsesjusterte_poeng", ovelsesjustert(sc))]:
        dd = d.copy()
        dd["dx"] = delta_fra(s2[s2["athlete_id"].isin(ids)], dd)
        dd["dx_z"] = standardiser(dd, "dx")
        rader.append(or_rad(navn, dd, "dx_z"))
    dd = d.dropna(subset=["niva_w2"]).copy()
    dd["l1"], dd["l2"] = dd["niva_w1"] / 100, dd["niva_w2"] / 100
    _, u = m03.logit_or(dd, [c for c in m03.M1_KOL if c != "niva_w1_z"] + ["l1", "l2"])
    for v, navn in [("l1", "tidlig_niva_per_100p_gitt_senere"), ("l2", "senere_niva_per_100p_gitt_tidlig")]:
        t = u[u["variabel"] == v].iloc[0]
        rader.append({"analyse": navn, "OR": t["OR"], "KI_lav": t["KI_lav"], "KI_hoy": t["KI_hoy"],
                      "n": len(dd), "hendelser": int(dd["senior"].sum())})
    return pd.DataFrame(rader)


def mediering(d):
    dq = d.dropna(subset=["kvartal"]).copy()
    dq["kvartal_c"] = dq["kvartal"].astype(float) - 2.5
    kl = {"groups": dq["club_id"].fillna("ukjent")}
    a_bet = sm.OLS(dq["delta_z"], m03.design(dq, m03.M1_KOL + ["kvartal_c"])).fit(cov_type="cluster", cov_kwds=kl)
    a_ubet = sm.OLS(dq["delta_z"], sm.add_constant(dq["kvartal_c"])).fit(cov_type="cluster", cov_kwds=kl)
    niva = sm.OLS(dq["niva_w1_z"], sm.add_constant(dq["kvartal_c"])).fit(cov_type="cluster", cov_kwds=kl)
    _, tot = m03.logit_or(dq, m03.M0_KOL + ["kvartal_c"])
    t = tot[tot["variabel"] == "kvartal_c"].iloc[0]

    def ols_rad(navn, m):
        ci = m.conf_int().loc["kvartal_c"]
        return {"storrelse": navn, "estimat": m.params["kvartal_c"], "ki_lav": ci[0], "ki_hoy": ci[1],
                "p": m.pvalues["kvartal_c"], "n": int(m.nobs)}

    return pd.DataFrame([ols_rad("a_sti_ubetinget_SD_per_kvartal", a_ubet),
                         ols_rad("a_sti_betinget_M1_SD_per_kvartal", a_bet),
                         ols_rad("niva_1314_SD_per_kvartal", niva),
                         {"storrelse": "kvartal_OR_bare_M0", "estimat": t["OR"], "ki_lav": t["KI_lav"],
                          "ki_hoy": t["KI_hoy"], "p": t["p"], "n": len(dq)}])


def nivatertiler(d):
    d = d.copy()
    d["nivatert"] = pd.qcut(d["niva_w1_z"], 3, labels=["lav", "midt", "hoy"])
    rader = []
    for navn, dd in [("alle", d), ("k_minst_3", d[(d["k13"] >= 3) & (d["k15"] >= 3)])]:
        for tt, g in dd.groupby("nivatert", observed=True):
            rader.append({"utvalg": navn, "tertil": tt, **or_rad("tertil", g, "delta_z"),
                          "sd_delta_z": g["delta_z"].std(), "median_k15": g["k15"].median()})
        di = dd.copy()
        di["dxn"] = di["delta_z"] * di["niva_w1_z"]
        _, u = m03.logit_or(di, m03.M2_KOL + ["dxn"])
        r = u[u["variabel"] == "dxn"].iloc[0]
        rader.append({"utvalg": navn, "tertil": "interaksjon", "analyse": "interaksjon", "OR": r["OR"],
                      "KI_lav": r["KI_lav"], "KI_hoy": r["KI_hoy"], "n": len(di),
                      "hendelser": int(di["senior"].sum())})
    return pd.DataFrame(rader)


def kjonn(d):
    di = d.copy()
    di["kvinne"] = (di["gender"] == "F").astype(float)
    di["dxk"] = di["delta_z"] * di["kvinne"]
    m, _ = m03.logit_or(di, m03.M2_KOL + ["dxk"])
    b, V = m.params, m.cov_params()
    rader = []
    for navn, lin in [("menn", ["delta_z"]), ("kvinner", ["delta_z", "dxk"])]:
        est = float(sum(b[x] for x in lin))
        se = float(np.sqrt(sum(V.loc[x, y] for x in lin for y in lin)))
        rader.append({"gruppe": navn, "OR": np.exp(est), "KI_lav": np.exp(est - 1.96 * se),
                      "KI_hoy": np.exp(est + 1.96 * se), "p_interaksjon": float(m.pvalues["dxk"])})
    return pd.DataFrame(rader)


def main():
    base = pd.read_csv(DATA / "analysedata.csv")
    d = m03.last_primaer()
    sc = poengrader(base[base["athlete_id"].isin(set(d["athlete_id"]))])
    folsomhet(d, sc).to_csv(MOD / "r2_h1_folsomhet.csv", index=False)
    mediering(d).to_csv(MOD / "r2_mediering.csv", index=False)
    nivatertiler(d).to_csv(MOD / "r2_nivatertiler.csv", index=False)
    kjonn(d).to_csv(MOD / "r2_kjonn.csv", index=False)
    logger.info(f"r2-filer i {MOD}/")


if __name__ == "__main__":
    main()
