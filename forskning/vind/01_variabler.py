"""
01_variabler.py — A6 «Vind»: bygg analysefilen.

Filtre (ANALYSEPLAN.md §3) med flyttelling; enhetene verifiseres empirisk
(tider i hundredeler -> sekunder; hopp i mm eller cm -> meter, autodetektert
per øvelse mot kjente størrelsesordener).

Output: data_private/analyseklar.csv (rader med vindverdi som passerer filtrene),
        data_private/missing.csv (dekning, aggregat), data_private/flyt.json
"""

import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data_private"
sys.path.insert(0, str(HERE.parent))
from rens_felles import fjern_kopier  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TIDSKODER = {"60m", "80m", "100m", "150m", "200m"}
GRENSER = {  # sekunder for løp, meter for hopp
    "60m": (6.4, 16), "80m": (8.5, 20), "100m": (9.5, 22),
    "150m": (14, 35), "200m": (19, 45),
    "lengde": (1.0, 8.6), "lengde_sone_05m": (1.0, 8.6),
    "tresteg": (4.0, 18.5), "tresteg_sone_05m": (4.0, 18.5),
}
BAND = [(10, 11, "10-11"), (12, 13, "12-13"), (14, 15, "14-15"),
        (16, 17, "16-17"), (18, 19, "18-19"), (20, 34, "20-34")]


def aldersband(a):
    for lo, hi, navn in BAND:
        if lo <= a <= hi:
            return navn
    return None


def main():
    r = pd.read_csv(DATA / "resultater.csv", parse_dates=["date"], low_memory=False)
    utv = pd.read_csv(DATA / "utovere.csv").rename(columns={"id": "athlete_id"})
    me = pd.read_csv(DATA / "meets.csv").rename(columns={"id": "meet_id"})
    flyt = {"rader_uttrekk": len(r)}
    r, kopier = fjern_kopier(r)
    flyt["ekskl_sonetvilling_brettkode"] = kopier["sonetvilling"]
    flyt["ekskl_flerdagskopi_brettkode"] = kopier["flerdagskopi"]
    flyt["ekskl_eksakt_dublett"] = kopier["eksakt_dublett"]

    r = r.merge(utv, on="athlete_id", how="left")
    r = r.merge(me[["meet_id", "indoor", "krets", "level"]], on="meet_id", how="left")
    r["aar"] = r["date"].dt.year
    r["maaned"] = r["date"].dt.month

    # Missingness-aggregat FØR filtrering (per øvelse x år: med/uten vind, ute)
    ute = r[r["indoor"].astype(str) != "True"]
    miss = (ute.assign(har_vind=ute["wind"].notna())
            .groupby(["event_code", "aar", "har_vind"]).size().rename("n").reset_index())
    miss.to_csv(DATA / "missing.csv", index=False)

    # ---- Filtre med telling ----------------------------------------------------------
    def steg(navn, maske):
        flyt[navn] = int((~maske).sum())
        return r[maske]

    r = steg("ekskl_ikke_ok", r["status"] == "OK")
    r = steg("ekskl_innendors", r["indoor"].astype(str) != "True")
    r = steg("ekskl_manuell", r["is_manual_time"].astype(str) != "True")
    r = steg("ekskl_uten_kjonn", r["gender"].isin(["M", "F"]))
    r = steg("ekskl_uten_fodselsaar", r["birth_year"].notna())
    r["alder"] = (r["aar"] - r["birth_year"]).astype(int)
    r = steg("ekskl_alder_utenfor_10_34", r["alder"].between(10, 34))
    # Fra februar 2026 la importen sonehopp under brettkoden (feil kode, ikke kopier; kan bare
    # avgjøres mot kilden): uttrekket har 0 utendørs sonerader i 2026 mot 1 736 ved 11–13 år i
    # 2025. Brettkodede hopp i 2026 ved 11–13 år holdes derfor utenfor (audit 30.10.2026).
    r = steg("ekskl_2026_brettkode_11_13", ~((r["aar"] == 2026) & r["event_code"].isin(["lengde", "tresteg"])
                                             & r["alder"].between(11, 13)))
    flyt["uten_vindverdi"] = int(r["wind"].isna().sum())
    r = r[r["wind"].notna()].copy()
    r = steg("ekskl_vind_over_8", r["wind"].abs() <= 8)

    # ---- Enheter: autodetekter per øvelse ---------------------------------------------
    y = pd.Series(np.nan, index=r.index)
    enheter = {}
    for kode, g in r.groupby("event_code"):
        med = g["performance_value"].median()
        if kode in TIDSKODER:
            fakt, enhet = 1 / 100, "hundredeler->s"
        elif med > 1500:
            fakt, enhet = 1 / 1000, "mm->m"
        else:
            fakt, enhet = 1 / 100, "cm->m"
        enheter[kode] = {"median_pv": float(med), "tolkning": enhet}
        y.loc[g.index] = g["performance_value"] * fakt
    r["y"] = y
    flyt["enheter"] = enheter

    lo = r["event_code"].map(lambda k: GRENSER[k][0])
    hi = r["event_code"].map(lambda k: GRENSER[k][1])
    r = steg("ekskl_urimelig_resultat", r["y"].between(lo, hi) & r["y"].notna())

    # ---- Celler, nivå og bånd ----------------------------------------------------------
    r["aldersband"] = r["alder"].map(aldersband)
    r["celle"] = (r["athlete_id"].astype(str) + "_" + r["aar"].astype(str)
                  + "_" + r["event_code"])
    cellestr = r.groupby("celle")["id"].transform("count")
    r["n_i_celle"] = cellestr
    flyt["rader_i_celler_min2"] = int((cellestr >= 2).sum())
    flyt["celler_min2"] = int(r.loc[cellestr >= 2, "celle"].nunique())

    cellemiddel = r.groupby("celle")["y"].transform("mean")
    r["prestasjon"] = np.where(r["event_code"].isin(list(TIDSKODER)),
                               -cellemiddel, cellemiddel)
    grp = r.groupby(["event_code", "gender", "aldersband"])["prestasjon"]
    r["niva_z"] = (r["prestasjon"] - grp.transform("mean")) / grp.transform("std")
    def tertil(s):
        if s.notna().sum() < 30 or s.nunique() < 3:
            return pd.Series(index=s.index, dtype="object")
        return pd.qcut(s.rank(method="first"), 3, labels=["lav", "midt", "hoy"])

    r["nivatertil"] = (r.groupby(["event_code", "gender", "aldersband"])["niva_z"]
                       .transform(tertil))

    r["runde"] = r["round"].fillna("ukjent").astype(str)
    r["vind_ulovlig"] = r["is_wind_legal"].astype(str) == "False"

    ut = r[["athlete_id", "event_code", "gender", "alder", "aldersband", "aar",
            "maaned", "runde", "meet_id", "krets", "level", "celle", "n_i_celle",
            "y", "wind", "niva_z", "nivatertil", "vind_ulovlig"]]
    ut.to_csv(DATA / "analyseklar.csv", index=False)
    flyt["rader_analyseklar"] = len(ut)
    flyt["utovere"] = int(r["athlete_id"].nunique())

    with open(DATA / "flyt.json", "w") as f:
        json.dump(flyt, f, indent=2, ensure_ascii=False)
    logger.info(f"analyseklar: {len(ut)} rader, {flyt['utovere']} utøvere, "
                f"{flyt['celler_min2']} celler med >=2 vindmålte")


if __name__ == "__main__":
    main()
