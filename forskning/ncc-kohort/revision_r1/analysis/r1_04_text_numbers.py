"""
r1_04_text_numbers.py — Remaining numbers quoted in the revised text that depend on the
corrected Tyrving scoring: volume-performance correlations and retention by Tyrving
quartile x volume (Section 3.6), and the HHI-performance correlations (Table S18 note).

Output: revision_r1/tables/r1_text_numbers.json, tables/tableS32_volume_by_performance.csv
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent
DATA = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data")


def main():
    df = pd.read_csv(DATA / "analysedata_utvidet.csv", low_memory=False)
    df = df.merge(pd.read_csv(R1 / "data_private" / "r1_variables.csv"), on="athlete_id", how="left")
    out = {}
    sp = lambda a, b: float(df[[a, b]].corr("spearman").iloc[0, 1])  # noqa: E731
    out["rho_vol_tyr"] = sp("vol_pre_milepael", "tyrving_best_r1")
    out["rho_vol_peak_pre15"] = sp("vol_pre_milepael", "tyrving_peak_pre15_r1")
    out["rho_milestonevol_tyr15"] = sp("vol_milepael", "tyrving_age_15_r1")
    out["r_hhi_tyr"] = float(df[["hhi_13_14", "tyrving_best_r1"]].corr().iloc[0, 1])

    d = df.dropna(subset=["tyrving_best_r1"]).copy()
    d["tq"] = pd.qcut(d["tyrving_best_r1"], 4, labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"])
    med = d["vol_pre_milepael"].median()
    d["vol_hi"] = np.where(d["vol_pre_milepael"] > med, "above median", "at or below median")
    t = d.groupby(["tq", "vol_hi"], observed=True)["aktiv_senior"].agg(["mean", "size"]).unstack()
    rows = []
    for q in t.index:
        rows.append({"Baseline Tyrving quartile": q,
                     "Senior retention, volume above median": f"{100 * t.loc[q, ('mean', 'above median')]:.1f}% (n = {int(t.loc[q, ('size', 'above median')])})",
                     "Senior retention, volume at or below median": f"{100 * t.loc[q, ('mean', 'at or below median')]:.1f}% (n = {int(t.loc[q, ('size', 'at or below median')])})"})
    pd.DataFrame(rows).to_csv(R1 / "tables" / "tableS32_volume_by_performance.csv", index=False)
    out["quartile_table"] = rows
    out["vol_median"] = float(med)
    out["tyr_mean_by_cohort"] = d.groupby(np.where(d["birth_year"] <= 2000, "A", "B"))["tyrving_best_r1"].mean().round(1).to_dict()
    out["tyr_mean_all"] = float(d["tyrving_best_r1"].mean())
    (R1 / "tables" / "r1_text_numbers.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
