"""
02_deskriptiv.py — A1 «Stagnasjon før exit»: forhåndsregistrerings-TRYGG deskriptiv.

Skriver bare det ANALYSEPLAN.md §7 tillater før OSF-registreringen:
flytdiagram, missingness og fordelinger av eksponeringskomponentene.
INGEN eksponering-utfall-krysninger; utfallet berøres ikke her
(den samlede seniorandelen står kun som marginaltall i flyttellingen fra 01).

Output (aggregater, kan ligge i git):
  tables/flyt.csv
  tables/deskriptiv_fordelinger.csv
  tables/hovedgrupper.csv
"""

import json
import logging
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
TAB = HERE / "tables"
TAB.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def kvantiler(s):
    s = s.dropna()
    if s.empty:
        return {}
    return {"n": int(s.size), "snitt": round(float(s.mean()), 2),
            "p10": round(float(s.quantile(0.10)), 2), "p25": round(float(s.quantile(0.25)), 2),
            "median": round(float(s.median()), 2),
            "p75": round(float(s.quantile(0.75)), 2), "p90": round(float(s.quantile(0.90)), 2)}


def main():
    d = pd.read_csv(DATA / "analysedata.csv")
    with open(DATA / "flyt.json") as f:
        flyt = json.load(f)

    pd.DataFrame([{"steg": k, "antall": v} for k, v in flyt.items()]).to_csv(
        TAB / "flyt.csv", index=False)

    prim = d[(d["kohort_primar"]) & (d["skaarbar"]) & (~d["liten_gruppecelle"])]
    rader = []
    for (kull, kjonn), g in prim.groupby(["birth_year", "gender"]):
        rad = {"fodselsaar": kull, "kjonn": kjonn, "n": len(g),
               "uten_kvartal": int(g["kvartal"].isna().sum())}
        for v in ["vol1314", "vol1516", "k13", "k15", "delta", "niva_w1"]:
            for navn, verdi in kvantiler(g[v]).items():
                rad[f"{v}_{navn}"] = verdi
        rader.append(rad)
    pd.DataFrame(rader).to_csv(TAB / "deskriptiv_fordelinger.csv", index=False)

    hg = (prim.groupby(["gender", "hovedgruppe"]).size().rename("n").reset_index()
          .sort_values(["gender", "n"], ascending=[True, False]))
    hg.to_csv(TAB / "hovedgrupper.csv", index=False)

    logger.info(f"primærutvalg {len(prim)}; tabeller skrevet til {TAB}/")
    logger.info("Ingen eksponering-utfall-analyser er kjørt. Neste steg: OSF-registrering.")


if __name__ == "__main__":
    main()
