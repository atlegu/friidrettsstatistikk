"""
Steg 9: Robusthetsanalyser for PSE-paper.

Kjører:
1. Schoenfeld residuals test for PH-antakelse
2. Cluster-robust SE (athletes within clubs)
3. E-value for unmeasured confounding
4. Sample size sensitivity (minimum detectable HR)
5. Complete-case vs simple imputation
6. Time-stratified Cox (if PH violated)
7. Subgroup analyses by sex
"""

import logging
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
ANALYSE_FILE = DATA_DIR / "analysedata_utvidet.csv"
OUT_DIR = DATA_DIR.parent / "submission_pse"
TAB_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"

mpl.rcParams["figure.dpi"] = 150
mpl.rcParams["savefig.dpi"] = 150
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["font.size"] = 9


def load_cox_data():
    df = pd.read_csv(ANALYSE_FILE)
    df["event"] = (df["aktiv_naa"] == 0).astype(int)
    df["baseline_age"] = df["stevne_aar"] - df["birth_year"]
    df["duration_age"] = (df["alder_ved_slutt"] - df["baseline_age"]).clip(lower=0.5)
    df["female"] = (df["gender"] == "F").astype(int)
    df["kohort"] = df["birth_year"].apply(lambda y: "1998-2000" if y <= 2000 else "2001-2002")
    for c in ["tyrving_best", "vol_milepael", "hhi_early"]:
        df[f"{c}_z"] = (df[c] - df[c].mean()) / df[c].std()
    return df


# =============================================================================
# 1. PROPORTIONAL HAZARDS TEST (Schoenfeld)
# =============================================================================

def ph_test(df):
    logger.info("\n=== 1. PROPORTIONAL HAZARDS TEST (Schoenfeld) ===")
    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    cox_df = df[["duration_age", "event"] + covars].dropna()
    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col="duration_age", event_col="event")

    ph = proportional_hazard_test(cph, cox_df, time_transform="rank")
    summary = ph.summary
    summary["test_statistic"] = summary["test_statistic"].round(3)
    summary["p"] = summary["p"].round(4)

    logger.info("Schoenfeld global + individual tests:")
    for _, row in summary.iterrows():
        logger.info(f"  {row.name}: chi2={row['test_statistic']:.2f}, p={row['p']:.4f}")

    # Lagre
    summary.to_csv(TAB_DIR / "tableS1_ph_test.csv")
    return summary


# =============================================================================
# 2. CLUSTER-ROBUST SE (athletes within clubs)
# =============================================================================

def cluster_robust(df):
    logger.info("\n=== 2. CLUSTER-ROBUST SE (clubs) ===")
    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    cox_df = df[["duration_age", "event", "klubb"] + covars].dropna()
    cox_df["klubb"] = cox_df["klubb"].fillna("UNKNOWN")

    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col="duration_age", event_col="event",
            cluster_col="klubb")

    rows = []
    for cov in covars:
        rows.append({
            "Covariate": cov,
            "HR": round(np.exp(cph.params_[cov]), 3),
            "Robust CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
            "Robust CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
            "p (robust)": round(cph.summary.loc[cov, "p"], 4),
        })
    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS2_cluster_robust.csv", index=False)
    logger.info(f"  C-index (clustered): {cph.concordance_index_:.3f}")
    for _, row in tab.iterrows():
        logger.info(f"  {row['Covariate']}: HR={row['HR']}, p={row['p (robust)']}")
    return tab, cph.concordance_index_


# =============================================================================
# 3. E-VALUE FOR UNMEASURED CONFOUNDING
# =============================================================================

def e_value(hr, ci_low, ci_high):
    """E-value per VanderWeele & Ding (2017)."""
    if hr <= 1:
        hr = 1 / hr
        ci_low_new, ci_high_new = 1 / ci_high, 1 / ci_low
        ci_low, ci_high = ci_low_new, ci_high_new
    ev = hr + np.sqrt(hr * (hr - 1))
    if ci_low <= 1:
        ev_ci = 1
    else:
        ev_ci = ci_low + np.sqrt(ci_low * (ci_low - 1))
    return round(ev, 2), round(ev_ci, 2)


def compute_e_values():
    logger.info("\n=== 3. E-VALUES FOR KEY EFFECTS ===")
    rows = []
    effects = [
        ("Volume at age 15-16 (per SD)", 0.35, 0.33, 0.38),
        ("Championship types (per type)", 0.74, 0.69, 0.80),
        ("Tyrving at baseline (per SD, M2)", 0.86, 0.82, 0.90),
    ]
    for name, hr, ci_lo, ci_hi in effects:
        ev, ev_ci = e_value(hr, ci_lo, ci_hi)
        rows.append({
            "Effect": name,
            "HR": hr,
            "CI": f"[{ci_lo}, {ci_hi}]",
            "E-value (point)": ev,
            "E-value (CI bound)": ev_ci,
        })
        logger.info(f"  {name}: E={ev} (CI bound {ev_ci})")
    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS3_e_values.csv", index=False)
    return tab


# =============================================================================
# 4. SAMPLE SIZE / MINIMUM DETECTABLE HR
# =============================================================================

def sample_size_sensitivity(df):
    """
    For complete-population designs, traditional power is N/A. We instead
    compute the minimum detectable HR given observed event count, sample
    size, and conventional Type I error (α=.05) and Type II error (β=.20,
    i.e. 80% power) per Hsieh & Lavori (2000).
    """
    logger.info("\n=== 4. SAMPLE SIZE / MINIMUM DETECTABLE HR ===")
    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z"]
    cox_df = df[["duration_age", "event"] + covars].dropna()
    n = len(cox_df)
    n_events = cox_df["event"].sum()

    # Hsieh-Lavori formula for Cox PH minimum detectable log-HR:
    # n_events = (z_alpha + z_beta)^2 / (sigma^2 * log(HR)^2)
    # where sigma^2 = variance of the standardized covariate (=1 for z-scored)
    # Solve for log(HR):  |log(HR)| = (z_alpha + z_beta) / (sigma * sqrt(n_events))
    from scipy.stats import norm
    alpha, beta = 0.05, 0.20
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(1 - beta)
    min_log_hr = (z_alpha + z_beta) / np.sqrt(n_events)
    min_hr = np.exp(min_log_hr)

    logger.info(f"  N = {n}, events = {int(n_events)} ({n_events/n*100:.1f}%)")
    logger.info(f"  Minimum detectable HR (80% power, α=.05): {min_hr:.3f}")
    logger.info(f"  Equivalently, HR < {1/min_hr:.3f} is detectable")

    # For cohort-specific
    rows = [{
        "Cohort": "Combined", "N": n, "Events": int(n_events),
        "Min detectable HR": round(min_hr, 3),
    }]
    for cohort in ["1998-2000", "2001-2002"]:
        sub = df[df["kohort"] == cohort][covars + ["duration_age", "event"]].dropna()
        n_c = len(sub)
        n_e = sub["event"].sum()
        if n_e > 0:
            min_log_hr_c = (z_alpha + z_beta) / np.sqrt(n_e)
            rows.append({
                "Cohort": cohort, "N": n_c, "Events": int(n_e),
                "Min detectable HR": round(np.exp(min_log_hr_c), 3),
            })

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS4_sample_size.csv", index=False)
    return tab


# =============================================================================
# 5. COMPLETE CASE vs IMPUTATION SENSITIVITY
# =============================================================================

def imputation_sensitivity(df):
    logger.info("\n=== 5. COMPLETE-CASE vs MEAN-IMPUTATION SENSITIVITY ===")
    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]

    # Complete case
    cc = df[["duration_age", "event"] + covars].dropna()
    cph_cc = CoxPHFitter()
    cph_cc.fit(cc, duration_col="duration_age", event_col="event")

    # Mean imputation for missing covariates (sensitivity)
    imp = df[["duration_age", "event"] + covars].copy()
    for c in covars:
        imp[c] = imp[c].fillna(imp[c].mean() if imp[c].dtype != "O" else imp[c].mode()[0])
    cph_imp = CoxPHFitter()
    cph_imp.fit(imp, duration_col="duration_age", event_col="event")

    rows = []
    for cov in covars:
        rows.append({
            "Covariate": cov,
            "HR (complete case)": round(np.exp(cph_cc.params_[cov]), 3),
            "n (CC)": len(cc),
            "HR (mean imputation)": round(np.exp(cph_imp.params_[cov]), 3),
            "n (imputed)": len(imp),
        })
    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS5_imputation.csv", index=False)
    logger.info(f"  Complete case n={len(cc)}, Imputed n={len(imp)}")
    for _, row in tab.iterrows():
        logger.info(f"  {row['Covariate']}: HR_CC={row['HR (complete case)']}, HR_imp={row['HR (mean imputation)']}")
    return tab


# =============================================================================
# 6. STRATIFIED COX (if PH violated)
# =============================================================================

def stratified_cox(df, ph_summary):
    """If PH assumption is violated for any covariate, fit stratified Cox."""
    logger.info("\n=== 6. STRATIFIED COX (if PH violated) ===")
    violators = ph_summary[ph_summary["p"] < 0.05].index.tolist()
    logger.info(f"  Variables violating PH (p<.05): {violators or 'none'}")

    if not violators:
        logger.info("  No violations — stratification not needed.")
        return None

    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    strata_var = violators[0]  # stratify on first violator if any
    if strata_var in covars:
        covars.remove(strata_var)

    sub = df[["duration_age", "event", strata_var] + covars].dropna()
    # Discretize continuous strata
    if sub[strata_var].nunique() > 5:
        sub[strata_var] = pd.qcut(sub[strata_var], q=3, labels=["low", "mid", "high"],
                                    duplicates="drop")
    cph = CoxPHFitter()
    cph.fit(sub, duration_col="duration_age", event_col="event",
            strata=[strata_var])
    rows = [{"Covariate": cov,
             "HR (strat. by " + strata_var + ")": round(np.exp(cph.params_[cov]), 3),
             "p": round(cph.summary.loc[cov, "p"], 4)} for cov in covars]
    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS6_stratified_cox.csv", index=False)
    return tab


# =============================================================================
# 7. SUBGROUP ANALYSES BY SEX
# =============================================================================

def subgroup_by_sex(df):
    logger.info("\n=== 7. SUBGROUP ANALYSES BY SEX ===")
    covars = ["tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    rows = []
    for sex, label in [("M", "Male"), ("F", "Female")]:
        sub = df[df["gender"] == sex][["duration_age", "event"] + covars].dropna()
        cph = CoxPHFitter()
        cph.fit(sub, duration_col="duration_age", event_col="event")
        for cov in covars:
            rows.append({
                "Sex": label, "n": len(sub),
                "Covariate": cov,
                "HR": round(np.exp(cph.params_[cov]), 3),
                "CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
                "CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
                "p": round(cph.summary.loc[cov, "p"], 4),
            })
        logger.info(f"  {label} (n={len(sub)}): C-index={cph.concordance_index_:.3f}")
    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS7_subgroup_sex.csv", index=False)
    return tab


# =============================================================================
# MAIN
# =============================================================================

def main():
    df = load_cox_data()
    logger.info(f"Lastet {len(df)} utøvere\n")

    ph_summary = ph_test(df)
    cluster_tab, c_idx_cluster = cluster_robust(df)
    e_tab = compute_e_values()
    sample_size_sensitivity(df)
    imputation_sensitivity(df)
    stratified_cox(df, ph_summary)
    subgroup_by_sex(df)

    logger.info("\n=== ALLE SENSITIVITY-ANALYSER FERDIG ===")
    logger.info(f"Output: {TAB_DIR}")


if __name__ == "__main__":
    main()
