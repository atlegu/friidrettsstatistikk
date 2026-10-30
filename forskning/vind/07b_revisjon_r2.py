"""
07b_revisjon_r2.py — A6: stevne-FE per kjønn og aldersbånd for 60/100/200 m (tabell S6).

Etter dataauditen 30.10.2026 (funn A6-3) presenteres stevne-FE som designets kontroll: den
sammenligner bare resultater fra samme stevne og tar opp all vær- og målerplassering på
stevnenivå. Spørsmålet her er om aldersgradienten overlever den kontrollen.

(De øvrige endringene fra auditen ligger i 03_estimering.py — standardfeil — og i
07_revisjon_r1.py — drag-referansen, H5 fra 0–2-segmentet med robust skala.)

Lybbert & Zheng (2023) tolker at motvind koster high school-løpere mer enn en drag-modell for
elitemenn tilsier, mest for jenter, som psykologi. Drag-asymmetrien vokser når farten faller
(omtrent (2v + w)/(2v − w)), så sammenligningen må gjøres ved løpernes egen fart og gjennom samme
estimator: r2_asym_100m.csv gir motvind/medvind-forholdet per kjønn og aldersbånd mot drag-
forholdet (med og uten stevne-FE), r2_drag_fart.csv drag-forholdet ved fast fart (lagt til etter
planen, Atles beskjed 30.10.2026).

Output: tables/estimering/r2_stevne_fe_alder.csv, r2_asym_100m.csv, r2_drag_fart.csv
"""

import importlib.util
import logging
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"

spec = importlib.util.spec_from_file_location("m03", HERE / "03_estimering.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def forhold_ki(r):
    """Motvind/medvind-forhold med delta-metode-KI fra den korrigerte kovariansen i estimer."""
    i, j = r["_navn"].index("wind_neg"), r["_navn"].index("wind_pos")
    bn, bp, V = r["wind_neg"][0], r["wind_pos"][0], r["_V"]
    R = bn / bp
    se = abs(R) * np.sqrt(V[i, i] / bn ** 2 + V[j, j] / bp ** 2 - 2 * V[i, j] / (bn * bp))
    return R, R - 1.96 * se, R + 1.96 * se


def drag_forhold(g, meet_fe=False, fast_tid=None):
    """Drag-forholdet gjennom samme estimator: Δt = t·((v−w)² − v²)/v², t = cellesnitt (eller fast)."""
    g = g.copy()
    t = g.groupby("celle")["y"].transform("mean") if fast_tid is None else pd.Series(fast_tid, index=g.index)
    v = 100 / t
    g["ysim"] = t * ((v - g["wind"]) ** 2 - v ** 2) / v ** 2
    r = m03.estimer(g, "ysim", vindkolonner=("wind_pos", "wind_neg"), meet_fe=meet_fe, cluster="meet_id")
    return r["wind_neg"][0] / r["wind_pos"][0]


def asymmetri_100m(d):
    g0 = d[d["event_code"] == "100m"].copy()
    g0["wind_pos"], g0["wind_neg"] = g0["wind"].clip(lower=0), g0["wind"].clip(upper=0)
    grupper = [(kj, b, False, g) for (kj, b), g in g0.groupby(["gender", "aldersband"])]
    grupper += [(kj, "alle", fe, g) for fe in (False, True) for kj, g in g0.groupby("gender")]
    rader = []
    for kj, band, fe, g in grupper:
        r = m03.estimer(g, "y", vindkolonner=("wind_pos", "wind_neg"), meet_fe=fe, cluster="meet_id")
        if not r:
            continue
        R, lo, hi = forhold_ki(r)
        rader.append({"kjonn": kj, "aldersband": band, "stevne_fe": fe, "n": r["n"],
                      "medvind_s": -r["wind_pos"][0], "motvind_s": -r["wind_neg"][0],
                      "forhold": R, "ki_lav": lo, "ki_hoy": hi, "forhold_drag": drag_forhold(g, fe),
                      "snitt_tid": float(g.loc[g["n_i_celle"] >= 2, "y"].mean())})
    pd.DataFrame(rader).to_csv(EST / "r2_asym_100m.csv", index=False)
    # drag-forholdet ved fast fart over 100 m-designet: eliten og snittidene i Lybbert & Zheng (tabell 1)
    fart = [{"gruppe": navn, "tid_s": tid, "forhold_drag": drag_forhold(g0, fast_tid=tid)}
            for navn, tid in [("elite_menn", 10.0), ("us_hs_gutter", 12.603), ("us_hs_jenter", 14.557)]]
    pd.DataFrame(fart).to_csv(EST / "r2_drag_fart.csv", index=False)


def main():
    d = pd.read_csv(DATA / "analyseklar.csv", low_memory=False)
    asymmetri_100m(d)
    rader = []
    for kode in ["60m", "100m", "200m"]:
        for (kj, band), g in d[d["event_code"] == kode].groupby(["gender", "aldersband"]):
            p = m03.estimer(g, "y", cluster="meet_id")
            m = m03.estimer(g, "y", meet_fe=True, cluster="meet_id")
            if not p or not m:
                continue
            b, se = m["wind"]
            rader.append({"event": kode, "kjonn": kj, "aldersband": band,
                          "primaer_s": -p["wind"][0], "stevne_fe_s": -b,
                          "stevne_fe_ki_lav": -b - 1.96 * se, "stevne_fe_ki_hoy": -b + 1.96 * se,
                          "stevne_fe_se": se, "forhold": b / p["wind"][0],
                          "n": p["n"], "celler": p["celler"], "stevner": int(g["meet_id"].nunique())})
    pd.DataFrame(rader).to_csv(EST / "r2_stevne_fe_alder.csv", index=False)
    logger.info(f"r2_stevne_fe_alder.csv, r2_asym_100m.csv og r2_drag_fart.csv i {EST}/")


if __name__ == "__main__":
    main()
