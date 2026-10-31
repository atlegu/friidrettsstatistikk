"""
12_utvalgsstorrelse.py — A6: følsomhetsanalysen i «Sample size estimation and justification» (JSS).

JSS krever et eget delavsnitt i Methods med alle inndata til utvalgsberegningen (Abt mfl. 2025,
doi 10.1080/02640414.2025.2499403). Utvalget er hele den kvalifiserte populasjonen i registeret, så
ingen størrelse ble beregnet a priori; redaksjonen anbefaler da en følsomhetsanalyse etter estimeringen:
minste påvisbare effekt (MDE) for tosidig Wald-test av den stevneklyngede helningen med α = 0,05 og
styrke 0,80, MDE = (z_0,975 + z_0,80) × SE. SE hentes fra KI-ene i r1-filene, som er bygget som
β ± 1,96 × SE (03_estimering.gevinst), og effekten er rå helning (s eller cm per m/s).

Minste effekt av interesse: helningen der det lovlige +2,0 m/s-vinduet flytter et merke én
registreringsenhet, altså 0,01 s i sprint og 1 cm i hopp: 0,005 s og 0,5 cm per m/s.

Inndata: tables/estimering/r1_hoved_meet.csv, r1_alder_meet.csv
Utdata:  tables/estimering/r4_mde.csv
"""

import logging
from pathlib import Path
from statistics import NormalDist

import pandas as pd

HERE = Path(__file__).parent
EST = HERE / "tables" / "estimering"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ALFA, STYRKE = 0.05, 0.80
Z_ALFA, Z_STYRKE = NormalDist().inv_cdf(1 - ALFA / 2), NormalDist().inv_cdf(STYRKE)
Z_KI = 1.96                       # KI-ene i r1-filene er β ± 1,96 × SE
SESOI = {"s": 0.01 / 2.0, "cm": 1.0 / 2.0}   # én registreringsenhet over +2,0 m/s


def mde(t):
    t = t.copy()
    t["se"] = (t["ki_hoy"] - t["ki_lav"]) / (2 * Z_KI)
    t["mde"] = (Z_ALFA + Z_STYRKE) * t["se"]
    t["sesoi"] = t["enhet"].map(SESOI)
    t["mde_under_sesoi"] = t["mde"] <= t["sesoi"]
    return t


def main():
    hov = pd.read_csv(EST / "r1_hoved_meet.csv")
    hov = hov[hov["analyse"] == "hoved_meet"].assign(nivaa="hoved", kjonn="begge", aldersband="alle")
    al = pd.read_csv(EST / "r1_alder_meet.csv")
    al = al[al["enhet"].isin(["s", "cm"])].assign(nivaa="alder")
    kol = ["nivaa", "event", "enhet", "kjonn", "aldersband", "gevinst_per_ms", "ki_lav", "ki_hoy", "n", "celler"]
    ut = mde(pd.concat([hov[kol], al[kol]], ignore_index=True))
    ut["alfa"], ut["styrke"] = ALFA, STYRKE
    ut["z_alfa"], ut["z_styrke"] = Z_ALFA, Z_STYRKE
    ut.to_csv(EST / "r4_mde.csv", index=False)

    h = ut[ut["nivaa"] == "hoved"].set_index("event")
    logger.info("MDE-faktor (z_0,975 + z_0,80) = %.4f", Z_ALFA + Z_STYRKE)
    for e, r in h.iterrows():
        logger.info("%-18s MDE %.4f %s per m/s (SESOI %.3f; under: %s)", e, r["mde"], r["enhet"], r["sesoi"],
                    r["mde_under_sesoi"])
    sp = ut[(ut["nivaa"] == "alder") & ut["event"].isin(["60m", "100m", "200m"]) & (ut["enhet"] == "s")]
    logger.info("aldersbånd 60/100/200 m: MDE %.4f–%.4f s per m/s (median %.4f, n = %d)",
                sp["mde"].min(), sp["mde"].max(), sp["mde"].median(), len(sp))
    logger.info("skrevet: %s", EST / "r4_mde.csv")


if __name__ == "__main__":
    main()
