"""
16_revision_analyses.py — Analyses required by the simulated IJSSC review panel
(PEER_REVIEW_SIMULATION_IJSSC.md, items M1, M6, M7, M8, M9, M13, S1, S2, S8).

Outputs (submission_pse/tables/):
  tableS3_e_values.csv           (REGENERATED: primary-spec E-values; old file -> _OLD)
  tableS9_outcome_sensitivity.csv(REGENERATED: primary L4 spec; old file -> _OLD)
  table6_NEW_prospective_calibration.csv (REGENERATED: + flagged/unflagged retention, bootstrap CIs)
  tableS19_sample_flow.csv       (M7: one map of every analysis n)
  tableS20_exit_aligned.csv      (M1: exit-aligned trajectories + % patterns)
  tableS21_hhi_stress.csv        (M8: count-dependence stress tests)
  tableS22_mi_sensitivity.csv    (M7: multiple imputation for the primary model)
  tableS23_club_effects.csv      (M13: club ICC + random-intercept refit)
  tableS24_calibration_slope.csv (M9: CV calibration of the L4 model)
  tableS25_fixed_window_outcome.csv (S1: ages 20-22 fixed-window outcome)
  tableS26_missing_comparison.csv(M7: included vs excluded athletes)
  revision_results.json          (all key numbers for the manuscript text)
"""

import json
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

HERE = Path(__file__).parent
TAB_DIR = HERE.parent / "submission_pse" / "tables"
RESULTS = {}
RNG = np.random.default_rng(42)


def lr_unpenalized():
    try:
        return LogisticRegression(penalty=None, max_iter=2000)
    except Exception:
        return LogisticRegression(C=1e9, max_iter=2000)


def fit_logit(df, covars, outcome="aktiv_senior"):
    d = df[covars + [outcome]].dropna()
    X = sm.add_constant(d[covars])
    m = sm.Logit(d[outcome], X).fit(disp=0)
    return m, d


def or_ci(m, term):
    return (float(np.exp(m.params[term])),
            float(np.exp(m.conf_int().loc[term, 0])),
            float(np.exp(m.conf_int().loc[term, 1])),
            float(m.pvalues[term]))


def cv_auc(df, covars, outcome="aktiv_senior", seed=42):
    d = df[covars + [outcome]].dropna()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    auc = cross_val_score(lr_unpenalized(), d[covars], d[outcome], cv=cv, scoring="roc_auc", n_jobs=-1)
    return float(auc.mean()), float(auc.std()), len(d)


def evalue_rr(rr):
    rr = max(rr, 1 / rr)
    return rr + np.sqrt(rr * (rr - 1))


def load():
    df = pd.read_csv(HERE / "analysedata_utvidet.csv", low_memory=False)
    df["female"] = df["gender"].map({"M": 0, "F": 1})
    for c in ["tyrving_best", "hhi_early", "vol_pre_milepael", "vol_milepael", "klubb_storrelse"]:
        df[c + "_z"] = (df[c] - df[c].mean()) / df[c].std()
    kar = pd.read_csv(HERE / "karrieredata_utvidet.csv", low_memory=False)
    kar["date"] = pd.to_datetime(kar["date"], errors="coerce")
    kar["year"] = kar["date"].dt.year
    kar = kar.merge(df[["athlete_id", "birth_year"]], on="athlete_id", how="inner")
    kar["age"] = kar["year"] - kar["birth_year"]
    return df, kar


def replicate_primary(df):
    logger.info("=== 0. PRIMARY L4 REPLICATION (authoritative numbers) ===")
    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"]
    m, d = fit_logit(df, covars)
    o, lo, hi, p = or_ci(m, "vol_pre_milepael_z")
    auc, aucsd, n = cv_auc(df, covars)
    oh, loh, hih, ph = or_ci(m, "hhi_early_z")
    of, lof, hif, pf = or_ci(m, "female")
    RESULTS["primary"] = dict(n=n, vol_or=o, vol_lo=lo, vol_hi=hi, vol_p=p,
                              hhi_or=oh, hhi_lo=loh, hhi_hi=hih, hhi_p=ph,
                              female_or=of, female_lo=lof, female_hi=hif, female_p=pf,
                              auc=auc, auc_sd=aucsd)
    logger.info(f"  n={n}  vol OR={o:.3f} [{lo:.3f},{hi:.3f}]  HHI OR={oh:.3f} [{loh:.3f},{hih:.3f}]"
                f"  female OR={of:.3f}  CV-AUC={auc:.3f}±{aucsd:.3f}")
    return covars


def m1_exit_aligned(df, kar):
    logger.info("=== M1. EXIT-ALIGNED PULL-BACK ANALYSIS ===")
    # active season (>=2 results) per athlete-age from raw data, ages 13-19
    counts = kar.groupby(["athlete_id", "age"]).size().rename("n_res").reset_index()
    meets = kar.groupby(["athlete_id", "age"])["meet_id"].nunique().rename("n_meets").reset_index()
    peryear = counts.merge(meets, on=["athlete_id", "age"])
    vol = peryear.pivot(index="athlete_id", columns="age", values="n_meets")

    d = df[df["aktiv_senior"] == 0].copy()
    d["final_age"] = d["siste_aktive_ar"] - d["birth_year"]
    RESULTS["m1_final_age_check"] = float((d["final_age"] == d["alder_ved_slutt"]).mean())

    # restrict to dropouts with final season at ages 15-19 (T-1..T-3 observable within 13-18)
    sub = d[(d["final_age"] >= 15) & (d["final_age"] <= 19)].copy()

    def vol_at(row, k):
        a = row["final_age"] - k
        if 13 <= a <= 19 and row["athlete_id"] in vol.index and a in vol.columns:
            v = vol.loc[row["athlete_id"], a]
            return 0.0 if pd.isna(v) else float(v)
        return np.nan

    for k in [0, 1, 2, 3]:
        sub[f"T_minus_{k}"] = sub.apply(lambda r: vol_at(r, k), axis=1)
        # ages below 13 are unobserved -> NaN stays NaN; ages >=13 with no rows = 0
        mask = (sub["final_age"] - k) >= 13
        sub.loc[mask & sub[f"T_minus_{k}"].isna(), f"T_minus_{k}"] = 0.0

    aligned = {f"T-{k}": dict(median=float(sub[f"T_minus_{k}"].median()),
                              q25=float(sub[f"T_minus_{k}"].quantile(.25)),
                              q75=float(sub[f"T_minus_{k}"].quantile(.75)),
                              n=int(sub[f"T_minus_{k}"].notna().sum()))
               for k in [3, 2, 1, 0]}

    # pattern shares among dropouts with final_age >= 15 (T-1 observable)
    s1 = sub.dropna(subset=["T_minus_1"])
    share_active_penult = float((s1["T_minus_1"] > 0).mean())

    # personal peak before T-1 (ages 13 .. final-2)
    def peak_before(row):
        ages = [a for a in range(13, int(row["final_age"]) - 1)]
        vals = [vol.loc[row["athlete_id"], a] if (row["athlete_id"] in vol.index and a in vol.columns) else np.nan
                for a in ages]
        vals = [0.0 if pd.isna(v) else float(v) for v in vals] if ages else []
        return max(vals) if vals else np.nan

    s2 = sub[sub["final_age"] >= 16].copy()          # need >=1 season before T-1
    s2["peak_pre"] = s2.apply(peak_before, axis=1)
    s2 = s2.dropna(subset=["T_minus_1", "peak_pre"])
    red_nonzero = (s2["T_minus_1"] > 0) & (s2["T_minus_1"] < s2["peak_pre"])
    share_reduced_nonzero = float(red_nonzero.mean())
    share_penult_zero = float((s2["T_minus_1"] == 0).mean())
    share_penult_at_peak = float((s2["T_minus_1"] >= s2["peak_pre"]).mean())

    # declined INTO the final season (final vol < personal peak before final)
    def peak_before_final(row):
        ages = [a for a in range(13, int(row["final_age"]))]
        vals = [vol.loc[row["athlete_id"], a] if (row["athlete_id"] in vol.index and a in vol.columns) else np.nan
                for a in ages]
        vals = [0.0 if pd.isna(v) else float(v) for v in vals] if ages else []
        return max(vals) if vals else np.nan

    s3 = sub.copy()
    s3["peak_bf"] = s3.apply(peak_before_final, axis=1)
    s3 = s3.dropna(subset=["T_minus_0", "peak_bf"])
    share_decline_into_final = float((s3["T_minus_0"] < s3["peak_bf"]).mean())

    # contamination-free change model: active at 16 (>=2 results), predict senior status.
    # Parameterized as in Table 4: earlier LEVEL (vol_15) + CHANGE into the more
    # recent season (vol_16 - vol_15); all predictors <=16, outcome at 20+.
    a16 = df[df["res_age_16"] >= 2].copy()
    a16["chg_15_16"] = a16["vol_age_16"] - a16["vol_age_15"]
    for c in ["vol_age_15", "chg_15_16"]:
        a16[c + "_z"] = (a16[c] - a16[c].mean()) / a16[c].std()
    mc, dc = fit_logit(a16, ["female", "vol_age_15_z", "chg_15_16_z"])
    lvl = or_ci(mc, "vol_age_15_z")
    chg = or_ci(mc, "chg_15_16_z")
    auc_c, _, n_c = cv_auc(a16, ["female", "vol_age_15_z", "chg_15_16_z"])

    RESULTS["m1"] = dict(
        n_dropouts_15_19=len(sub), aligned=aligned,
        share_active_penultimate=share_active_penult,
        n_final16plus=len(s2),
        share_reduced_nonzero_penultimate=share_reduced_nonzero,
        share_penultimate_zero=share_penult_zero,
        share_penultimate_at_peak=share_penult_at_peak,
        share_decline_into_final=share_decline_into_final,
        change_model=dict(n=len(dc), auc=auc_c,
                          level_or=lvl[0], level_lo=lvl[1], level_hi=lvl[2], level_p=lvl[3],
                          change_or=chg[0], change_lo=chg[1], change_hi=chg[2], change_p=chg[3]))
    logger.info(f"  dropouts final 15-19: n={len(sub)}; aligned medians "
                f"T-3..T: {[aligned[f'T-{k}']['median'] for k in [3,2,1,0]]}")
    logger.info(f"  active in penultimate season: {share_active_penult:.1%}")
    logger.info(f"  final>=16 (n={len(s2)}): reduced-but-nonzero penultimate {share_reduced_nonzero:.1%}, "
                f"penultimate zero {share_penult_zero:.1%}, at-peak {share_penult_at_peak:.1%}")
    logger.info(f"  declined into final season: {share_decline_into_final:.1%}")
    logger.info(f"  change model (active@16, n={len(dc)}): level OR={lvl[0]:.2f}, change OR={chg[0]:.2f} "
                f"(p={chg[3]:.4f}), AUC={auc_c:.3f}")

    rows = [{"Quantity": f"Aligned volume T-{k} (median [IQR])",
             "Value": f"{aligned[f'T-{k}']['median']:.0f} [{aligned[f'T-{k}']['q25']:.0f}-{aligned[f'T-{k}']['q75']:.0f}]",
             "n": aligned[f"T-{k}"]["n"]} for k in [3, 2, 1, 0]]
    rows += [
        {"Quantity": "Dropouts (final season at ages 15-19)", "Value": len(sub), "n": len(sub)},
        {"Quantity": "Active (>0 meets) in penultimate season", "Value": f"{share_active_penult:.1%}", "n": len(s1)},
        {"Quantity": "Reduced-but-nonzero penultimate season (final age >=16)", "Value": f"{share_reduced_nonzero:.1%}", "n": len(s2)},
        {"Quantity": "Penultimate season zero (gap year before final)", "Value": f"{share_penult_zero:.1%}", "n": len(s2)},
        {"Quantity": "Penultimate at personal peak (abrupt profile)", "Value": f"{share_penult_at_peak:.1%}", "n": len(s2)},
        {"Quantity": "Volume in final season below personal peak", "Value": f"{share_decline_into_final:.1%}", "n": len(s3)},
        {"Quantity": "Change model among active at 16: level at 15 OR (per SD)",
         "Value": f"{lvl[0]:.2f} [{lvl[1]:.2f}, {lvl[2]:.2f}]", "n": len(dc)},
        {"Quantity": "Change model among active at 16: change 15->16 OR (per SD)",
         "Value": f"{chg[0]:.2f} [{chg[1]:.2f}, {chg[2]:.2f}]", "n": len(dc)},
    ]
    pd.DataFrame(rows).to_csv(TAB_DIR / "tableS20_exit_aligned.csv", index=False)


def m6_evalues(df):
    logger.info("=== M6. E-VALUES ON THE PRIMARY SPECIFICATION ===")
    p_out = df["aktiv_senior"].mean()
    o = RESULTS["primary"]
    rr = np.sqrt(o["vol_or"])          # OR -> RR approx for common outcome
    rr_lo = np.sqrt(o["vol_lo"])
    e_point, e_lo = evalue_rr(rr), evalue_rr(rr_lo)
    # baseline-only Cox HR from S16 (volume per SD)
    hr = None
    try:
        s16 = pd.read_csv(TAB_DIR / "tableS16_cox_with_structural.csv")
        row = s16[s16.iloc[:, 0].astype(str).str.contains("vol_pre", case=False, na=False)]
        if len(row):
            hr = float(row.iloc[0][[c for c in s16.columns if "HR" in c or "exp" in c][0]])
    except Exception:
        pass
    res = dict(outcome_prev=float(p_out), or_=o["vol_or"], rr_approx=float(rr),
               evalue_point=float(e_point), evalue_ci=float(e_lo), cox_hr_s16=hr)
    if hr:
        rr_hr = (1 - 0.5 ** np.sqrt(1 / hr)) / (1 - 0.5 ** np.sqrt(hr))  # common-outcome HR->RR
        res["cox_rr_approx"] = float(rr_hr)
        res["cox_evalue"] = float(evalue_rr(rr_hr))
    RESULTS["m6"] = res
    logger.info(f"  primary OR {o['vol_or']:.2f} -> RR~{rr:.2f} -> E-value {e_point:.2f} (CI bound {e_lo:.2f})"
                + (f"; Cox HR {hr} -> E {res.get('cox_evalue'):.2f}" if hr else ""))
    old = TAB_DIR / "tableS3_e_values.csv"
    if old.exists():
        old.rename(TAB_DIR / "tableS3_e_values_OLD.csv")
    rows = [{"Effect": "Pre-milestone volume, primary logistic (per SD)",
             "Estimate": f"OR {o['vol_or']:.2f} [{o['vol_lo']:.2f}, {o['vol_hi']:.2f}]",
             "Approx. RR (common outcome, sqrt-OR)": round(float(rr), 2),
             "E-value (point)": round(float(e_point), 2),
             "E-value (CI bound)": round(float(e_lo), 2),
             "Note": "Outcome prevalence 16.4%; OR converted to RR before E-value (VanderWeele & Ding 2017)"}]
    if hr:
        rows.append({"Effect": "Pre-milestone volume, baseline-only Cox (per SD)",
                     "Estimate": f"HR {hr:.2f}",
                     "Approx. RR (common outcome, sqrt-OR)": round(res["cox_rr_approx"], 2),
                     "E-value (point)": round(res["cox_evalue"], 2),
                     "E-value (CI bound)": "",
                     "Note": "HR converted for common outcome"})
    pd.DataFrame(rows).to_csv(TAB_DIR / "tableS3_e_values.csv", index=False)


def m7_missing(df, covars):
    logger.info("=== M7. MISSING DATA: MI, INCLUDED-VS-EXCLUDED, SAMPLE FLOW ===")
    base_cols = ["aktiv_senior", "female", "tyrving_best", "hhi_early", "vol_pre_milepael"]
    d = df[base_cols + ["athlete_id"]].copy()
    complete = d.dropna(subset=base_cols)
    incomplete = d[d[base_cols].isna().any(axis=1)]
    comp_rows = []
    for c in ["aktiv_senior", "female", "vol_pre_milepael", "hhi_early", "tyrving_best"]:
        comp_rows.append({"Variable": c,
                          "Included (complete case)": round(float(complete[c].mean()), 3),
                          "Excluded (any missing)": round(float(incomplete[c].mean()), 3),
                          "n included": int(complete[c].notna().sum()),
                          "n excluded (non-missing on var)": int(incomplete[c].notna().sum())})
    pd.DataFrame(comp_rows).to_csv(TAB_DIR / "tableS26_missing_comparison.csv", index=False)
    RESULTS["m7_excluded_retention"] = float(incomplete["aktiv_senior"].mean())
    RESULTS["m7_included_retention"] = float(complete["aktiv_senior"].mean())

    # multiple imputation (m=20) for tyrving_best & hhi_early; sex-unknown athletes
    # are excluded BEFORE imputation (sex is never imputed), matching S-M3.
    d = d.dropna(subset=["female"]).reset_index(drop=True)
    ors = []
    feat = ["aktiv_senior", "female", "tyrving_best", "hhi_early", "vol_pre_milepael"]
    for m_i in range(20):
        imp = IterativeImputer(random_state=m_i, max_iter=15, sample_posterior=True)
        arr = imp.fit_transform(d[feat])
        di = pd.DataFrame(arr, columns=feat)
        di["aktiv_senior"] = d["aktiv_senior"].values  # outcome never imputed (no missing)
        di["female"] = d["female"].values              # sex never imputed
        for c in ["tyrving_best", "hhi_early", "vol_pre_milepael"]:
            di[c + "_z"] = (di[c] - di[c].mean()) / di[c].std()
        mi_m, _ = fit_logit(di, ["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"])
        ors.append((mi_m.params["vol_pre_milepael_z"], mi_m.bse["vol_pre_milepael_z"],
                    mi_m.params["hhi_early_z"], mi_m.bse["hhi_early_z"]))
    b = np.array([o[0] for o in ors]); se = np.array([o[1] for o in ors])
    bh = np.array([o[2] for o in ors]); seh = np.array([o[3] for o in ors])

    def rubin(b, se):
        qbar = b.mean(); ubar = (se ** 2).mean(); bvar = b.var(ddof=1)
        t = ubar + (1 + 1 / len(b)) * bvar
        return qbar, np.sqrt(t)

    qv, tv = rubin(b, se); qh, th = rubin(bh, seh)
    RESULTS["m7_mi"] = dict(vol_or=float(np.exp(qv)), vol_lo=float(np.exp(qv - 1.96 * tv)),
                            vol_hi=float(np.exp(qv + 1.96 * tv)),
                            hhi_or=float(np.exp(qh)), hhi_lo=float(np.exp(qh - 1.96 * th)),
                            hhi_hi=float(np.exp(qh + 1.96 * th)), m=20, n=int(len(d)))
    logger.info(f"  MI (m=20, n={len(d)}): vol OR={np.exp(qv):.3f} "
                f"[{np.exp(qv-1.96*tv):.3f},{np.exp(qv+1.96*tv):.3f}]; "
                f"HHI OR={np.exp(qh):.3f} [{np.exp(qh-1.96*th):.3f},{np.exp(qh+1.96*th):.3f}]")
    pd.DataFrame([
        {"Model": "Complete case (primary)", "n": RESULTS["primary"]["n"],
         "Volume OR [95% CI]": f"{RESULTS['primary']['vol_or']:.2f} [{RESULTS['primary']['vol_lo']:.2f}, {RESULTS['primary']['vol_hi']:.2f}]",
         "HHI OR [95% CI]": f"{RESULTS['primary']['hhi_or']:.2f} [{RESULTS['primary']['hhi_lo']:.2f}, {RESULTS['primary']['hhi_hi']:.2f}]"},
        {"Model": "Multiple imputation (m=20, Rubin)", "n": int(len(d)),
         "Volume OR [95% CI]": f"{np.exp(qv):.2f} [{np.exp(qv-1.96*tv):.2f}, {np.exp(qv+1.96*tv):.2f}]",
         "HHI OR [95% CI]": f"{np.exp(qh):.2f} [{np.exp(qh-1.96*th):.2f}, {np.exp(qh+1.96*th):.2f}]"},
    ]).to_csv(TAB_DIR / "tableS22_mi_sensitivity.csv", index=False)

    # sample flow + Table 4 n resolution
    n_total = len(df)
    n_sex = int(df["female"].notna().sum())
    n_l4 = RESULTS["primary"]["n"]
    a14 = df[df["res_age_14"] >= 1]  # >=1 result at 14 (as in 13_ script via career file)
    a14_career_n = RESULTS.get("m1_active14_n")
    n_t4 = int(a14[["aktiv_senior", "female", "tyrving_best", "vol_age_14"]].dropna().shape[0])
    tyr_missing_active14 = float(a14["tyrving_best"].isna().mean())
    tyr_missing_inactive14 = float(df[df["res_age_14"] < 1]["tyrving_best"].isna().mean())
    RESULTS["m7_flow"] = dict(n_total=n_total, n_sex_known=n_sex, n_l4=n_l4,
                              n_active14=len(a14), n_table4=n_t4,
                              tyr_missing_active14=tyr_missing_active14,
                              tyr_missing_inactive14=tyr_missing_inactive14)
    logger.info(f"  Table 4 resolution: active@14 n={len(a14)}, complete-case n={n_t4}; "
                f"tyrving missing among active@14: {tyr_missing_active14:.1%} vs inactive@14: {tyr_missing_inactive14:.1%}")
    a16 = df[df["res_age_16"] >= 2]
    pd.DataFrame([
        {"Analysis": "Total cohort", "n": n_total, "Definition": "All included athletes"},
        {"Analysis": "Sex known", "n": n_sex, "Definition": "gender M/F (24 unknown; excluded from models, included in KM totals)"},
        {"Analysis": "Primary logistic L1-L4", "n": n_l4, "Definition": "complete case on sex, Tyrving, HHI, pre-milestone volume; L1-L3 fitted on the same fixed sample"},
        {"Analysis": "Level-vs-change (Table 4)", "n": n_t4, "Definition": ">=1 result at age 14, complete case on sex, Tyrving, vol_14; Tyrving missingness is concentrated among early-inactive athletes"},
        {"Analysis": "Change model, active at 16 (new)", "n": int(len(a16)), "Definition": ">=2 results at age 16"},
        {"Analysis": "Multiple imputation", "n": n_total - (n_total - n_sex), "Definition": "all athletes with known sex; Tyrving & HHI imputed (m=20)"},
    ]).to_csv(TAB_DIR / "tableS19_sample_flow.csv", index=False)


def m8_hhi(df, kar, covars):
    logger.info("=== M8. HHI COUNT-DEPENDENCE STRESS TESTS ===")
    # results in first three active seasons (basis of hhi_early)
    per_year = kar.groupby(["athlete_id", "year"]).size().rename("n").reset_index()
    per_year = per_year.sort_values(["athlete_id", "year"])
    first3 = per_year.groupby("athlete_id").head(3).groupby("athlete_id")["n"].sum().rename("res_first3")
    d = df.merge(first3, on="athlete_id", how="left")
    corr_res = float(d[["hhi_early", "res_first3"]].corr(method="spearman").iloc[0, 1])
    corr_vol = float(d[["hhi_early", "vol_pre_milepael"]].corr(method="spearman").iloc[0, 1])
    RESULTS["m8_corr"] = dict(hhi_vs_res_first3=corr_res, hhi_vs_volpre=corr_vol)
    logger.info(f"  Spearman: HHI~results(first 3 seasons)={corr_res:.3f}, HHI~vol_pre={corr_vol:.3f}")

    rows = [{"Model": "Primary L4 (all)", "n": RESULTS["primary"]["n"],
             "HHI OR [95% CI]": f"{RESULTS['primary']['hhi_or']:.2f} [{RESULTS['primary']['hhi_lo']:.2f}, {RESULTS['primary']['hhi_hi']:.2f}]",
             "Volume OR": f"{RESULTS['primary']['vol_or']:.2f}"}]
    for cut in [5, 8]:
        sub = d[d["res_first3"] >= cut].copy()
        for c in ["tyrving_best", "hhi_early", "vol_pre_milepael"]:
            sub[c + "_z"] = (sub[c] - sub[c].mean()) / sub[c].std()
        m, dd = fit_logit(sub, covars)
        o = or_ci(m, "hhi_early_z"); v = or_ci(m, "vol_pre_milepael_z")
        rows.append({"Model": f"Restricted: >= {cut} results in first three seasons", "n": len(dd),
                     "HHI OR [95% CI]": f"{o[0]:.2f} [{o[1]:.2f}, {o[2]:.2f}]",
                     "Volume OR": f"{v[0]:.2f}"})
        RESULTS[f"m8_ge{cut}"] = dict(n=len(dd), hhi_or=o[0], hhi_lo=o[1], hhi_hi=o[2], hhi_p=o[3])
        logger.info(f"  >= {cut} results: n={len(dd)}, HHI OR={o[0]:.2f} [{o[1]:.2f},{o[2]:.2f}], vol OR={v[0]:.2f}")
    # finite-sample-corrected index
    sub = d[d["res_first3"] >= 2].copy()
    sub["hhi_corr"] = (sub["hhi_early"] - 1 / sub["res_first3"]) / (1 - 1 / sub["res_first3"])
    sub = sub[np.isfinite(sub["hhi_corr"])]
    for c in ["tyrving_best", "vol_pre_milepael", "hhi_corr"]:
        sub[c + "_z"] = (sub[c] - sub[c].mean()) / sub[c].std()
    m, dd = fit_logit(sub, ["female", "tyrving_best_z", "hhi_corr_z", "vol_pre_milepael_z"])
    o = or_ci(m, "hhi_corr_z")
    rows.append({"Model": "Finite-sample-corrected HHI* = (HHI - 1/n)/(1 - 1/n)", "n": len(dd),
                 "HHI OR [95% CI]": f"{o[0]:.2f} [{o[1]:.2f}, {o[2]:.2f}]",
                 "Volume OR": f"{or_ci(m, 'vol_pre_milepael_z')[0]:.2f}"})
    RESULTS["m8_corrected"] = dict(n=len(dd), hhi_or=o[0], hhi_lo=o[1], hhi_hi=o[2], hhi_p=o[3])
    logger.info(f"  corrected HHI*: n={len(dd)}, OR={o[0]:.2f} [{o[1]:.2f},{o[2]:.2f}] p={o[3]:.4f}")
    pd.DataFrame(rows).to_csv(TAB_DIR / "tableS21_hhi_stress.csv", index=False)


def m9_calibration(df, covars):
    logger.info("=== M9. CV CALIBRATION + TABLE 6 WITH BOOTSTRAP CIs ===")
    d = df[covars + ["aktiv_senior", "vol_pre_milepael"]].dropna()
    X, y = d[covars].values, d["aktiv_senior"].values
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    p_oof = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        mdl = lr_unpenalized().fit(X[tr], y[tr])
        p_oof[te] = mdl.predict_proba(X[te])[:, 1]
    lp = np.log(p_oof / (1 - p_oof))
    cal = sm.Logit(y, sm.add_constant(lp)).fit(disp=0)
    slope, icpt = float(cal.params[1]), float(cal.params[0])
    brier = float(np.mean((p_oof - y) ** 2))
    RESULTS["m9_cal"] = dict(slope=slope, intercept=icpt, brier=brier, n=len(y))
    logger.info(f"  CV calibration: slope={slope:.3f}, intercept={icpt:.3f}, Brier={brier:.4f}")
    pd.DataFrame([{"Metric": "Calibration slope (cross-validated)", "Value": round(slope, 3)},
                  {"Metric": "Calibration intercept", "Value": round(icpt, 3)},
                  {"Metric": "Brier score", "Value": round(brier, 4)},
                  {"Metric": "n", "Value": len(y)}]).to_csv(TAB_DIR / "tableS24_calibration_slope.csv", index=False)

    # Table 6 on the FULL cohort with one denominator + bootstrap CIs + absolute risks
    full = df[["aktiv_senior", "vol_pre_milepael"]].dropna()
    yF, vF = full["aktiv_senior"].values, full["vol_pre_milepael"].values

    def metrics(y, v, thr):
        flag = v < thr
        dropout = (y == 0)
        tp = (flag & dropout).sum(); fp = (flag & ~dropout).sum()
        fn = (~flag & dropout).sum(); tn = (~flag & ~dropout).sum()
        return dict(flagged=flag.mean(), sens=tp / max(tp + fn, 1), spec=tn / max(tn + fp, 1),
                    ppv=tp / max(tp + fp, 1) if flag.sum() else np.nan,
                    npv=tn / max(tn + fn, 1),
                    ret_flag=y[flag].mean() if flag.sum() else np.nan,
                    ret_unflag=y[~flag].mean())

    rows = []
    B = 2000
    for thr in [5, 8, 10, 15]:
        m0 = metrics(yF, vF, thr)
        boots = {k: [] for k in m0}
        idx = np.arange(len(yF))
        for _ in range(B):
            bi = RNG.choice(idx, size=len(idx), replace=True)
            mb = metrics(yF[bi], vF[bi], thr)
            for k in boots:
                boots[k].append(mb[k])
        ci = {k: (np.nanpercentile(boots[k], 2.5), np.nanpercentile(boots[k], 97.5)) for k in boots}
        rows.append({
            "Threshold (vol <)": thr,
            "Flagged %": f"{m0['flagged']*100:.1f}",
            "Sensitivity [95% CI]": f"{m0['sens']:.2f} [{ci['sens'][0]:.2f}, {ci['sens'][1]:.2f}]",
            "Specificity [95% CI]": f"{m0['spec']:.2f} [{ci['spec'][0]:.2f}, {ci['spec'][1]:.2f}]",
            "PPV [95% CI]": f"{m0['ppv']:.2f} [{ci['ppv'][0]:.2f}, {ci['ppv'][1]:.2f}]",
            "NPV [95% CI]": f"{m0['npv']:.2f} [{ci['npv'][0]:.2f}, {ci['npv'][1]:.2f}]",
            "Senior retention, flagged [95% CI]": f"{m0['ret_flag']*100:.1f}% [{ci['ret_flag'][0]*100:.1f}, {ci['ret_flag'][1]*100:.1f}]",
            "Senior retention, unflagged [95% CI]": f"{m0['ret_unflag']*100:.1f}% [{ci['ret_unflag'][0]*100:.1f}, {ci['ret_unflag'][1]*100:.1f}]",
        })
        if thr == 10:
            RESULTS["m9_thr10"] = {k: float(v) for k, v in m0.items()}

    # Q8 (round-2): composition of the flagged group + activity-at-17 outcome
    flag10 = full["vol_pre_milepael"] < 10
    zero_share = float((full.loc[flag10, "vol_pre_milepael"] == 0).mean())
    reachable = full.loc[flag10, "vol_pre_milepael"].between(1, 9, inclusive="both")
    RESULTS["q8_flag_composition"] = dict(
        flagged_n=int(flag10.sum()), zero_share=zero_share,
        reachable_share=float(reachable.mean()),
        reachable_pct_of_cohort=float((flag10 & (full["vol_pre_milepael"] >= 1)).mean()))
    a17 = df[["aktiv_17", "vol_pre_milepael"]].dropna()
    m17 = metrics(a17["aktiv_17"].values, a17["vol_pre_milepael"].values, 10)
    RESULTS["q8_age17_outcome_thr10"] = {k: float(v) for k, v in m17.items()}
    logger.info(f"  Q8: flagged<10 zero-share={zero_share:.1%}, reachable(1-9)={reachable.mean():.1%}; "
                f"age-17 outcome thr<10: PPV={m17['ppv']:.2f}, sens={m17['sens']:.2f}, "
                f"active17 flagged={m17['ret_flag']:.1%} vs unflagged={m17['ret_unflag']:.1%}")
    old = TAB_DIR / "table6_NEW_prospective_calibration.csv"
    if old.exists():
        old.rename(TAB_DIR / "table6_NEW_prospective_calibration_OLD.csv")
    pd.DataFrame(rows).to_csv(TAB_DIR / "table6_NEW_prospective_calibration.csv", index=False)
    logger.info(f"  Table 6 regenerated on one denominator (n={len(yF)}), thr<10: "
                f"{RESULTS['m9_thr10']}")

    # performance-trajectory competitor (baseline-aligned delta 13->14)
    dd = df.copy()
    dd["tyr_delta_13_14"] = dd["tyrving_age_14"] - dd["tyrving_age_13"]
    dd["tyr_delta_13_14_z"] = (dd["tyr_delta_13_14"] - dd["tyr_delta_13_14"].mean()) / dd["tyr_delta_13_14"].std()
    res = {}
    for label, cov in [("sex+Tyrving best", ["female", "tyrving_best_z"]),
                       ("sex+Tyrving best+delta13-14", ["female", "tyrving_best_z", "tyr_delta_13_14_z"]),
                       ("sex+volume", ["female", "vol_pre_milepael_z"]),
                       ("all", ["female", "tyrving_best_z", "tyr_delta_13_14_z", "vol_pre_milepael_z"])]:
        auc, _, n = cv_auc(dd, cov)
        res[label] = dict(auc=auc, n=n)
        logger.info(f"  AUC {label}: {auc:.3f} (n={n})")
    RESULTS["m9_perf_traj"] = res


def m13_club(df, covars):
    logger.info("=== M13. CLUB-LEVEL ICC AND RANDOM-INTERCEPT REFIT ===")
    d = df[covars + ["aktiv_senior", "klubb", "vol_pre_milepael"]].dropna()
    mm = sm.MixedLM.from_formula("vol_pre_milepael ~ 1", groups="klubb", data=d).fit(reml=True)
    var_b = float(mm.cov_re.iloc[0, 0]); var_w = float(mm.scale)
    icc = var_b / (var_b + var_w)
    RESULTS["m13_icc"] = dict(icc=icc, n_clubs=int(d["klubb"].nunique()), n=len(d))
    logger.info(f"  ICC(vol_pre by club) = {icc:.3f} across {d['klubb'].nunique()} clubs")
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    fml = "aktiv_senior ~ female + tyrving_best_z + hhi_early_z + vol_pre_milepael_z"
    md = BinomialBayesMixedGLM.from_formula(fml, {"club": "0 + C(klubb)"}, d)
    fit = md.fit_vb()
    names = list(fit.model.exog_names)
    iv = names.index("vol_pre_milepael_z")
    or_re = float(np.exp(fit.fe_mean[iv])); se = float(fit.fe_sd[iv])
    lo, hi = np.exp(fit.fe_mean[iv] - 1.96 * se), np.exp(fit.fe_mean[iv] + 1.96 * se)
    ih = names.index("hhi_early_z")
    or_hhi = float(np.exp(fit.fe_mean[ih]))
    RESULTS["m13_re"] = dict(vol_or=or_re, vol_lo=float(lo), vol_hi=float(hi), hhi_or=or_hhi)
    logger.info(f"  Club random-intercept: vol OR={or_re:.3f} [{lo:.3f},{hi:.3f}]; HHI OR={or_hhi:.3f}")
    pd.DataFrame([
        {"Quantity": "ICC of pre-milestone volume across baseline clubs", "Value": f"{icc:.3f}",
         "n": f"{len(d)} athletes, {d['klubb'].nunique()} clubs"},
        {"Quantity": "Volume OR, primary (no club terms)", "Value": f"{RESULTS['primary']['vol_or']:.2f}", "n": RESULTS["primary"]["n"]},
        {"Quantity": "Volume OR, club random intercepts (Bayes VB)", "Value": f"{or_re:.2f} [{lo:.2f}, {hi:.2f}]", "n": len(d)},
        {"Quantity": "HHI OR, club random intercepts", "Value": f"{or_hhi:.2f}", "n": len(d)},
    ]).to_csv(TAB_DIR / "tableS23_club_effects.csv", index=False)


def s1_fixed_window(df, kar, covars):
    logger.info("=== S1. FIXED-WINDOW OUTCOME (ages 20-22) ===")
    per = kar[(kar["age"] >= 20) & (kar["age"] <= 22)].groupby(["athlete_id", "age"]).size().rename("n").reset_index()
    ok = set(per[per["n"] >= 2]["athlete_id"].unique())
    d = df.copy()
    d["senior_20_22"] = d["athlete_id"].isin(ok).astype(int)
    rate = d.groupby("forste_utgave" if "forste_utgave" in d else "birth_year")["senior_20_22"].mean()
    m, dd = fit_logit(d, covars, outcome="senior_20_22")
    o = or_ci(m, "vol_pre_milepael_z")
    auc, _, n = cv_auc(d, covars, outcome="senior_20_22")
    ra = float(d[d["birth_year"] <= 2000]["senior_20_22"].mean())
    rb = float(d[d["birth_year"] >= 2001]["senior_20_22"].mean())
    RESULTS["s1"] = dict(prev=float(d["senior_20_22"].mean()), or_=o[0], lo=o[1], hi=o[2],
                         auc=auc, n=n, rate_A=ra, rate_B=rb)
    logger.info(f"  senior 20-22: prev={d['senior_20_22'].mean():.3f} (A {ra:.3f} vs B {rb:.3f}); "
                f"vol OR={o[0]:.2f} [{o[1]:.2f},{o[2]:.2f}], AUC={auc:.3f}")
    pd.DataFrame([{"Outcome": ">=2 results in any season at ages 20-22 (fixed window, observable for all)",
                   "Prevalence": f"{d['senior_20_22'].mean():.3f}",
                   "Cohort A": f"{ra:.3f}", "Cohort B": f"{rb:.3f}",
                   "Volume OR [95% CI]": f"{o[0]:.2f} [{o[1]:.2f}, {o[2]:.2f}]",
                   "CV-AUC": f"{auc:.3f}", "n": n}]).to_csv(TAB_DIR / "tableS25_fixed_window_outcome.csv", index=False)


def s9_outcome_sensitivity(df, kar, covars):
    logger.info("=== S9 REGENERATED: OUTCOME SENSITIVITY ON PRIMARY L4 SPEC ===")
    per = kar[kar["age"] >= 20].groupby(["athlete_id", "age"]).size().rename("n").reset_index()
    ge1 = set(per[per["n"] >= 1]["athlete_id"].unique())
    yrs2 = per[per["n"] >= 2].groupby("athlete_id")["age"].nunique()
    ge2_2y = set(yrs2[yrs2 >= 2].index)
    d = df.copy()
    d["out_A"] = d["athlete_id"].isin(ge1).astype(int)
    d["out_C"] = d["athlete_id"].isin(ge2_2y).astype(int)
    rows = []
    for code, col, desc in [("A", "out_A", ">=1 senior result (age 20+)"),
                            ("B", "aktiv_senior", ">=2 results in any senior year (primary)"),
                            ("C", "out_C", ">=2 results in each of two senior years")]:
        m, dd = fit_logit(d, covars, outcome=col)
        o = or_ci(m, "vol_pre_milepael_z")
        auc, _, n = cv_auc(d, covars, outcome=col)
        rows.append({"Outcome": code, "Description": desc,
                     "Retainer n": int(d[col].sum()), "Retainer %": round(100 * d[col].mean(), 1),
                     "OR (pre-milestone volume, per SD)": round(o[0], 2),
                     "95% CI": f"[{o[1]:.2f}, {o[2]:.2f}]",
                     "CV-AUC (L4)": round(auc, 3)})
        RESULTS[f"s9_{code}"] = dict(or_=o[0], lo=o[1], hi=o[2], auc=auc)
        logger.info(f"  outcome {code}: OR={o[0]:.2f}, AUC={auc:.3f}")
    old = TAB_DIR / "tableS9_outcome_sensitivity.csv"
    if old.exists():
        old.rename(TAB_DIR / "tableS9_outcome_sensitivity_OLD.csv")
    pd.DataFrame(rows).to_csv(TAB_DIR / "tableS9_outcome_sensitivity.csv", index=False)


def s8_mdor(df):
    logger.info("=== S8. LOGISTIC MINIMUM DETECTABLE OR (simulation) ===")
    n, p = RESULTS["primary"]["n"], 0.164
    found = None
    for or_try in [1.10, 1.15, 1.20, 1.25]:
        beta = np.log(or_try)
        hits = 0; S = 300
        for s in range(S):
            x = RNG.standard_normal(n)
            b0 = np.log(p / (1 - p))
            pr = 1 / (1 + np.exp(-(b0 + beta * x)))
            y = RNG.binomial(1, pr)
            try:
                m = sm.Logit(y, sm.add_constant(x)).fit(disp=0)
                if m.pvalues[1] < 0.05:
                    hits += 1
            except Exception:
                pass
        pw = hits / S
        logger.info(f"  OR {or_try}: power {pw:.2f}")
        if pw >= 0.8 and found is None:
            found = or_try
    RESULTS["s8_mdor"] = found
    logger.info(f"  Minimum detectable OR (80% power) ~ {found}")


def sex_and_table1(df):
    a20 = float(df["aktiv_20"].mean()) if "aktiv_20" in df else None
    RESULTS["aktiv_20_mean"] = a20
    RESULTS["aktiv_senior_mean"] = float(df["aktiv_senior"].mean())
    logger.info(f"  aktiv_20 (age-specific) mean={a20}, aktiv_senior={df['aktiv_senior'].mean():.3f}")


def main():
    df, kar = load()
    covars = replicate_primary(df)
    sex_and_table1(df)
    m1_exit_aligned(df, kar)
    m6_evalues(df)
    m7_missing(df, covars)
    m8_hhi(df, kar, covars)
    m9_calibration(df, covars)
    m13_club(df, covars)
    s1_fixed_window(df, kar, covars)
    s9_outcome_sensitivity(df, kar, covars)
    s8_mdor(df)
    with open(HERE / "revision_results.json", "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    logger.info("=== ALL REVISION ANALYSES DONE -> revision_results.json ===")


if __name__ == "__main__":
    main()
