"""
02_deskriptiv.py — A6 «Vind»: forhåndssjekkene fra ANALYSEPLAN.md §5.

Heaping i vindverdiene, dekning per øvelse x år, og celletellinger.
Ingen vind-resultat-estimering her.

Output: tables/heaping.csv, tables/dekning.csv, tables/celler.csv
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables"
TAB.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    d = pd.read_csv(DATA / "analyseklar.csv")

    w = d["wind"]
    tideler = (w * 10).round().astype(int)
    rader = [{
        "mål": "andel eksakt 0,0", "verdi": round(float((w == 0).mean()), 4)},
        {"mål": "andel hele m/s (x,0)", "verdi": round(float((tideler % 10 == 0).mean()), 4)},
        {"mål": "andel medvind (>0)", "verdi": round(float((w > 0).mean()), 4)},
        {"mål": "andel motvind (<0)", "verdi": round(float((w < 0).mean()), 4)},
        {"mål": "median", "verdi": round(float(w.median()), 2)},
        {"mål": "p5", "verdi": round(float(w.quantile(0.05)), 2)},
        {"mål": "p95", "verdi": round(float(w.quantile(0.95)), 2)},
    ]
    pd.DataFrame(rader).to_csv(TAB / "heaping.csv", index=False)

    miss = pd.read_csv(DATA / "missing.csv")
    dek = (miss.pivot_table(index=["event_code", "aar"], columns="har_vind",
                            values="n", fill_value=0).reset_index()
           .rename(columns={True: "med_vind", False: "uten_vind"}))
    dek["dekning"] = (dek["med_vind"] / (dek["med_vind"] + dek["uten_vind"])).round(3)
    dek.to_csv(TAB / "dekning.csv", index=False)

    celler = (d[d["n_i_celle"] >= 2]
              .groupby(["event_code", "gender", "aldersband"])
              .agg(rader=("y", "size"), celler=("celle", "nunique"),
                   utovere=("athlete_id", "nunique")).reset_index())
    celler.to_csv(TAB / "celler.csv", index=False)

    logger.info(f"heaping: 0,0-andel {rader[0]['verdi']}, hele m/s {rader[1]['verdi']}")
    logger.info(f"dekning og celletellinger skrevet til {TAB}/")


if __name__ == "__main__":
    main()
