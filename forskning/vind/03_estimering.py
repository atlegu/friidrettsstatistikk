"""
03_estimering.py — A6 «Vind»: within utøver x sesong-estimering (ANALYSEPLAN.md §4).

Primærspesifikasjon per øvelse: resultat = FE(utøver x år) + beta*vind
+ månedsdummyer + rundedummyer, estimert ved demeaning innen celler,
klyngerobuste SE på utøver. Effekter rapporteres som GEVINST per +1 m/s
medvind: sekunder (løp), cm (hopp) og prosent (log-utfall).

Output i tables/estimering/: hoved.csv, alder.csv, niva.csv, asym.csv,
kvad.csv, robusthet.csv, fordel2ms.csv
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as scst

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables" / "estimering"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TIDSKODER = {"60m", "80m", "100m", "150m", "200m"}
MIN_N, MIN_CELLER = 300, 100


def dummies(d):
    mnd = pd.get_dummies(d["maaned"].clip(4, 10), prefix="m", drop_first=True, dtype=float)
    rnd = d["runde"].where(d["runde"].isin(d["runde"].value_counts().head(5).index), "annet")
    rnd = pd.get_dummies(rnd, prefix="r", drop_first=True, dtype=float)
    return pd.concat([mnd, rnd], axis=1)


def _gruppesnitt(X, kode, n, antall):
    return np.column_stack([np.bincount(kode, weights=X[:, j], minlength=n)
                            for j in range(X.shape[1])]) / antall[:, None]


def demean(M, grupper, grupper2=None, tol=1e-10, maks=100_000):
    """Within-transformasjon; to-veis ved alternerende projeksjoner når grupper2 er satt.

    To-veis itereres til største gruppesnitt for den første grupperingen er under tol. Den
    tidligere faste grensen på 25 runder konvergerte ikke (det trengs 600-2 300 runder), selv
    om estimatene var like på fire-fem siffer (audit 30.10.2026, funn A6-8).
    """
    M = M.astype(float)
    if grupper2 is None:
        return M - M.groupby(grupper).transform("mean")
    X = M.to_numpy(copy=True)
    a, b = pd.factorize(grupper)[0], pd.factorize(grupper2)[0]
    na, nb = a.max() + 1, b.max() + 1
    ca, cb = np.bincount(a, minlength=na).astype(float), np.bincount(b, minlength=nb).astype(float)
    for runde in range(1, maks + 1):
        X -= _gruppesnitt(X, a, na, ca)[a]
        X -= _gruppesnitt(X, b, nb, cb)[b]
        if runde % 10 == 0 and np.abs(_gruppesnitt(X, a, na, ca)).max() < tol:
            break
    else:
        logger.warning(f"to-veis demeaning konvergerte ikke på {maks} runder")
    return pd.DataFrame(X, index=M.index, columns=M.columns)


def estimer(d, y_kol, vindkolonner=("wind",), meet_fe=False, cluster="athlete_id"):
    """Returnerer koeffisienter for vindkolonnene med klyngerobuste SE."""
    d = d[d["n_i_celle"] >= 2]
    if len(d) < MIN_N or d["celle"].nunique() < MIN_CELLER:
        return None
    M = pd.concat([d[y_kol], d[list(vindkolonner)], dummies(d)], axis=1)
    Md = demean(M, d["celle"], d["meet_id"] if meet_fe else None)
    # absorberte kolonner (f.eks. måned under stevne-FE) er null opp til konvergenstoleransen
    Md = Md.loc[:, Md.abs().max(axis=0) > 1e-6 * M.abs().max(axis=0).replace(0, 1)]
    y = Md[y_kol].to_numpy()
    Xk = [k for k in vindkolonner if k in Md.columns]
    if not Xk:
        return None
    X = Md.drop(columns=[y_kol]).to_numpy()
    navn = Md.drop(columns=[y_kol]).columns.tolist()
    m = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": d[cluster]})
    ut = {}
    for k in Xk:
        i = navn.index(k)
        ut[k] = (float(m.params[i]), float(m.bse[i]))
    ut["n"] = len(d)
    ut["celler"] = int(d["celle"].nunique())
    ut["_modell"] = m
    ut["_navn"] = navn
    return ut


def gevinst(kode, beta, se):
    """Fortegnsjustert gevinst per +1 m/s medvind, med KI."""
    s = -1 if kode in TIDSKODER else 1
    g = s * beta
    return g, g - 1.96 * se, g + 1.96 * se


def rad(kode, res, y_kol, merk, ekstra=None):
    b, se = res["wind"]
    g, lo, hi = gevinst(kode, b, se)
    skala = 100 if (kode not in TIDSKODER and y_kol == "y") else 1   # hopp: m -> cm
    enhet = ("s" if kode in TIDSKODER else "cm") if y_kol == "y" else "%"
    f = (lambda x: x * skala) if y_kol == "y" else (lambda x: -100 * x if kode in TIDSKODER else 100 * x)
    if y_kol == "logy":
        b_, se_ = res["wind"]
        g_, lo_, hi_ = f(b_), None, None
        g_lo, g_hi = sorted([f(b_ - 1.96 * se_), f(b_ + 1.96 * se_)])
        return {"analyse": merk, "event": kode, "enhet": enhet, "gevinst_per_ms": round(g_, 4),
                "ki_lav": round(g_lo, 4), "ki_hoy": round(g_hi, 4),
                "n": res["n"], "celler": res["celler"], **(ekstra or {})}
    return {"analyse": merk, "event": kode, "enhet": enhet,
            "gevinst_per_ms": round(g * skala, 4),
            "ki_lav": round(lo * skala, 4), "ki_hoy": round(hi * skala, 4),
            "n": res["n"], "celler": res["celler"], **(ekstra or {})}


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(DATA / "analyseklar.csv")
    d["logy"] = np.log(d["y"])
    d["wind_pos"] = d["wind"].clip(lower=0)
    d["wind_neg"] = d["wind"].clip(upper=0)
    d["wind2"] = d["wind"] ** 2
    koder = sorted(d["event_code"].unique())

    # ---- Hovedeffekter per øvelse (og per kjønn) ---------------------------------------
    hoved = []
    for kode in koder:
        g = d[d["event_code"] == kode]
        for y_kol in ["y", "logy"]:
            r = estimer(g, y_kol)
            if r:
                hoved.append(rad(kode, r, y_kol, "hoved"))
        for kj in ["M", "F"]:
            r = estimer(g[g["gender"] == kj], "y")
            if r:
                hoved.append(rad(kode, r, "y", f"kjonn_{kj}"))
    pd.DataFrame(hoved).to_csv(TAB / "hoved.csv", index=False)
    logger.info("hovedeffekter ferdig")

    # ---- Skalering: alder x kjønn (H2/H3) ----------------------------------------------
    alder = []
    for kode in koder:
        for kj in ["M", "F"]:
            for band, gg in d[(d["event_code"] == kode) & (d["gender"] == kj)].groupby("aldersband"):
                for y_kol in ["y", "logy"]:
                    r = estimer(gg, y_kol)
                    if r:
                        alder.append(rad(kode, r, y_kol, "alder",
                                         {"kjonn": kj, "aldersband": band}))
    pd.DataFrame(alder).to_csv(TAB / "alder.csv", index=False)
    logger.info("aldersskalering ferdig")

    # ---- Nivåtertiler ------------------------------------------------------------------
    niva = []
    for kode in koder:
        for tert, gg in d[d["event_code"] == kode].groupby("nivatertil"):
            r = estimer(gg, "y")
            if r:
                niva.append(rad(kode, r, "y", "niva", {"tertil": tert}))
    pd.DataFrame(niva).to_csv(TAB / "niva.csv", index=False)

    # ---- Asymmetri (H4) ----------------------------------------------------------------
    asym = []
    for kode in koder:
        g = d[d["event_code"] == kode]
        r = estimer(g, "y", vindkolonner=("wind_pos", "wind_neg"))
        if not r:
            continue
        s = -1 if kode in TIDSKODER else 1
        skala = 1 if kode in TIDSKODER else 100
        bp, sep = r["wind_pos"]
        bn, sen = r["wind_neg"]
        m, navn = r["_modell"], r["_navn"]
        i, j = navn.index("wind_pos"), navn.index("wind_neg")
        diff = m.params[i] - m.params[j]
        se_d = float(np.sqrt(m.cov_params()[i, i] + m.cov_params()[j, j]
                             - 2 * m.cov_params()[i, j]))
        asym.append({"event": kode,
                     "medvind_gevinst_per_ms": round(s * bp * skala, 4),
                     "medvind_ki": f"{s*bp*skala - 1.96*sep*skala:.4f}..{s*bp*skala + 1.96*sep*skala:.4f}",
                     "motvind_kost_per_ms": round(s * bn * skala, 4),
                     "motvind_ki": f"{s*bn*skala - 1.96*sen*skala:.4f}..{s*bn*skala + 1.96*sen*skala:.4f}",
                     "p_lik_stigning": round(float(2 * (1 - scst.norm.cdf(abs(diff / se_d)))), 5)
                     if se_d > 0 else np.nan,
                     "n": r["n"], "celler": r["celler"]})
    pd.DataFrame(asym).to_csv(TAB / "asym.csv", index=False)
    logger.info("asymmetri ferdig")

    # ---- Kvadratisk form ---------------------------------------------------------------
    kvad = []
    for kode in koder:
        r = estimer(d[d["event_code"] == kode], "y", vindkolonner=("wind", "wind2"))
        if r:
            kvad.append({"event": kode, "beta_lin": round(r["wind"][0], 5),
                         "se_lin": round(r["wind"][1], 5),
                         "beta_kvad": round(r["wind2"][0], 5),
                         "se_kvad": round(r["wind2"][1], 5),
                         "n": r["n"], "celler": r["celler"]})
    pd.DataFrame(kvad).to_csv(TAB / "kvad.csv", index=False)

    # ---- Robusthet ---------------------------------------------------------------------
    rob = []
    for kode in koder:
        g = d[d["event_code"] == kode]
        varianter = [
            ("primaer", g, {}),
            ("celler_min3", g[g["n_i_celle"] >= 3], {}),
            ("uten_vind_0", g[g["wind"] != 0], {}),
            ("periode_2011_2019", g[g["aar"] <= 2019], {}),
            ("periode_2021_2026", g[g["aar"] >= 2021], {}),
            ("stevne_fe", g, {"meet_fe": True}),
            ("kluster_stevne", g, {"cluster": "meet_id"}),
        ]
        for navn, gg, kw in varianter:
            r = estimer(gg, "y", **kw)
            if r:
                rob.append(rad(kode, r, "y", navn))
    pd.DataFrame(rob).to_csv(TAB / "robusthet.csv", index=False)
    logger.info("robusthet ferdig")

    # ---- H5: fordelen ved +2,0 m/s, også i within-celle-SD -----------------------------
    sd_celle = (d.assign(dm=lambda x: x["y"] - x.groupby("celle")["y"].transform("mean"))
                .groupby(["event_code", "gender", "aldersband"])["dm"].std()
                .rename("sd_within").reset_index())
    a = pd.DataFrame(alder)
    a = a[a["enhet"].isin(["s", "cm"])].merge(
        sd_celle, left_on=["event", "kjonn", "aldersband"],
        right_on=["event_code", "gender", "aldersband"], how="left")
    a["fordel_2ms"] = (2 * a["gevinst_per_ms"]).round(3)
    skala = a["event"].map(lambda k: 1 if k in TIDSKODER else 1 / 100)
    a["fordel_2ms_i_sd"] = (2 * a["gevinst_per_ms"] * skala / a["sd_within"]).round(3)
    a[["event", "kjonn", "aldersband", "enhet", "fordel_2ms", "fordel_2ms_i_sd",
       "n", "celler"]].to_csv(TAB / "fordel2ms.csv", index=False)

    logger.info(f"ferdig; tabeller i {TAB}/")


if __name__ == "__main__":
    main()
