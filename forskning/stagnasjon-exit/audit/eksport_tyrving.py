"""
eksport_tyrving.py — A1-audit: eksporter Tyrving-poeng per resultat (alder 13–16,
elektronisk) fra den validerte skåringsmodulen (tyrving_r2.py, 2014-arbeidsboken).

Skåringen er en DELT, tidligere validert komponent (jf. JSAMS-følgestudien); den
uavhengige R-implementasjonen bygger alt annet selv og leser bare disse radene.
Output: audit/tyrving_scored.csv (+ sha256 i DATA_AUDIT).
"""

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent.parent
sys.path.insert(0, "/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/"
                   "forskning/ncc-kohort/revision_r1/analysis")
from tyrving_r2 import beregn_tyrving_poeng, parse_tyrving_xls  # noqa: E402


def main():
    r = pd.read_csv(HERE / "data_private" / "resultater.csv",
                    parse_dates=["date"], low_memory=False)
    utv = pd.read_csv(HERE / "data_private" / "utovere.csv").rename(columns={"id": "athlete_id"})
    r = r.drop(columns=["birth_year"], errors="ignore").merge(utv, on="athlete_id", how="inner")
    r = r[r["status"] == "OK"].copy()
    r["alder"] = r["date"].dt.year - r["birth_year"]
    r = r[r["alder"].between(13, 16) & (r["is_manual_time"].astype(str) != "True")
          & r["gender"].isin(["M", "F"])].copy()
    tab = parse_tyrving_xls()
    r["tyrving"] = [
        beregn_tyrving_poeng(pv, kode, rt, kj, al, tab)
        for pv, kode, rt, kj, al in zip(r["performance_value"], r["event_code"],
                                        r["result_type"], r["gender"], r["alder"])
    ]
    r = r[r["tyrving"].notna()]
    ut = r[["id", "athlete_id", "alder", "event_code", "event_category",
            "is_wind_legal", "tyrving"]]
    ut.to_csv(HERE / "audit" / "tyrving_scored.csv", index=False)
    print(f"{len(ut)} skårede rader")


if __name__ == "__main__":
    main()
