"""
r1_04_text_numbers.py — Remaining numbers quoted in the revised text that depend on the
corrected data and Tyrving scoring: volume-performance correlations and retention by Tyrving
quartile x volume (Section 3.6), and the HHI-performance correlations (Table S18 note).

Output: revision_r1/tables/r1_text_numbers.json, tables/tableS32_volume_by_performance.csv
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent
sys.path.insert(0, str(HERE))
from r1_paths import CDATA, PRIV  # noqa: E402


def baseline_points_by_category():
    """Mean Tyrving points of baseline-meet results by event group (quoted in Section 3.6)."""
    import tyrving_r2 as ty
    df = pd.read_csv(CDATA / "analysedata_utvidet.csv", low_memory=False, usecols=["athlete_id", "birth_year", "gender", "forste_utgave"])
    k = pd.read_csv(CDATA / "karrieredata_utvidet.csv", low_memory=False,
                    usecols=["athlete_id", "date", "event_code", "event_category", "result_type", "performance_value", "er_lekene"])
    k = k[k["er_lekene"] == 1].merge(df, on="athlete_id")
    yr = {"ncc_2011": 2011, "ncc_2012": 2012, "peab_2013": 2013, "peab_2014": 2014, "bendit_2015": 2015, "ungdomslekene_2016": 2016}
    k["year"] = pd.to_datetime(k["date"]).dt.year
    k = k[k["year"] == k["forste_utgave"].map(yr)]
    t = ty.parse_tyrving_xls()
    k["pts"] = [ty.beregn_tyrving_poeng(None if pd.isna(v) else float(v), c, r, g, y - b, t)
                for v, c, r, g, y, b in zip(k["performance_value"], k["event_code"], k["result_type"], k["gender"], k["year"], k["birth_year"])]
    return k.groupby("event_category")["pts"].mean().round(0).to_dict()


def main():
    global TYR_BY_CAT
    TYR_BY_CAT = baseline_points_by_category()
    df = pd.read_csv(CDATA / "analysedata_utvidet.csv", low_memory=False)
    df = df.merge(pd.read_csv(PRIV / "r1_variables.csv"), on="athlete_id", how="left")
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

    # zone jumps scored as missing instead of against the board-jump norm (Supplementary Methods S-M3)
    import r1_03_reviewer_analyses as ra
    z = ra.z
    e = df.assign(female=df["gender"].map({"M": 0, "F": 1}), vol_z=z(df["vol_pre_milepael"]), hhi_z=z(df["hhi_13_14"]))
    for lab, col in [("zone_as_board", "tyrving_best_r1"), ("zone_missing", "tyrving_best_r1_nozone")]:
        e["tyr_z"] = z(e[col])
        m, dd = ra.logit(e, ra.L4)
        cvr, _ = ra.repeated_cv(dd[ra.L4].values, dd["aktiv_senior"].values)
        out[f"tyr_{lab}"] = dict(n=len(dd), missing=int(e[col].isna().sum()), vol=ra.orci(m, "vol_z"), tyr=ra.orci(m, "tyr_z"),
                                 auc=cvr["auc"])
    out["retainers_primary"] = int(df.loc[df["gender"].notna() & df["tyrving_best_r1"].notna(), "aktiv_senior"].sum())
    out["tyr_mean_by_category"] = TYR_BY_CAT
    (R1 / "tables" / "r1_text_numbers.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
