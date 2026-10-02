"""
audit_02_compare_extracts.py — Compares the original career extract (data/karrieredata_utvidet.csv)
with the deterministic re-extraction (audit_01; rows created before 2026-05-18) and measures the
consequences for every derived variable used in the analyses.

Output: audit/audit_02_summary.csv and printed summary.
"""

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent
DATA = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data")


def derive(kar, df):
    """Per-athlete variables as in data/07: vol/res per age 13-18, active seasons, final active year."""
    k = kar.merge(df[["athlete_id", "birth_year", "stevne_aar"]], on="athlete_id")
    k["year"] = pd.to_datetime(k["date"], errors="coerce").dt.year
    k["age"] = k["year"] - k["birth_year"]
    out = df[["athlete_id", "birth_year", "stevne_aar"]].copy().set_index("athlete_id")
    for a in range(13, 19):
        ka = k[k["age"] == a]
        out[f"vol_age_{a}"] = ka.groupby("athlete_id")["meet_id"].nunique().reindex(out.index).fillna(0)
        out[f"res_age_{a}"] = ka.groupby("athlete_id").size().reindex(out.index).fillna(0)
    per = k.groupby(["athlete_id", "year"]).size()
    act = per[per >= 2].reset_index()
    last = act.groupby("athlete_id")["year"].max().reindex(out.index)
    out["siste_aktive_ar"] = last.fillna(out["stevne_aar"]).astype(int)
    out["aktiv_senior"] = (out["siste_aktive_ar"] >= out["birth_year"] + 20).astype(int)
    out["aktiv_naa"] = (out["siste_aktive_ar"] >= 2024).astype(int)
    out["vol_pre_milepael"] = out["vol_age_13"] + out["vol_age_14"]
    out["n_active_seasons"] = act.groupby("athlete_id").size().reindex(out.index).fillna(0)
    return out


def main():
    df = pd.read_csv(DATA / "analysedata_utvidet.csv", low_memory=False)
    old = pd.read_csv(DATA / "karrieredata_utvidet.csv", low_memory=False)
    old = old[old["athlete_id"].isin(df["athlete_id"])]
    new = pd.read_csv(R1 / "data_private" / "audit_reextract.csv", low_memory=False)
    rows = []
    rows.append(("old extract: rows / unique ids", f"{len(old):,} / {old['id'].nunique():,}"))
    rows.append(("re-extract (created <= 2026-05-18): rows / unique ids", f"{len(new):,} / {new['id'].nunique():,}"))
    old_ids, new_ids = set(old["id"]), set(new["id"])
    rows.append(("ids in re-extract missing from old extract", f"{len(new_ids - old_ids):,}"))
    rows.append(("ids in old extract absent from re-extract (deleted/reassigned since)", f"{len(old_ids - new_ids):,}"))
    miss = new[new["id"].isin(new_ids - old_ids)]
    rows.append(("athletes affected by missing rows", f"{miss['athlete_id'].nunique():,}"))

    old_d = old.drop_duplicates("id")
    a = derive(old_d, df)
    b = derive(new.drop_duplicates("id"), df)
    sub = df.set_index("athlete_id")
    rows.append(("analysis data vs. old extract re-derived: vol_pre_milepael identical",
                 f"{(a['vol_pre_milepael'] == sub['vol_pre_milepael']).mean():.4f}"))
    rows.append(("analysis data vs. old extract re-derived: aktiv_senior identical",
                 f"{(a['aktiv_senior'] == sub['aktiv_senior']).mean():.4f}"))
    rows.append(("analysis data vs. old extract re-derived: siste_aktive_ar identical",
                 f"{(a['siste_aktive_ar'] == sub['siste_aktive_ar']).mean():.4f}"))
    for v in ["vol_pre_milepael", "vol_age_14", "vol_age_15", "vol_age_16", "res_age_14", "res_age_16",
              "siste_aktive_ar", "aktiv_senior", "aktiv_naa"]:
        diff = (b[v] - a[v])
        rows.append((f"complete vs. old extract: {v} differs (athletes; mean diff)",
                     f"{int((diff != 0).sum())} ; {diff.mean():+.3f}"))
    out = pd.DataFrame(rows, columns=["Check", "Value"])
    out.to_csv(HERE / "audit_02_summary.csv", index=False)
    print(out.to_string(index=False))
    b.reset_index().to_csv(R1 / "data_private" / "audit_rederived_complete.csv", index=False)
    a.reset_index().to_csv(R1 / "data_private" / "audit_rederived_old.csv", index=False)


if __name__ == "__main__":
    main()
