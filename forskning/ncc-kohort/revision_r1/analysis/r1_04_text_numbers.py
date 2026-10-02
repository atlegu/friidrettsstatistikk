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
from r1_paths import CDATA, DATA, PRIV  # noqa: E402


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


def descriptives(df):
    """Section 2.2, 3.2 and 4.9 / S-M8 numbers: Kaplan-Meier summary, exit rate by age, club changes,
    hurdlers who also sprinted, combined-event totals."""
    from lifelines import KaplanMeierFitter
    o = {}
    d = df.copy()
    d["event"] = (d["aktiv_naa"] == 0).astype(int)
    d["dur"] = (d["alder_ved_slutt"] - (d["stevne_aar"] - d["birth_year"])).clip(lower=0.5)
    km = KaplanMeierFitter().fit(d["dur"], d["event"])
    o["km_surv"] = {t: float(km.survival_function_at_times(t).iloc[0]) for t in (2, 3, 5, 14)}
    o["km_median"] = float(km.median_survival_time_)
    o["exit_rate_by_age"] = {a: float(((d["alder_ved_slutt"] == a) & (d["event"] == 1)).sum() / (d["alder_ved_slutt"] >= a).sum())
                             for a in range(13, 24)}
    d["vol_q"] = pd.cut(d["vol_milepael"], [-0.5, 0.5, 5.5, 15.5, 30.5, np.inf], labels=["0", "1-5", "6-15", "16-30", "31+"])
    o["fig3_strata"] = {}
    for q, g in d.groupby("vol_q", observed=True):
        k = KaplanMeierFitter().fit(g["dur"], g["event"])
        o["fig3_strata"][q] = dict(n=len(g), surv14=float(k.survival_function_at_times(14).iloc[0]), senior=float(g["aktiv_senior"].mean()))
    kar = pd.read_csv(CDATA / "karrieredata_utvidet.csv", low_memory=False, usecols=["athlete_id", "date", "club_name", "event_category", "event_code"])
    o["share_two_or_more_clubs"] = float((kar.groupby("athlete_id")["club_name"].nunique() >= 2).mean())
    kar = kar.merge(df[["athlete_id", "birth_year"]], on="athlete_id")
    w = kar[(pd.to_datetime(kar["date"]).dt.year - kar["birth_year"]).between(13, 14)]
    cats = w.groupby("athlete_id")["event_category"].agg(set)
    hurd = cats[cats.map(lambda c: "hurdles" in c)]
    o["hurdlers_13_14"] = dict(n=len(hurd), also_sprint=float(hurd.map(lambda c: "sprint" in c).mean()))
    o["combined_share_13_14"] = float((w["event_category"] == "combined").mean())
    return o


def submitted_data_checks():
    """Response-letter numbers that refer to the submitted analysis file (data/analysedata_utvidet.csv)."""
    import statsmodels.api as sm
    sub = pd.read_csv(DATA / "analysedata_utvidet.csv", low_memory=False)
    kar = pd.read_csv(DATA / "karrieredata_utvidet.csv", low_memory=False, usecols=["athlete_id", "date", "event_category"])
    kar = kar.merge(sub[["athlete_id", "birth_year", "stevne_aar"]], on="athlete_id")
    kar["year"] = pd.to_datetime(kar["date"]).dt.year
    kar["age"] = kar["year"] - kar["birth_year"]
    early = kar[kar["year"] <= kar["stevne_aar"] + 2]
    hh = kar[kar["age"].between(13, 14)].groupby("athlete_id")["event_category"].apply(
        lambda c: float((c.value_counts(normalize=True) ** 2).sum())).rename("hhi1314")
    sub = sub.merge(hh, on="athlete_id", how="left")
    sub["female"] = sub["gender"].map({"M": 0, "F": 1})
    zz = lambda v: (v - v.mean()) / v.std()  # noqa: E731
    o = {"hhi_early_results_age15_16": int(early["age"].between(15, 16).sum())}
    for lab, h in [("submitted", "hhi_early"), ("hhi_13_14", "hhi1314")]:
        dd = sub.assign(tyr_z=zz(sub["tyrving_best"]), hhi_z=zz(sub[h]), vol_z=zz(sub["vol_pre_milepael"]))
        dd = dd[["aktiv_senior", "female", "tyr_z", "hhi_z", "vol_z"]].dropna()
        m = sm.Logit(dd["aktiv_senior"], sm.add_constant(dd[["female", "tyr_z", "hhi_z", "vol_z"]])).fit(disp=0)
        o[f"submitted_refit_{lab}"] = dict(n=len(dd), vol=float(np.exp(m.params["vol_z"])), hhi=float(np.exp(m.params["hhi_z"])))
    # unknown sex as a separate category (no Tyrving), submitted data, HHI from ages 13-14 (R1 response, Comment 5)
    dd = sub.assign(hhi_z=zz(sub["hhi1314"]), vol_z=zz(sub["vol_pre_milepael"]))
    dd["sex_unknown"] = dd["female"].isna().astype(int)
    dd["female3"] = dd["female"].fillna(0)
    m_all = sm.Logit(dd["aktiv_senior"], sm.add_constant(dd[["female3", "sex_unknown", "hhi_z", "vol_z"]])).fit(disp=0)
    kn = dd[dd["sex_unknown"] == 0]
    m_kn = sm.Logit(kn["aktiv_senior"], sm.add_constant(kn[["female", "hhi_z", "vol_z"]])).fit(disp=0)
    o["submitted_unknown_sex"] = dict(n_all=len(dd), vol_all=float(np.exp(m_all.params["vol_z"])),
                                      n_known=len(kn), vol_known=float(np.exp(m_kn.params["vol_z"])))
    return o


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
    out.update(descriptives(df))
    out.update(submitted_data_checks())
    (R1 / "tables" / "r1_text_numbers.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
