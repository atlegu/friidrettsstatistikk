"""
02_deskriptiv.py — A3 «Debutalder»: eksponeringssidens deskriptiv.

Debutalder per kohort og kjønn, fødselskvartal per debutalder, og
debutårets volum — ingen utfallskrysninger (modellene kommer i 03).

Output: tables/debutfordeling.csv, tables/kvartal_per_debutalder.csv,
        tables/debutvolum.csv
"""

import logging
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables"
TAB.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    d = pd.read_csv(DATA / "analysedata.csv")
    d = d[d["debut_10_16"]]

    ford = (d.groupby(["birth_year", "debut_alder"]).size().rename("n").reset_index()
            .pivot(index="birth_year", columns="debut_alder", values="n").fillna(0).astype(int))
    ford["totalt"] = ford.sum(axis=1)
    ford.to_csv(TAB / "debutfordeling.csv")

    kv = (d.dropna(subset=["kvartal"]).groupby(["debut_alder", "kvartal"]).size()
          .rename("n").reset_index()
          .pivot(index="debut_alder", columns="kvartal", values="n").fillna(0).astype(int))
    kv_pst = (kv.div(kv.sum(axis=1), axis=0) * 100).round(1)
    kv_pst.to_csv(TAB / "kvartal_per_debutalder.csv")

    vol = d.groupby("debut_alder")["vol_debutaar"].describe()[["count", "25%", "50%", "75%"]]
    vol.round(1).to_csv(TAB / "debutvolum.csv")

    logger.info(f"{len(d)} debutanter 10-16 beskrevet; tabeller i {TAB}/")
    logger.info("Ingen eksponering-utfall-analyser kjørt her.")


if __name__ == "__main__":
    main()
