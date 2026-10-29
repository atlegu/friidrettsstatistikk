"""
01_variabler.py — A3 «Debutalder»: bygg analysedatasettet (ren deltakelse).

Én rad per utøver født 2001-2008 med konkurransedebut (første godkjente
resultat) ved alder 10+. Se ANALYSEPLAN.md §3-4.

Output: data_private/analysedata.csv, data_private/arsvolum.csv, data_private/flyt.json
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def modal(serie):
    s = serie.dropna()
    if s.empty:
        return None
    telling = s.value_counts()
    beste = telling[telling == telling.max()]
    return sorted(beste.index.astype(str))[0]


def main():
    utv = pd.read_csv(DATA / "utovere.csv")
    r = pd.read_csv(DATA / "resultater.csv", parse_dates=["date"], low_memory=False)
    me = pd.read_csv(DATA / "meets.csv").rename(columns={"id": "meet_id"})
    flyt = {"utovere_fodt_2001_2008": len(utv), "resultatrader": len(r)}

    r = r.merge(utv.rename(columns={"id": "athlete_id"}), on="athlete_id", how="inner")
    flyt["rader_ikke_ok"] = int((r["status"] != "OK").sum())
    r = r[r["status"] == "OK"].copy()
    r["alder"] = r["date"].dt.year - r["birth_year"]
    flyt["rader_alder_under_10"] = int((r["alder"] < 10).sum())
    r = r[r["alder"] >= 10].copy()
    r["aar"] = r["date"].dt.year

    # ---- Debut --------------------------------------------------------------------------
    forste = r.sort_values("date").groupby("athlete_id").first().reset_index()
    base = forste[["athlete_id", "date"]].rename(columns={"date": "debut_dato"})
    base = base.merge(utv.rename(columns={"id": "athlete_id"}), on="athlete_id")
    base["debut_aar"] = base["debut_dato"].dt.year
    base["debut_alder"] = base["debut_aar"] - base["birth_year"]
    flyt["debutanter_alder_10plus"] = len(base)
    flyt["debut_17plus"] = int((base["debut_alder"] >= 17).sum())

    uten_kjonn = base["gender"].isna() | ~base["gender"].isin(["M", "F"])
    flyt["uten_kjonn"] = int(uten_kjonn.sum())
    base = base[~uten_kjonn].copy()

    bd = pd.to_datetime(base["birth_date"], errors="coerce")
    base["kvartal"] = ((bd.dt.month - 1) // 3 + 1).astype("Int64")

    # ---- Årsvolum (konkurransedager per utøver per alder) -------------------------------
    arsvol = (r.groupby(["athlete_id", "alder"])["date"].nunique()
              .rename("dager").reset_index())
    arsvol.to_csv(DATA / "arsvolum.csv", index=False)
    piv = arsvol.pivot(index="athlete_id", columns="alder", values="dager")

    def dager_ved(aldre):
        kol = [a for a in aldre if a in piv.columns]
        return piv[kol].sum(axis=1, min_count=1)

    base["vol_debutaar"] = [
        piv.at[a, al] if (a in piv.index and al in piv.columns) else np.nan
        for a, al in zip(base["athlete_id"], base["debut_alder"])
    ]
    v1617 = dager_ved([16, 17])
    base["vol_16_17"] = base["athlete_id"].map(v1617)

    # ---- Utfall og sensur ---------------------------------------------------------------
    siste = r.groupby("athlete_id")["alder"].max()
    base["siste_alder"] = base["athlete_id"].map(siste)
    aktive_naa = set(r.loc[r["aar"] >= 2025, "athlete_id"])
    base["aktiv_naa"] = base["athlete_id"].isin(aktive_naa)
    base["karriere_aar"] = base["siste_alder"] - base["debut_alder"] + 1

    senior_res = r[r["alder"] >= 20]
    per_aar = senior_res.groupby(["athlete_id", "aar"]).size()
    min2 = set(per_aar[per_aar >= 2].reset_index()["athlete_id"])
    base["senior"] = base["athlete_id"].isin(min2).astype(int)
    base["senior_min1"] = base["athlete_id"].isin(set(senior_res["athlete_id"])).astype(int)
    base["aktiv17"] = base["athlete_id"].isin(
        set(r.loc[r["alder"] >= 17, "athlete_id"])).astype(int)

    # ---- Region og klubb i debutsesongen ------------------------------------------------
    rk = r.merge(me[["meet_id", "krets"]], on="meet_id", how="left")
    debutsesong = rk.merge(base[["athlete_id", "debut_aar"]], on="athlete_id")
    debutsesong = debutsesong[debutsesong["aar"] == debutsesong["debut_aar"]]
    base["region"] = base["athlete_id"].map(debutsesong.groupby("athlete_id")["krets"].agg(modal))
    base["club_id"] = base["athlete_id"].map(debutsesong.groupby("athlete_id")["club_id"].agg(modal))
    base["klubbstorrelse"] = base.groupby("club_id")["athlete_id"].transform("count")
    base["log_klubbstorrelse"] = np.log1p(base["klubbstorrelse"])

    # ---- Flagg og utvalg ----------------------------------------------------------------
    base["covid_debut"] = base["debut_aar"].isin([2020, 2021])
    base["kohort_primar"] = base["birth_year"].between(2001, 2005)
    base["debut_10_16"] = base["debut_alder"].between(10, 16)
    prim = base["kohort_primar"] & base["debut_10_16"]
    flyt["primaerutvalg_fodt_2001_2005_debut_10_16"] = int(prim.sum())
    flyt["primaerutvalg_seniorer"] = int(base.loc[prim, "senior"].sum())

    base.drop(columns=["birth_date"]).to_csv(DATA / "analysedata.csv", index=False)
    with open(DATA / "flyt.json", "w") as f:
        json.dump(flyt, f, indent=2, ensure_ascii=False)
    logger.info(f"analysedata: {len(base)} debutanter; primærutvalg {flyt['primaerutvalg_fodt_2001_2005_debut_10_16']} "
                f"({flyt['primaerutvalg_seniorer']} seniorer)")


if __name__ == "__main__":
    main()
