"""
Steg 13: Adressere reviewens fundamentale kritikk.

Reviewens hovedpunkter:
1. Look-ahead bias i Cox-modellene (vol_milestone er post-baseline)
2. Outcome-estimand uklart (binær senior status vs time-to-cessation)
3. Strukturelle kontroller (region, klubb, RAE) mangler
4. Pull-back vs typologi-separasjon ikke skilt
5. Behavior-vs-performance ikke tids-aligned

Løsninger:
A) Primær analyse: LOGISTIC REGRESSION for binær senior-retention
   - Bruker KUN baseline (alder 13-14) prediktorer
   - Adderer strukturelle kontroller stepwise
B) Sekundær Cox: nå eksplisitt "time-to-cessation"
   - Med pre-milestone volum (ikke post-baseline)
C) Within-athlete decline test (vol_trend conditional on baseline volume)
D) Time-aligned behavior-vs-performance comparison
"""

import logging
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
import statsmodels.api as sm

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
ANALYSE_FILE = DATA_DIR / "analysedata_utvidet.csv"
OUT_DIR = DATA_DIR.parent / "submission_pse"
TAB_DIR = OUT_DIR / "tables"


def load_data():
    df = pd.read_csv(ANALYSE_FILE)
    df["female"] = (df["gender"] == "F").astype(int)
    df["q1_born"] = (df["fodt_kvartal"] == "Q1").astype(int)
    df["q4_born"] = (df["fodt_kvartal"] == "Q4").astype(int)
    df["region_ostlandet"] = (df["region"] == "Østlandet").astype(int)
    df["region_midt"] = (df["region"] == "Midt-Norge").astype(int)
    # (Vestlandet = reference)

    # Standardize continuous covariates
    for c in ["tyrving_best", "vol_milepael", "hhi_early", "vol_pre_milepael", "klubb_storrelse"]:
        if c in df.columns:
            v = df[c]
            if v.std() > 0:
                df[f"{c}_z"] = (v - v.mean()) / v.std()

    # Survival variables
    df["event"] = (df["aktiv_naa"] == 0).astype(int)
    df["baseline_age"] = df["stevne_aar"] - df["birth_year"]
    df["duration_age"] = (df["alder_ved_slutt"] - df["baseline_age"]).clip(lower=0.5)
    df["kohort"] = df["birth_year"].apply(lambda y: "1998-2000" if y <= 2000 else "2001-2002")
    return df


# =============================================================================
# A. PRIMARY ANALYSIS: Logistic regression with binary senior outcome
#    Uses ONLY baseline (age 13-14) predictors — no look-ahead
# =============================================================================

def primary_logistic_baseline_only(df):
    """
    Primary model: logistic regression for active_senior (binary outcome).
    Predictors: ONLY observable at end of baseline window (age 13-14).
    - vol_pre_milestone (volum ages 13-14)
    - tyrving_best at baseline
    - HHI early
    - female
    NO post-baseline predictors.
    """
    logger.info("\n=== A. PRIMARY LOGISTIC (binary senior, baseline-only predictors) ===")

    base = df.dropna(subset=["aktiv_senior", "vol_pre_milepael_z", "tyrving_best_z",
                             "hhi_early_z", "female"]).copy()

    # Build nested models
    specs = {
        "L1: Sex only": ["female"],
        "L2: + Performance (baseline)": ["female", "tyrving_best_z"],
        "L3: + Specialization (early)": ["female", "tyrving_best_z", "hhi_early_z"],
        "L4: + Volume (pre-milestone, ages 13-14)": ["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rows = []
    for name, covars in specs.items():
        sub = base[covars + ["aktiv_senior"]].dropna()
        X = sub[covars]
        y = sub["aktiv_senior"]

        # Statsmodels Logit for interpretable coefficients + CIs
        X_sm = sm.add_constant(X)
        try:
            logit = sm.Logit(y, X_sm).fit(disp=0)
            for cov in covars:
                or_val = np.exp(logit.params[cov])
                ci_lo, ci_hi = np.exp(logit.conf_int().loc[cov].values)
                p = logit.pvalues[cov]
                rows.append({
                    "Model": name, "n": len(sub), "Covariate": cov,
                    "OR": round(or_val, 3),
                    "CI low": round(ci_lo, 3), "CI high": round(ci_hi, 3),
                    "p": round(p, 4),
                })
        except Exception as e:
            logger.warning(f"  {name} failed: {e}")
            continue

        # CV-AUC
        lr = LogisticRegression(max_iter=2000)
        auc = cross_val_score(lr, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
        for r in rows[-len(covars):]:
            r["CV-AUC"] = round(auc.mean(), 3)
            r["CV-AUC SD"] = round(auc.std(), 3)
        logger.info(f"  {name}: n={len(sub)}, CV-AUC={auc.mean():.3f}±{auc.std():.3f}")

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "table3_NEW_primary_logistic.csv", index=False)
    return tab


# =============================================================================
# B. STRUCTURAL CONTROLS — add region, birth quarter, club size to primary
# =============================================================================

def structural_controls_test(df):
    """
    Test whether the volume effect survives controlling for structural variables:
    - Region (3-level: Østlandet ref, Vestlandet, Midt-Norge)
    - Birth quarter (Q1 indicator for RAE)
    - Club size at baseline
    """
    logger.info("\n=== B. STRUCTURAL CONTROLS (region, RAE, club size) ===")

    base = df.dropna(subset=["aktiv_senior", "vol_pre_milepael_z", "tyrving_best_z",
                              "hhi_early_z", "female", "klubb_storrelse_z"]).copy()

    full_covars = [
        "female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z",
        "q1_born", "q4_born",
        "region_ostlandet", "region_midt",
        "klubb_storrelse_z",
    ]
    sub = base[full_covars + ["aktiv_senior"]].dropna()
    X_sm = sm.add_constant(sub[full_covars])
    logit = sm.Logit(sub["aktiv_senior"], X_sm).fit(disp=0)

    rows = []
    for cov in full_covars:
        or_val = np.exp(logit.params[cov])
        ci_lo, ci_hi = np.exp(logit.conf_int().loc[cov].values)
        rows.append({
            "Covariate": cov, "OR": round(or_val, 3),
            "CI low": round(ci_lo, 3), "CI high": round(ci_hi, 3),
            "p": round(logit.pvalues[cov], 4),
        })
    tab = pd.DataFrame(rows)

    # AUC
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    lr = LogisticRegression(max_iter=2000)
    auc = cross_val_score(lr, sub[full_covars], sub["aktiv_senior"], cv=cv, scoring="roc_auc", n_jobs=-1)
    tab["n"] = len(sub)
    tab["CV-AUC"] = round(auc.mean(), 3)

    tab.to_csv(TAB_DIR / "tableS13_structural_controls.csv", index=False)
    logger.info(f"  Full model with controls: n={len(sub)}, AUC={auc.mean():.3f}±{auc.std():.3f}")
    for _, row in tab.iterrows():
        logger.info(f"  {row['Covariate']}: OR={row['OR']} [{row['CI low']}, {row['CI high']}], p={row['p']}")

    # Compare: vol_pre_milepael_z without vs with structural controls
    sub_no = base[["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z", "aktiv_senior"]].dropna()
    X_sm_no = sm.add_constant(sub_no[["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"]])
    logit_no = sm.Logit(sub_no["aktiv_senior"], X_sm_no).fit(disp=0)
    or_no = np.exp(logit_no.params["vol_pre_milepael_z"])
    or_yes = np.exp(logit.params["vol_pre_milepael_z"])
    logger.info(f"\n  vol_pre_milestone OR without controls: {or_no:.3f}")
    logger.info(f"  vol_pre_milestone OR WITH controls:    {or_yes:.3f}")
    logger.info(f"  Change: {(or_yes - or_no) / or_no * 100:+.1f}%")

    return tab


# =============================================================================
# C. PULL-BACK vs TYPOLOGY: vol_trend conditional on baseline volume
# =============================================================================

def pullback_vs_typology(df):
    """
    Test whether within-athlete VOLUME DECLINE (vol_trend) predicts dropout
    conditional on baseline volume.

    If "pulling back" is the mechanism: vol_trend should matter after controlling
    for baseline level (vol_pre_milestone).
    If just typology separation: vol_trend should add nothing once baseline is in.

    Note: vol_trend = vol_milestone - vol_pre_milestone (so this still has
    look-ahead concern). We instead use vol_age_15 - vol_age_14 as a "first
    decline" indicator, which uses two adjacent age years.
    """
    logger.info("\n=== C. PULL-BACK vs TYPOLOGY (conditional decline) ===")

    df = df.copy()
    df["vol_change_14_15"] = df["vol_age_15"] - df["vol_age_14"]
    # Standardize change
    df["vol_change_14_15_z"] = (df["vol_change_14_15"] - df["vol_change_14_15"].mean()) / df["vol_change_14_15"].std()

    # Among athletes still active at age 14 (≥1 result), does AGE-14→15 change
    # predict dropout, controlling for AGE-14 LEVEL?
    karriere = pd.read_csv(DATA_DIR / "karrieredata_utvidet.csv", low_memory=False)
    karriere["date"] = pd.to_datetime(karriere["date"], errors="coerce")
    karriere["year"] = karriere["date"].dt.year
    karriere = karriere.merge(df[["athlete_id", "birth_year"]], on="athlete_id", how="inner")
    karriere["age"] = karriere["year"] - karriere["birth_year"]

    active_at_14 = set(karriere[karriere["age"] == 14]["athlete_id"].unique())
    logger.info(f"  Athletes still active at age 14: {len(active_at_14)} of {len(df)}")

    sub = df[df["athlete_id"].isin(active_at_14)].copy()
    sub["vol_age_14_z"] = (sub["vol_age_14"] - sub["vol_age_14"].mean()) / sub["vol_age_14"].std()
    sub["vol_change_14_15_z"] = (sub["vol_change_14_15"] - sub["vol_change_14_15"].mean()) / sub["vol_change_14_15"].std()

    # Model 1: vol at 14 only
    m1_data = sub[["aktiv_senior", "female", "tyrving_best_z", "vol_age_14_z"]].dropna()
    X1 = sm.add_constant(m1_data[["female", "tyrving_best_z", "vol_age_14_z"]])
    m1 = sm.Logit(m1_data["aktiv_senior"], X1).fit(disp=0)

    # Model 2: vol at 14 + change 14→15
    m2_data = sub[["aktiv_senior", "female", "tyrving_best_z", "vol_age_14_z", "vol_change_14_15_z"]].dropna()
    X2 = sm.add_constant(m2_data[["female", "tyrving_best_z", "vol_age_14_z", "vol_change_14_15_z"]])
    m2 = sm.Logit(m2_data["aktiv_senior"], X2).fit(disp=0)

    rows = []
    for name, m, covs in [("M1: Volume at 14 only", m1, ["female", "tyrving_best_z", "vol_age_14_z"]),
                          ("M2: + Volume change 14→15", m2, ["female", "tyrving_best_z", "vol_age_14_z", "vol_change_14_15_z"])]:
        for c in covs:
            rows.append({
                "Model": name, "Covariate": c,
                "OR": round(np.exp(m.params[c]), 3),
                "CI low": round(np.exp(m.conf_int().loc[c, 0]), 3),
                "CI high": round(np.exp(m.conf_int().loc[c, 1]), 3),
                "p": round(m.pvalues[c], 4),
            })
        logger.info(f"  {name}: pseudo-R²={m.prsquared:.3f}, AIC={m.aic:.0f}")

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS14_pullback_vs_typology.csv", index=False)
    return tab


# =============================================================================
# D. TIME-ALIGNED behavior-vs-performance
# =============================================================================

def time_aligned_behavior_vs_performance(df):
    """
    Reviewer: behavior vs performance is asymmetric (vol at age 15-16 vs Tyrving
    at age 13-14). Now we compare BOTH measured at baseline (ages 13-14):
    - Baseline Tyrving
    - vol_pre_milestone (ages 13-14)
    """
    logger.info("\n=== D. TIME-ALIGNED BEHAVIOR-VS-PERFORMANCE ===")

    base = df.dropna(subset=["aktiv_senior", "vol_pre_milepael_z", "tyrving_best_z",
                              "female"]).copy()

    specs = {
        "Performance only (Tyrving + sex)": ["female", "tyrving_best_z"],
        "Behavior only (vol_pre + sex)": ["female", "vol_pre_milepael_z"],
        "Both behavior + performance": ["female", "tyrving_best_z", "vol_pre_milepael_z"],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rows = []
    for name, covars in specs.items():
        sub = base[covars + ["aktiv_senior"]].dropna()
        X = sub[covars]
        y = sub["aktiv_senior"]
        lr = LogisticRegression(max_iter=2000)
        auc = cross_val_score(lr, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
        rows.append({
            "Model (both ages 13-14)": name,
            "n": len(sub),
            "CV-AUC": round(auc.mean(), 3),
            "CV-AUC SD": round(auc.std(), 3),
        })
        logger.info(f"  {name}: AUC = {auc.mean():.3f} ± {auc.std():.3f}")

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS15_time_aligned_behav_vs_perf.csv", index=False)
    return tab


# =============================================================================
# E. COX TIME-TO-CESSATION (reframed, with structural controls)
# =============================================================================

def cox_time_to_cessation(df):
    """Re-frame Cox as 'time to last active season' explicitly, with controls."""
    logger.info("\n=== E. COX TIME-TO-CESSATION with structural controls ===")

    full_covars = [
        "female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z",
        "q1_born", "q4_born",
        "region_ostlandet", "region_midt",
        "klubb_storrelse_z",
    ]
    cox_df = df[["duration_age", "event"] + full_covars].dropna()
    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col="duration_age", event_col="event")

    rows = []
    for cov in full_covars:
        rows.append({
            "Covariate": cov,
            "HR": round(np.exp(cph.params_[cov]), 3),
            "CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
            "CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
            "p": round(cph.summary.loc[cov, "p"], 4),
        })
    logger.info(f"  Cox with all controls (n={len(cox_df)}, C={cph.concordance_index_:.3f}):")
    for r in rows:
        logger.info(f"    {r['Covariate']}: HR={r['HR']} [{r['CI low']}, {r['CI high']}]")
    tab = pd.DataFrame(rows)
    tab["n"] = len(cox_df)
    tab["C-index"] = round(cph.concordance_index_, 3)
    tab.to_csv(TAB_DIR / "tableS16_cox_with_structural.csv", index=False)
    return tab


# =============================================================================
# F. EARLY-WARNING with pre-milestone (truly prospective!)
# =============================================================================

def prospective_early_warning(df):
    """
    Reviewer: worked example uses future data. Redo with pre-milestone (13-14)
    volume — truly prospective at end of age 14.
    """
    logger.info("\n=== F. PROSPECTIVE EARLY-WARNING (pre-milestone volume at age 14) ===")

    df = df.dropna(subset=["aktiv_senior", "vol_pre_milepael"]).copy()
    df["dropout"] = 1 - df["aktiv_senior"]

    thresholds = [1, 3, 5, 8, 10, 15]
    rows = []
    for t in thresholds:
        flagged = df["vol_pre_milepael"] < t
        tp = ((flagged == 1) & (df["dropout"] == 1)).sum()
        fp = ((flagged == 1) & (df["dropout"] == 0)).sum()
        fn = ((flagged == 0) & (df["dropout"] == 1)).sum()
        tn = ((flagged == 0) & (df["dropout"] == 0)).sum()

        ppv = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
        npv = tn / (tn + fn) if (tn + fn) > 0 else float("nan")
        sens = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        spec = tn / (tn + fp) if (tn + fp) > 0 else float("nan")

        rows.append({
            "Threshold (pre-milestone vol <)": t,
            "Flagged %": round(flagged.mean() * 100, 1),
            "Sensitivity": round(sens, 3),
            "Specificity": round(spec, 3),
            "PPV": round(ppv, 3),
            "NPV": round(npv, 3),
        })

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "table6_NEW_prospective_calibration.csv", index=False)
    for _, row in tab.iterrows():
        logger.info(f"  vol_13_14<{row['Threshold (pre-milestone vol <)']}: PPV={row['PPV']}, sens={row['Sensitivity']}, {row['Flagged %']}% flagged")
    return tab


# =============================================================================
# G. SPECIALIZATION DIRECTION FIX — what's the REAL HHI effect?
# =============================================================================

def hhi_direction_check(df):
    """Verify HHI direction and report cohort-specific effect clearly."""
    logger.info("\n=== G. HHI DIRECTION CHECK ===")

    for cohort_name in ["1998-2000", "2001-2002", "Combined"]:
        if cohort_name == "Combined":
            sub = df
        else:
            sub = df[df["kohort"] == cohort_name]

        d = sub[["aktiv_senior", "female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"]].dropna()
        X = sm.add_constant(d[["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"]])
        try:
            m = sm.Logit(d["aktiv_senior"], X).fit(disp=0)
            hhi_or = np.exp(m.params["hhi_early_z"])
            hhi_ci = np.exp(m.conf_int().loc["hhi_early_z"].values)
            hhi_p = m.pvalues["hhi_early_z"]
            direction = "specialization → LOWER dropout" if hhi_or < 1 else "specialization → HIGHER dropout"
            logger.info(f"  {cohort_name} (n={len(d)}): HHI OR={hhi_or:.3f} [{hhi_ci[0]:.3f}, {hhi_ci[1]:.3f}] p={hhi_p:.4f} — {direction}")
        except Exception as e:
            logger.warning(f"  {cohort_name} failed: {e}")


def main():
    df = load_data()
    logger.info(f"Lastet {len(df)} utøvere\n")
    primary_logistic_baseline_only(df)
    structural_controls_test(df)
    pullback_vs_typology(df)
    time_aligned_behavior_vs_performance(df)
    cox_time_to_cessation(df)
    prospective_early_warning(df)
    hhi_direction_check(df)
    logger.info("\n=== ALL REVIEWER-RESPONSE ANALYSES DONE ===")


if __name__ == "__main__":
    main()
