"""
08_audit_alternativer.py — A1: alternativene statistikk- og datagjennomgangen (audit 30.10.2026)
ba om, beregnet på de rensede dataene, som grunnlag for Atles beslutning om påstandene.

  A1-1  exit-justerte baner og Δ med like mange poengsatte resultater i sesongene som sammenlignes
        (snitt av 30 tilfeldige trekk av min(k_a, k_b) resultater fra hver sesong) og sesongmedian.
  A1-2  mediering: a-stien betinget på M1-kovariatene og den samlede kvartalsassosiasjonen (M0).
  A1-3  nivåtertiler med k13 >= 3 og k15 >= 3.
  A1-4  E-verdi med RR ≈ √OR (VanderWeele og Ding, vanlig utfall).
  A1-5  tidligere nivå gitt senere nivå (regresjon mot middelet).
  A1-6  kjønn i én modell.
  H1-følsomhet: Δ med like mange resultater, splines for k og volum, k >= 3, bare utendørs,
        øvelsesjusterte poeng (øvelsesforskyvning innen utøversesong, kjønn x gruppe).

Output: tables/audit/*.csv
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
UT = HERE / "tables" / "audit"
UT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE.parent))
from a1_tyrving import beregn_tyrving_poeng, parse_tyrving_xls  # noqa: E402
from rens_felles import fjern_kopier  # noqa: E402

spec = importlib.util.spec_from_file_location("m03", HERE / "03_modeller.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
RNG = np.random.default_rng(20261030)
TREKK = 30


def mean3(p):
    return float(np.mean(sorted(p, reverse=True)[:3])) if len(p) else np.nan


def lik_k(a, b):
    """mean3(b) − mean3(a) med like mange resultater fra hver liste, snitt over trekk."""
    n = min(len(a), len(b))
    return float(np.mean([mean3(list(RNG.choice(b, n, replace=False)))
                          - mean3(list(RNG.choice(a, n, replace=False))) for _ in range(TREKK)]))


def boot_median(x, n=2000):
    x = np.asarray(x)
    b = [np.median(RNG.choice(x, len(x))) for _ in range(n)]
    return float(np.median(x)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def poengrader(base):
    """Poengsatte OK-resultater 13-19 år i utøverens hovedgruppe (elektronisk), med innendørsflagg."""
    r = pd.read_csv(DATA / "resultater.csv", parse_dates=["date"], low_memory=False)
    r, _ = fjern_kopier(r)
    r = r.drop(columns=["birth_year"]).merge(base[["athlete_id", "birth_year", "gender", "hovedgruppe"]],
                                             on="athlete_id")
    r["alder"] = r["date"].dt.year - r["birth_year"]
    r = r[(r["status"] == "OK") & r["alder"].between(13, 19)
          & (r["is_manual_time"].astype(str) != "True") & (r["event_category"] == r["hovedgruppe"])].copy()
    me = pd.read_csv(DATA / "meets.csv").rename(columns={"id": "meet_id"})
    r = r.merge(me[["meet_id", "indoor"]], on="meet_id", how="left")
    r["inne"] = r["indoor"].astype(str) == "True"
    tab = parse_tyrving_xls()
    r["p"] = [beregn_tyrving_poeng(pv, k, rt, g, a, tab) for pv, k, rt, g, a in
              zip(r["performance_value"], r["event_code"], r["result_type"], r["gender"], r["alder"])]
    return r[r["p"].notna()].copy()


def exit_baner(base, sc):
    prim = base[base["prim"]]
    ex = prim[(~prim["aktiv_naa"]) & prim["siste_alder"].between(16, 19)]
    lister = sc.groupby(["athlete_id", "alder"])["p"].agg(list).to_dict()
    rader = []
    for _, u in ex.iterrows():
        aldre = [int(u["siste_alder"]) - k for k in (3, 2, 1, 0)]
        if aldre[0] < 13:
            continue
        L = [lister.get((u["athlete_id"], a)) for a in aldre]
        if any(x is None for x in L):
            continue
        rader.append({"k": [len(x) for x in L], "m3": [mean3(x) - mean3(L[0]) for x in L],
                      "lik": [lik_k(L[0], x) for x in L],
                      "med": [float(np.median(x) - np.median(L[0])) for x in L]})
    ut = []
    for j, t in enumerate(["T-3", "T-2", "T-1", "T0"]):
        rad = {"t": t, "n": len(rader), "median_k": float(np.median([x["k"][j] for x in rader]))}
        for nokkel, navn in [("m3", "rapportert"), ("lik", "like_mange"), ("med", "sesongmedian")]:
            m, lo, hi = boot_median([x[nokkel][j] for x in rader])
            rad.update({navn: m, f"{navn}_ki_lav": lo, f"{navn}_ki_hoy": hi})
        ut.append(rad)
    return pd.DataFrame(ut)


def delta_lik_k(base, sc):
    w = sc[sc["alder"].between(13, 16)]
    l1 = w[w["alder"] <= 14].groupby("athlete_id")["p"].agg(list)
    l2 = w[w["alder"] >= 15].groupby("athlete_id")["p"].agg(list)
    d = {a: lik_k(l1[a], l2[a]) for a in base.loc[base["prim"], "athlete_id"] if a in l1.index and a in l2.index}
    return pd.Series(d)


def standardiser(d, kol):
    g = d.groupby(["gender", "hovedgruppe"])[kol]
    return (d[kol] - g.transform("mean")) / g.transform("std")


def h1_or(d, kol="delta_z", ekstra=None):
    dd = d.dropna(subset=[kol]).copy()
    _, ut = m03.logit_or(dd, [c for c in m03.M1_KOL] + [kol] + (ekstra or []))
    t = ut[ut["variabel"] == kol].iloc[0]
    return {"OR": t["OR"], "KI_lav": t["KI_lav"], "KI_hoy": t["KI_hoy"], "n": len(dd),
            "hendelser": int(dd["senior"].sum())}


def delta_fra(sc, base, w1=(13, 14), w2=(15, 16)):
    a = sc[sc["alder"].between(*w1)].groupby("athlete_id")["p"].agg(list).map(mean3)
    b = sc[sc["alder"].between(*w2)].groupby("athlete_id")["p"].agg(list).map(mean3)
    return base["athlete_id"].map(b - a)


def ovelsesjustert(sc):
    """Trekk fra øvelsesforskyvningen (FE for utøversesong + øvelse, innen kjønn x gruppe)."""
    sc = sc.copy()
    sc["just"] = np.nan
    for (_, _), g in sc.groupby(["gender", "hovedgruppe"]):
        ov = pd.get_dummies(g["event_code"], dtype=float)
        if ov.shape[1] < 2:
            sc.loc[g.index, "just"] = g["p"]
            continue
        ref = g["event_code"].value_counts().index[0]
        ov = ov.drop(columns=[ref])
        celle = g["athlete_id"] + "_" + g["alder"].astype(str)
        yd = g["p"] - g.groupby(celle)["p"].transform("mean")
        Xd = ov - ov.groupby(celle).transform("mean")
        b = np.linalg.lstsq(Xd.to_numpy(), yd.to_numpy(), rcond=None)[0]
        forsk = pd.Series(b, index=ov.columns).reindex(g["event_code"]).fillna(0).to_numpy()
        sc.loc[g.index, "just"] = g["p"] - forsk
    return sc.assign(p=sc["just"])


def main():
    base = pd.read_csv(DATA / "analysedata.csv")
    base["prim"] = base["kohort_primar"] & base["skaarbar"] & ~base["liten_gruppecelle"]
    base["aktiv_naa"] = (base["birth_year"] + base["siste_alder"]) >= 2025
    sc = poengrader(base)

    exit_baner(base, sc).to_csv(UT / "a1_exit_like_mange.csv", index=False)
    logger.info("exit-baner ferdig")

    d = m03.last_primaer()
    prim_ids = set(d["athlete_id"])
    # Δ med like mange resultater; tabell 1-størrelser
    dl = delta_lik_k(base, sc)
    d["delta_lik"] = d["athlete_id"].map(dl)
    d["delta_lik_z"] = standardiser(d, "delta_lik")
    t1 = []
    for s, g in d.groupby("senior"):
        t1.append({"senior": s, "median_delta": g["delta"].median(), "median_delta_lik": g["delta_lik"].median(),
                   "andel_neg": (g["delta"] < 0).mean(), "andel_neg_lik": (g["delta_lik"] < 0).mean(),
                   "median_k13": g["k13"].median(), "median_k15": g["k15"].median(), "n": len(g)})
    pd.DataFrame(t1).to_csv(UT / "a1_tabell1_like_mange.csv", index=False)

    rader = [{"analyse": "primaer", **h1_or(d)}, {"analyse": "delta_like_mange", **h1_or(d, "delta_lik_z")}]
    k3 = d[(d["k13"] >= 3) & (d["k15"] >= 3)]
    rader.append({"analyse": "k13_og_k15_minst_3", **h1_or(k3)})
    # splines for antall resultater og volum
    ds = d.copy()
    f = ("senior ~ C(gender) + C(birth_year) + log_klubbstorrelse + niva_w1_z + delta_z"
         " + bs(k13, df=4) + bs(k15, df=4) + bs(vol1314_g, df=4) + bs(vol1516_g, df=4)")
    m = smf.logit(f, data=ds).fit(disp=0)
    ci = m.conf_int().loc["delta_z"]
    rader.append({"analyse": "splines_k_og_volum", "OR": np.exp(m.params["delta_z"]),
                  "KI_lav": np.exp(ci[0]), "KI_hoy": np.exp(ci[1]), "n": len(ds), "hendelser": int(ds["senior"].sum())})
    # bare utendørs og øvelsesjusterte poeng (Δ bygget på nytt fra resultatradene)
    for navn, s2 in [("bare_utendors", sc[~sc["inne"]]), ("ovelsesjusterte_poeng", ovelsesjustert(sc))]:
        dd = d.copy()
        dd["dx"] = delta_fra(s2[s2["athlete_id"].isin(prim_ids)], dd)
        dd["dx_z"] = standardiser(dd, "dx")
        rader.append({"analyse": navn, **h1_or(dd, "dx_z")})
    pd.DataFrame(rader).to_csv(UT / "a1_h1_folsomhet.csv", index=False)
    logger.info("H1-følsomhet ferdig")

    # mediering
    dq = d.dropna(subset=["kvartal"]).copy()
    dq["kvartal_c"] = dq["kvartal"].astype(float) - 2.5
    X = m03.design(dq, m03.M1_KOL + ["kvartal_c"])
    a_bet = sm.OLS(dq["delta_z"], X).fit(cov_type="cluster", cov_kwds={"groups": dq["club_id"].fillna("ukjent")})
    a_ubet = sm.OLS(dq["delta_z"], sm.add_constant(dq["kvartal_c"])).fit(
        cov_type="cluster", cov_kwds={"groups": dq["club_id"].fillna("ukjent")})
    _, tot = m03.logit_or(dq, m03.M0_KOL + ["kvartal_c"])
    t = tot[tot["variabel"] == "kvartal_c"].iloc[0]
    med = [{"storrelse": "a_sti_ubetinget_SD_per_kvartal", "estimat": a_ubet.params["kvartal_c"],
            "ki_lav": a_ubet.conf_int().loc["kvartal_c"][0], "ki_hoy": a_ubet.conf_int().loc["kvartal_c"][1],
            "p": a_ubet.pvalues["kvartal_c"]},
           {"storrelse": "a_sti_betinget_M1_SD_per_kvartal", "estimat": a_bet.params["kvartal_c"],
            "ki_lav": a_bet.conf_int().loc["kvartal_c"][0], "ki_hoy": a_bet.conf_int().loc["kvartal_c"][1],
            "p": a_bet.pvalues["kvartal_c"]},
           {"storrelse": "kvartal_OR_bare_M0", "estimat": t["OR"], "ki_lav": t["KI_lav"], "ki_hoy": t["KI_hoy"],
            "p": t["p"]},
           {"storrelse": "niva_1314_SD_per_kvartal",
            "estimat": sm.OLS(dq["niva_w1_z"], sm.add_constant(dq["kvartal_c"])).fit().params["kvartal_c"],
            "ki_lav": np.nan, "ki_hoy": np.nan, "p": np.nan}]
    pd.DataFrame(med).to_csv(UT / "a1_mediering.csv", index=False)

    # nivåtertiler, alle og k >= 3
    d["nivatert"] = pd.qcut(d["niva_w1_z"], 3, labels=["lav", "midt", "hoy"])
    ter = []
    for navn, dd in [("alle", d), ("k_minst_3", d[(d["k13"] >= 3) & (d["k15"] >= 3)])]:
        for tt, g in dd.groupby("nivatert", observed=True):
            ter.append({"utvalg": navn, "tertil": tt, **h1_or(g), "sd_delta_z": g["delta_z"].std(),
                        "median_k15": g["k15"].median()})
        di = dd.copy()
        di["dxn"] = di["delta_z"] * di["niva_w1_z"]
        _, u = m03.logit_or(di, m03.M2_KOL + ["dxn"])
        r = u[u["variabel"] == "dxn"].iloc[0]
        ter.append({"utvalg": navn, "tertil": "interaksjon", "OR": r["OR"], "KI_lav": r["KI_lav"],
                    "KI_hoy": r["KI_hoy"], "n": len(di)})
    pd.DataFrame(ter).to_csv(UT / "a1_nivatertiler.csv", index=False)

    # E-verdi, kjønn, tidligere nivå gitt senere nivå
    h1 = rader[0]
    ev = lambda rr: rr + np.sqrt(rr * (rr - 1))  # noqa: E731
    p0 = d["senior"].mean()
    andre = [{"storrelse": "E_verdi_papirets_formel", "estimat": ev(h1["OR"] / (1 - p0 + p0 * h1["OR"])),
              "grense": ev(h1["KI_lav"] / (1 - p0 + p0 * h1["KI_lav"]))},
             {"storrelse": "E_verdi_rot_OR", "estimat": ev(np.sqrt(h1["OR"])), "grense": ev(np.sqrt(h1["KI_lav"]))}]
    di = d.copy()
    di["kvinne"] = (di["gender"] == "F").astype(float)
    di["dxk"] = di["delta_z"] * di["kvinne"]
    m, u = m03.logit_or(di, m03.M2_KOL + ["dxk"])
    b, V = m.params, m.cov_params()
    for navn, lin in [("OR_menn_interaksjonsmodell", ["delta_z"]), ("OR_kvinner_interaksjonsmodell", ["delta_z", "dxk"])]:
        est = float(sum(b[x] for x in lin))
        se = float(np.sqrt(sum(V.loc[x, y] for x in lin for y in lin)))
        andre.append({"storrelse": navn, "estimat": np.exp(est), "ki_lav": np.exp(est - 1.96 * se),
                      "ki_hoy": np.exp(est + 1.96 * se), "p_interaksjon": float(m.pvalues["dxk"])})
    dd = d.dropna(subset=["niva_w2"]).copy()
    dd["l1"], dd["l2"] = dd["niva_w1"] / 100, dd["niva_w2"] / 100
    kol = [c for c in m03.M1_KOL if c != "niva_w1_z"] + ["l1", "l2"]
    _, u = m03.logit_or(dd, kol)
    for v, navn in [("l1", "OR_tidlig_niva_per_100p_gitt_senere"), ("l2", "OR_senere_niva_per_100p_gitt_tidlig")]:
        r = u[u["variabel"] == v].iloc[0]
        andre.append({"storrelse": navn, "estimat": r["OR"], "ki_lav": r["KI_lav"], "ki_hoy": r["KI_hoy"]})
    pd.DataFrame(andre).to_csv(UT / "a1_andre.csv", index=False)
    logger.info(f"ferdig; filer i {UT}/")


if __name__ == "__main__":
    main()
