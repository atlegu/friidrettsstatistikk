"""
07b_revisjon_r2.py — A6: stevne-FE per kjønn og aldersbånd for 60/100/200 m (tabell S6).

Etter dataauditen 30.10.2026 (funn A6-3) presenteres stevne-FE som designets kontroll: den
sammenligner bare resultater fra samme stevne og tar opp all vær- og målerplassering på
stevnenivå. Spørsmålet her er om aldersgradienten overlever den kontrollen.

(De øvrige endringene fra auditen ligger i 03_estimering.py — standardfeil — og i
07_revisjon_r1.py — drag-referansen, H5 fra 0–2-segmentet med robust skala.)

Output: tables/estimering/r2_stevne_fe_alder.csv
"""

import importlib.util
import logging
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
EST = HERE / "tables" / "estimering"

spec = importlib.util.spec_from_file_location("m03", HERE / "03_estimering.py")
m03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m03)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    d = pd.read_csv(DATA / "analyseklar.csv", low_memory=False)
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
    logger.info(f"r2_stevne_fe_alder.csv i {EST}/")


if __name__ == "__main__":
    main()
