"""
Steg 11: Landmark-analyse + outcome-sensitivitet + calibration.

Addresserer reviewer-kritikken:
1. Landmark ved alder 16 — eliminerer tautologi
2. Outcome-sensitivitet (≥1 vs ≥2 vs 2+ år)
3. Lagged volume (alder 13-14 predikerer alene)
4. Volume change-score
5. Confusion matrix + PPV/NPV
6. Calibration plot
"""

import logging
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from lifelines import CoxPHFitter, KaplanMeierFitter
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix, roc_auc_score, precision_score, recall_score,
    f1_score
)
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
ANALYSE_FILE = DATA_DIR / "analysedata_utvidet.csv"
KARRIERE_FILE = DATA_DIR / "karrieredata_utvidet.csv"
OUT_DIR = DATA_DIR.parent / "submission_pse"
TAB_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"

mpl.rcParams["figure.dpi"] = 150
mpl.rcParams["savefig.dpi"] = 150
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["font.size"] = 9


def load_data():
    df = pd.read_csv(ANALYSE_FILE)
    df["event"] = (df["aktiv_naa"] == 0).astype(int)
    df["baseline_age"] = df["stevne_aar"] - df["birth_year"]
    df["duration_age"] = (df["alder_ved_slutt"] - df["baseline_age"]).clip(lower=0.5)
    df["female"] = (df["gender"] == "F").astype(int)
    for c in ["tyrving_best", "vol_milepael", "hhi_early", "vol_pre_milepael"]:
        df[f"{c}_z"] = (df[c] - df[c].mean()) / df[c].std()
    return df


# =============================================================================
# 1. LANDMARK ANALYSIS at age 16
# =============================================================================

def landmark_age_16(df):
    """
    Among athletes STILL ACTIVE at age 16 (vol_age_16 >= 1 meet OR
    documented activity in their age-16 calendar year), does volume
    at age 15-16 predict senior retention?

    This addresses the tautology concern: predictor (volume) is no longer
    mechanically zero for those who already dropped out before age 16.
    """
    logger.info("\n=== 1. LANDMARK ANALYSIS AT AGE 16 ===")

    # Athletes still active at age 16: have at least 1 result at age 16
    karriere = pd.read_csv(KARRIERE_FILE, low_memory=False)
    karriere["date"] = pd.to_datetime(karriere["date"], errors="coerce")
    karriere["year"] = karriere["date"].dt.year
    # Merge birth_year from df
    karriere = karriere.merge(df[["athlete_id", "birth_year"]], on="athlete_id", how="inner")
    karriere["age"] = karriere["year"] - karriere["birth_year"]

    # Athletes with >=1 result at age 16
    age16_active = set(karriere[karriere["age"] == 16]["athlete_id"].unique())
    logger.info(f"  Of {len(df)} total athletes, {len(age16_active)} still active at age 16")

    landmark_df = df[df["athlete_id"].isin(age16_active)].copy()
    landmark_df["lm_event"] = (landmark_df["aktiv_naa"] == 0).astype(int)

    # Duration from landmark (age 16) to last active year
    landmark_df["lm_duration"] = (landmark_df["alder_ved_slutt"] - 16).clip(lower=0.5)

    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    cox_df = landmark_df[["lm_duration", "lm_event"] + covars].dropna()

    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col="lm_duration", event_col="lm_event")

    rows = []
    for cov in covars:
        rows.append({
            "Covariate": cov,
            "HR": round(np.exp(cph.params_[cov]), 3),
            "CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
            "CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
            "p": round(cph.summary.loc[cov, "p"], 4),
        })
    tab = pd.DataFrame(rows)
    tab["n"] = len(cox_df)
    tab["C-index"] = round(cph.concordance_index_, 3)
    tab.to_csv(TAB_DIR / "tableS8_landmark_age16.csv", index=False)

    logger.info(f"  Cox among age-16-active (n={len(cox_df)}, C={cph.concordance_index_:.3f}):")
    for _, row in tab.iterrows():
        logger.info(f"    {row['Covariate']}: HR={row['HR']} [{row['CI low']}, {row['CI high']}], p={row['p']}")

    return tab


# =============================================================================
# 2. OUTCOME SENSITIVITY (3 definitions)
# =============================================================================

def outcome_sensitivity(df):
    """
    Compare HR for volume across 3 outcome definitions:
    A. ≥1 result at age 20+ (most lenient)
    B. ≥2 results in any year at age 20+ (current primary)
    C. ≥2 results in two different senior years (most strict)
    """
    logger.info("\n=== 2. OUTCOME-DEFINITION SENSITIVITY ===")
    karriere = pd.read_csv(KARRIERE_FILE, low_memory=False)
    karriere["date"] = pd.to_datetime(karriere["date"], errors="coerce")
    karriere["year"] = karriere["date"].dt.year
    karriere = karriere.merge(df[["athlete_id", "birth_year"]], on="athlete_id", how="inner")
    karriere["age"] = karriere["year"] - karriere["birth_year"]

    # Compute alternative outcomes
    senior = karriere[karriere["age"] >= 20].copy()
    senior_counts = senior.groupby(["athlete_id", "year"]).size().reset_index(name="n_results")

    # A: ≥1 result senior
    a_athletes = set(senior["athlete_id"].unique())
    df["outcome_A"] = df["athlete_id"].isin(a_athletes).astype(int)

    # B: ≥2 results in any single senior year (= current primary)
    b_athletes = set(senior_counts[senior_counts["n_results"] >= 2]["athlete_id"].unique())
    df["outcome_B"] = df["athlete_id"].isin(b_athletes).astype(int)

    # C: ≥2 results in two different senior years
    c_athletes = set(
        senior_counts[senior_counts["n_results"] >= 2]
        .groupby("athlete_id").size()[lambda x: x >= 2].index
    )
    df["outcome_C"] = df["athlete_id"].isin(c_athletes).astype(int)

    logger.info(f"  Outcome A (>=1 result, age 20+): {df['outcome_A'].sum()} ({df['outcome_A'].mean()*100:.1f}%)")
    logger.info(f"  Outcome B (>=2 results in any year): {df['outcome_B'].sum()} ({df['outcome_B'].mean()*100:.1f}%)")
    logger.info(f"  Outcome C (>=2 results in 2 yrs): {df['outcome_C'].sum()} ({df['outcome_C'].mean()*100:.1f}%)")

    # Logistic regression for each, predictor: vol_milepael_z
    rows = []
    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    for outcome in ["A", "B", "C"]:
        sub = df[covars + [f"outcome_{outcome}"]].dropna()
        X = sub[covars]
        y = sub[f"outcome_{outcome}"]
        lr = LogisticRegression(max_iter=2000)
        lr.fit(X, y)
        auc = lr.predict_proba(X)[:, 1]
        from sklearn.metrics import roc_auc_score
        auc_score = roc_auc_score(y, auc)

        # Odds ratio for vol_milepael_z (last covariate)
        for i, c in enumerate(covars):
            if c == "vol_milepael_z":
                or_val = np.exp(lr.coef_[0][i])
                break

        rows.append({
            "Outcome": outcome,
            "Description": {
                "A": "≥1 senior result (age 20+)",
                "B": "≥2 results in any senior year (primary)",
                "C": "≥2 results in 2 different senior years",
            }[outcome],
            "Retainer n": int(y.sum()),
            "Retainer %": round(y.mean() * 100, 1),
            "OR (vol_milepael_z)": round(or_val, 3),
            "AUC (full model)": round(auc_score, 3),
        })

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS9_outcome_sensitivity.csv", index=False)
    for _, row in tab.iterrows():
        logger.info(f"  Outcome {row['Outcome']}: OR={row['OR (vol_milepael_z)']}, AUC={row['AUC (full model)']}")
    return tab


# =============================================================================
# 3. LAGGED VOLUME — pre-milestone (ages 13-14) ALONE
# =============================================================================

def lagged_volume_test(df):
    """
    Can volume at ages 13-14 ALONE (before the milestone window) predict
    senior retention? This tests whether the behavioral signal is detectable
    even before the qualification milestone is reached — strengthens the
    "early warning" claim.
    """
    logger.info("\n=== 3. LAGGED VOLUME (ages 13-14 only) ===")

    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"]
    cox_df = df[["duration_age", "event"] + covars].dropna()
    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col="duration_age", event_col="event")

    rows = []
    for cov in covars:
        rows.append({
            "Covariate": cov,
            "HR": round(np.exp(cph.params_[cov]), 3),
            "CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
            "CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
            "p": round(cph.summary.loc[cov, "p"], 4),
        })
    tab = pd.DataFrame(rows)
    tab["n"] = len(cox_df)
    tab["C-index"] = round(cph.concordance_index_, 3)
    tab.to_csv(TAB_DIR / "tableS10_lagged_volume.csv", index=False)
    logger.info(f"  Cox with pre-milestone volume (ages 13-14) only (n={len(cox_df)}, C={cph.concordance_index_:.3f}):")
    for _, row in tab.iterrows():
        logger.info(f"    {row['Covariate']}: HR={row['HR']} [{row['CI low']}, {row['CI high']}]")
    return tab


# =============================================================================
# 4. CONFUSION MATRIX + PPV/NPV
# =============================================================================

def calibration_metrics(df):
    """
    For practical early-warning claim, compute calibration metrics:
    PPV (positive predictive value), NPV, sensitivity, specificity
    at multiple volume thresholds.

    Operationally: 'flag an athlete' = their vol_milepael is in bottom quintile.
    """
    logger.info("\n=== 4. CALIBRATION FOR EARLY-WARNING (volume thresholds) ===")

    df = df.dropna(subset=["vol_milepael", "aktiv_senior"]).copy()
    df["dropout"] = 1 - df["aktiv_senior"]
    n_total = len(df)

    # Define thresholds (athletes flagged if vol < threshold)
    thresholds = [1, 5, 10, 15, 20]

    rows = []
    for t in thresholds:
        flagged = df["vol_milepael"] < t  # 1 = high-risk flag
        tp = ((flagged == 1) & (df["dropout"] == 1)).sum()
        fp = ((flagged == 1) & (df["dropout"] == 0)).sum()
        fn = ((flagged == 0) & (df["dropout"] == 1)).sum()
        tn = ((flagged == 0) & (df["dropout"] == 0)).sum()

        ppv = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
        npv = tn / (tn + fn) if (tn + fn) > 0 else float("nan")
        sens = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        spec = tn / (tn + fp) if (tn + fp) > 0 else float("nan")

        rows.append({
            "Threshold (meets < )": t,
            "Flagged %": round(flagged.mean() * 100, 1),
            "Sensitivity": round(sens, 3),
            "Specificity": round(spec, 3),
            "PPV": round(ppv, 3),
            "NPV": round(npv, 3),
            "TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn),
        })

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS11_calibration.csv", index=False)
    for _, row in tab.iterrows():
        logger.info(f"  vol<{row['Threshold (meets < )']}: PPV={row['PPV']}, NPV={row['NPV']}, "
                    f"sens={row['Sensitivity']}, spec={row['Specificity']} ({row['Flagged %']}% flagged)")
    return tab


# =============================================================================
# 5. CALIBRATION PLOT
# =============================================================================

def calibration_plot(df):
    """Plot dropout rate vs predicted retention probability across deciles."""
    logger.info("\n=== 5. CALIBRATION PLOT ===")

    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    sub = df[covars + ["aktiv_senior"]].dropna()

    # Fit on full data (illustration, not formal CV)
    lr = LogisticRegression(max_iter=2000)
    lr.fit(sub[covars], sub["aktiv_senior"])
    sub["pred_retain"] = lr.predict_proba(sub[covars])[:, 1]

    # Bin into deciles by predicted probability
    sub["decile"] = pd.qcut(sub["pred_retain"], q=10, labels=False, duplicates="drop")
    grouped = sub.groupby("decile").agg(
        n=("aktiv_senior", "size"),
        observed=("aktiv_senior", "mean"),
        predicted=("pred_retain", "mean"),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(5, 4.5))
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect calibration")
    ax.plot(grouped["predicted"], grouped["observed"], "o-",
            color="#2E7D32", linewidth=2, markersize=8,
            label=f"Full model (n={len(sub)})")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Predicted probability of senior retention")
    ax.set_ylabel("Observed proportion retained as seniors")
    ax.set_title("Calibration of full Cox model (apparent fit)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "figS1_calibration.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"  Calibration plot saved")
    return grouped


# =============================================================================
# 6. SUBSET ANALYSIS: zero volume excluded
# =============================================================================

def exclude_zero_vol(df):
    """
    Refit the main Cox model excluding athletes with vol_milepael=0.
    Tests whether the effect holds among athletes who participated at all
    during the milestone window.
    """
    logger.info("\n=== 6. EXCLUDE ZERO-VOLUME ATHLETES ===")
    sub = df[df["vol_milepael"] > 0].copy()
    logger.info(f"  Excluding {(df['vol_milepael']==0).sum()} athletes with vol_milepael=0; remaining n={len(sub)}")

    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    cox_df = sub[["duration_age", "event"] + covars].dropna()

    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col="duration_age", event_col="event")

    rows = []
    for cov in covars:
        rows.append({
            "Covariate": cov,
            "HR": round(np.exp(cph.params_[cov]), 3),
            "CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
            "CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
            "p": round(cph.summary.loc[cov, "p"], 4),
        })
    tab = pd.DataFrame(rows)
    tab["n"] = len(cox_df)
    tab["C-index"] = round(cph.concordance_index_, 3)
    tab.to_csv(TAB_DIR / "tableS12_exclude_zero_vol.csv", index=False)
    logger.info(f"  Cox excluding zero-volume (n={len(cox_df)}, C={cph.concordance_index_:.3f}):")
    for _, row in tab.iterrows():
        logger.info(f"    {row['Covariate']}: HR={row['HR']} [{row['CI low']}, {row['CI high']}]")
    return tab


def main():
    df = load_data()
    logger.info(f"Lastet {len(df)} utøvere\n")

    landmark_age_16(df)
    outcome_sensitivity(df)
    lagged_volume_test(df)
    calibration_metrics(df)
    calibration_plot(df)
    exclude_zero_vol(df)

    logger.info("\n=== ALLE LANDMARK+CALIBRATION ANALYSER FERDIG ===")
    logger.info(f"Output: {TAB_DIR}")


if __name__ == "__main__":
    main()
