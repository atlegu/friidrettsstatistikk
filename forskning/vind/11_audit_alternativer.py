"""
11_audit_alternativer.py — A6: alternativene statistikkgjennomgangen (audit 30.10.2026) ba om,
beregnet på de rensede dataene, som grunnlag for Atles beslutning om påstandene.

  A6-1  v²-referansen for estimatoren: ren drag-sannhet Δt = c·t·((v−w)² − v²)/v² lagt på det
        faktiske designet og estimert med papirets egne modeller; c kalibreres slik at den
        symmetriske helningen er lik den observerte.
  A6-2  medvindsgrenen mot den symmetriske helningen (allerede i r1_asym_meet / r1_vindu_medvind).
  A6-3  stevne-FE per kjønn og aldersbånd (60/100/200 m).
  A6-4/5 H5 med robust skala (1,4826·MAD av residualene innen celle) og verdsatt fra [0, 2]-segmentet.
  A6-7  standardfeil med frihetsgradskorreksjon for de absorberte cellene (som fixest gjør når
        cellene ikke er nøstet i stevneklyngene); hekk mot flat på nytt.

Output: tables/audit/*.csv
"""

import importlib.util
import logging
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"
UT = HERE / "tables" / "audit"
UT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("m03", HERE / "03_estimering.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DIST = {"60m": 60, "100m": 100, "200m": 200}


def fe_faktor(res):
    """SE-faktor når de absorberte cellene telles i småutvalgskorreksjonen."""
    n, k, c = res["n"], len(res["_navn"]), res["celler"]
    return float(np.sqrt((n - k) / (n - k - c)))


def drag(d):
    rader = []
    for kode, lengde in DIST.items():
        g = d[d["event_code"] == kode].copy()
        t = g.groupby("celle")["y"].transform("mean")
        v = lengde / t
        g["ysim"] = t * ((v - g["wind"]) ** 2 - v ** 2) / v ** 2
        g["wind2"] = g["wind"] ** 2
        obs_l = m03.estimer(g, "y", cluster="meet_id")["wind"][0]
        sim_l = m03.estimer(g, "ysim", cluster="meet_id")["wind"][0]
        c = obs_l / sim_l
        po = m03.estimer(g, "y", vindkolonner=("wind_pos", "wind_neg"), cluster="meet_id")
        ps = m03.estimer(g, "ysim", vindkolonner=("wind_pos", "wind_neg"), cluster="meet_id")
        qo = m03.estimer(g, "y", vindkolonner=("wind", "wind2"), cluster="meet_id")
        qs = m03.estimer(g, "ysim", vindkolonner=("wind", "wind2"), cluster="meet_id")
        vbar = lengde / g["y"].mean()
        rader.append({
            "event": kode, "snittfart_ms": vbar,
            "papirets_referanse": (2 * vbar + 1) / (2 * vbar - 1),
            "drag_ratio_estimator": ps["wind_neg"][0] / ps["wind_pos"][0],
            "observert_ratio": po["wind_neg"][0] / po["wind_pos"][0],
            "drag_medvind_s": -c * ps["wind_pos"][0], "obs_medvind_s": -po["wind_pos"][0],
            "drag_motvind_s": -c * ps["wind_neg"][0], "obs_motvind_s": -po["wind_neg"][0],
            "drag_kvad": c * qs["wind2"][0], "obs_kvad": qo["wind2"][0], "obs_kvad_se": qo["wind2"][1],
        })
    return pd.DataFrame(rader)


def h5(d):
    hoved = pd.read_csv(EST / "r1_hoved_meet.csv")
    beta = {r["event"]: r["gevinst_per_ms"] for _, r in hoved[hoved["analyse"] == "hoved_meet"].iterrows()}
    rader = []
    for kode in DIST:
        g0 = d[d["event_code"] == kode].copy()
        g0["y_adj"] = g0["y"] + beta[kode] * g0["wind"]
        g0["w02"] = g0["wind"].clip(0, 2)
        g0["w2p"] = (g0["wind"] - 2).clip(lower=0)
        for (kj, band), g in g0.groupby(["gender", "aldersband"]):
            r = m03.estimer(g, "y", vindkolonner=("wind_pos", "wind_neg"), cluster="meet_id")
            r02 = m03.estimer(g, "y", vindkolonner=("w02", "w2p", "wind_neg"), cluster="meet_id")
            if not r or not r02 or "w02" not in r02:
                continue
            g3 = g[g["n_i_celle"] >= 3]
            res = g3["y_adj"] - g3.groupby("celle")["y_adj"].transform("mean")
            frih = int((g3.groupby("celle")["y"].count() - 1).sum())
            sd = float(np.sqrt((res ** 2).sum() / frih))
            robust = float(1.4826 * np.median(np.abs(res - res.median())) * np.sqrt(len(res) / frih))
            f_hel, f02 = -2 * r["wind_pos"][0], -2 * r02["w02"][0]
            rader.append({"event": kode, "kjonn": kj, "aldersband": band,
                          "fordel_hel_gren_s": f_hel, "fordel_0_2_s": f02, "fordel_0_2_se": 2 * r02["w02"][1],
                          "sd_poolet": sd, "skala_robust": robust,
                          "andel_sd": f_hel / sd, "andel_robust": f_hel / robust,
                          "andel_robust_0_2": f02 / robust,
                          "rader_avvik_over_20pst": int((np.abs(g["y"] / g.groupby("celle")["y"].transform("median") - 1)
                                                         > 0.2).sum()),
                          "n": r["n"]})
    return pd.DataFrame(rader)


def stevne_fe_alder(d):
    rader = []
    for kode in DIST:
        for (kj, band), g in d[d["event_code"] == kode].groupby(["gender", "aldersband"]):
            p = m03.estimer(g, "y", cluster="meet_id")
            m = m03.estimer(g, "y", meet_fe=True, cluster="meet_id")
            if not p or not m:
                continue
            rader.append({"event": kode, "kjonn": kj, "aldersband": band,
                          "primaer_s": -p["wind"][0], "stevne_fe_s": -m["wind"][0],
                          "stevne_fe_se": m["wind"][1], "forhold": m["wind"][0] / p["wind"][0],
                          "n": p["n"]})
    return pd.DataFrame(rader)


def se_korreksjon(d):
    rader = []
    for kode in sorted(d["event_code"].unique()):
        r = m03.estimer(d[d["event_code"] == kode], "y", cluster="meet_id")
        if r:
            rader.append({"event": kode, "beta": r["wind"][0], "se_papir": r["wind"][1],
                          "faktor_fe": fe_faktor(r), "se_fe_korrigert": r["wind"][1] * fe_faktor(r),
                          "n": r["n"], "celler": r["celler"], "regressorer": len(r["_navn"])})
    return pd.DataFrame(rader)


def hekk_korrigert():
    """Hekk mot flat med FE-korrigerte SE (faktor per estimat beregnes på nytt i 07-logikken)."""
    hk = pd.read_csv(EST / "r1_hekk_meet.csv")
    hk = hk[hk["kjonn"] != "begge"].copy()
    hk["faktor"] = np.sqrt((hk["n"] - 10) / (hk["n"] - 10 - hk["celler"]))
    hk["halv_ki"] = (hk["ki_hoy"] - hk["ki_lav"]) / 2 * hk["faktor"]
    hk["ki_lav_korr"] = hk["gevinst_s_per_ms"] - hk["halv_ki"]
    hk["ki_hoy_korr"] = hk["gevinst_s_per_ms"] + hk["halv_ki"]
    hk["over_flat_punkt_korr"] = hk["ki_lav_korr"] > hk["flat_ref"]
    return hk[["kode", "kjonn", "gevinst_s_per_ms", "ki_lav", "ki_hoy", "ki_lav_korr", "ki_hoy_korr",
               "flat_ref", "flat_ref_ki_lav", "flat_ref_ki_hoy", "over_flat_punkt_korr", "n", "celler"]]


def main():
    d = pd.read_csv(DATA / "analyseklar.csv", low_memory=False)
    d["wind_pos"] = d["wind"].clip(lower=0)
    d["wind_neg"] = d["wind"].clip(upper=0)
    drag(d).to_csv(UT / "a6_drag_referanse.csv", index=False)
    logger.info("drag-referanse ferdig")
    h5(d).to_csv(UT / "a6_h5_robust.csv", index=False)
    logger.info("H5 robust ferdig")
    stevne_fe_alder(d).to_csv(UT / "a6_stevne_fe_alder.csv", index=False)
    logger.info("stevne-FE per alder ferdig")
    se_korreksjon(d).to_csv(UT / "a6_se_korreksjon.csv", index=False)
    hekk_korrigert().to_csv(UT / "a6_hekk_korrigert.csv", index=False)
    logger.info(f"ferdig; filer i {UT}/")


if __name__ == "__main__":
    main()
