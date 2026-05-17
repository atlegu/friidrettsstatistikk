"""
Steg 8: Hovedanalyser for PSE-paper.

Kjører:
1. Kaplan-Meier (samlet, kjønn, volum-kvintil, mesterskap-typer)
2. Cox proportional hazards med stepwise modellbygging
3. Random Forest med variable importance (pre-baseline + behavioral)
4. Logistisk regresjon for aktiv_senior med AUC
5. Volum-trajectory plot (retention vs dropout)

Skriver output til submission_pse/figures/ og submission_pse/tables/
Alle figurer med dpi=150, tight_layout for å holde filstørrelse lav.
"""

import logging
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
ANALYSE_FILE = DATA_DIR / "analysedata_utvidet.csv"
OUT_DIR = DATA_DIR.parent / "submission_pse"
FIG_DIR = OUT_DIR / "figures"
TAB_DIR = OUT_DIR / "tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

# Matplotlib defaults — keep figures small
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams["savefig.dpi"] = 150
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["font.size"] = 9
mpl.rcParams["axes.titlesize"] = 10
mpl.rcParams["axes.labelsize"] = 9


# =============================================================================
# Helpers
# =============================================================================

def load_data():
    df = pd.read_csv(ANALYSE_FILE)
    logger.info(f"Lastet analysedata: {len(df)} utøvere, {len(df.columns)} kolonner")

    # Lag survival-variabler
    # event = 1 hvis sluttet (siste_aktive_ar < 2024), 0 hvis aktiv (censored)
    df["event"] = (df["aktiv_naa"] == 0).astype(int)
    df["duration"] = df["karriere_ar"].clip(lower=0.5)

    # COVID-eksklusjon: utøvere som sluttet i 2020-2021 ekskluderes for robusthet
    df["covid_dropout"] = df["siste_aktive_ar"].isin([2020, 2021]).astype(int)

    # Kohort-indikator
    df["kohort"] = df["birth_year"].apply(
        lambda y: "1998-2000" if y <= 2000 else "2001-2002"
    )

    return df


def lagre_tabell(df, fn):
    df.to_csv(TAB_DIR / fn, index=False, encoding="utf-8")
    logger.info(f"  -> {TAB_DIR / fn}")


def lagre_figur(fig, fn):
    fig.savefig(FIG_DIR / fn, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"  -> {FIG_DIR / fn}")


# =============================================================================
# 1. DESCRIPTIVES
# =============================================================================

def deskriptiv(df):
    logger.info("\n=== 1. DESKRIPTIV STATISTIKK ===")

    rows = []
    for cohort in ["1998-2000", "2001-2002", "All"]:
        if cohort == "All":
            sub = df
        else:
            sub = df[df["kohort"] == cohort]
        rows.append({
            "Cohort": cohort,
            "N": len(sub),
            "M": (sub["gender"] == "M").sum(),
            "F": (sub["gender"] == "F").sum(),
            "Median career (years)": sub["karriere_ar"].median(),
            "Active age 17 (%)": round(sub["aktiv_17"].mean() * 100, 1),
            "Active age 20 (%)": round(sub["aktiv_20"].mean() * 100, 1),
            "Still active 2024+ (%)": round(sub["aktiv_naa"].mean() * 100, 1),
            "Mean Tyrving best": round(sub["tyrving_best"].mean(), 0),
            "Median competitions age 15-16": sub["vol_milepael"].median(),
        })
    tab = pd.DataFrame(rows)
    lagre_tabell(tab, "table1_descriptives.csv")
    return tab


# =============================================================================
# 2. KAPLAN-MEIER
# =============================================================================

def kaplan_meier_plots(df):
    logger.info("\n=== 2. KAPLAN-MEIER ===")

    # Use age as time axis: time from baseline (age 13/14) to dropout
    # duration_age = alder_ved_slutt - baseline_age
    df_km = df.copy()
    # Baseline age = stevne_aar - birth_year (typically 13 or 14)
    df_km["baseline_age"] = df_km["stevne_aar"] - df_km["birth_year"]
    df_km["duration_age"] = (df_km["alder_ved_slutt"] - df_km["baseline_age"]).clip(lower=0.5)

    # Plot 1: Overall + by sex
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    kmf = KaplanMeierFitter()

    kmf.fit(df_km["duration_age"], df_km["event"], label="All athletes")
    kmf.plot_survival_function(ax=axes[0], ci_show=True)
    axes[0].set_title("A. Overall retention")
    axes[0].set_xlabel("Years since baseline (age 13/14)")
    axes[0].set_ylabel("Proportion still active")
    axes[0].set_ylim(0, 1)
    axes[0].set_xlim(0, 14)
    axes[0].grid(alpha=0.3)

    for sex, label, ls in [("M", "Male", "-"), ("F", "Female", "--")]:
        sub = df_km[df_km["gender"] == sex]
        kmf.fit(sub["duration_age"], sub["event"], label=label)
        kmf.plot_survival_function(ax=axes[1], ci_show=False, linestyle=ls)
    axes[1].set_title("B. By sex")
    axes[1].set_xlabel("Years since baseline")
    axes[1].set_ylabel("Proportion still active")
    axes[1].set_ylim(0, 1)
    axes[1].set_xlim(0, 14)
    axes[1].grid(alpha=0.3)
    axes[1].legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    lagre_figur(fig, "fig2_km_overall_sex.png")

    # Logrank for sex
    m = df_km[df_km["gender"] == "M"]
    f = df_km[df_km["gender"] == "F"]
    lr = logrank_test(m["duration_age"], f["duration_age"], m["event"], f["event"])
    logger.info(f"  Log-rank sex: chi2={lr.test_statistic:.2f}, p={lr.p_value:.4f}")

    # Plot 2: KM by competition volume quintile (age 15-16)
    df_km["vol_q"] = pd.qcut(df_km["vol_milepael"], q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"],
                              duplicates="drop")

    fig, ax = plt.subplots(figsize=(6, 4.5))
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, 5))
    for i, q in enumerate(["Q1", "Q2", "Q3", "Q4", "Q5"]):
        sub = df_km[df_km["vol_q"] == q]
        if len(sub) < 5:
            continue
        kmf.fit(sub["duration_age"], sub["event"],
                label=f"{q} (n={len(sub)}, vol={int(sub['vol_milepael'].median())} meets)")
        kmf.plot_survival_function(ax=ax, ci_show=False, color=colors[i])
    ax.set_title("Retention by competition volume at age 15–16 (quintiles)")
    ax.set_xlabel("Years since baseline (age 13/14)")
    ax.set_ylabel("Proportion still active")
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 14)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=7)
    plt.tight_layout()
    lagre_figur(fig, "fig3_km_vol_quintile.png")

    # Plot 3: KM by mesterskap-typer
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for n_typer, color in zip([0, 1, 2, 3, 4], plt.cm.plasma(np.linspace(0.1, 0.9, 5))):
        sub = df_km[df_km["n_msk_typer"] == n_typer]
        if len(sub) < 10:
            continue
        kmf.fit(sub["duration_age"], sub["event"],
                label=f"{n_typer} types (n={len(sub)})")
        kmf.plot_survival_function(ax=ax, ci_show=False, color=color)
    ax.set_title("Retention by number of championship types (pre-age 17)")
    ax.set_xlabel("Years since baseline (age 13/14)")
    ax.set_ylabel("Proportion still active")
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 14)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=7)
    plt.tight_layout()
    lagre_figur(fig, "fig4_km_msk_typer.png")

    return df_km


# =============================================================================
# 3. VOLUM-TRAJECTORY (CORE FIGURE)
# =============================================================================

def volum_trajectory(df):
    logger.info("\n=== 3. VOLUM-TRAJECTORY ===")

    # For utøvere som vi vet hvordan det gikk (alle våre — vi har 14 år oppfølging)
    df_traj = df.copy()
    df_traj["retainer"] = df_traj["aktiv_senior"]

    # Median volum per aldersår, stratifisert etter retention status
    ages = [13, 14, 15, 16, 17, 18]
    vol_cols = [f"vol_age_{a}" for a in ages]

    fig, ax = plt.subplots(figsize=(7, 4.5))

    for retainer, color, label, marker in [(1, "#2E7D32", "Senior retainers (age 20+)", "o"),
                                             (0, "#C62828", "Dropouts before age 20", "s")]:
        sub = df_traj[df_traj["retainer"] == retainer]
        n = len(sub)
        medians = [sub[c].median() for c in vol_cols]
        q25 = [sub[c].quantile(0.25) for c in vol_cols]
        q75 = [sub[c].quantile(0.75) for c in vol_cols]
        ax.plot(ages, medians, marker=marker, color=color, linewidth=2,
                markersize=7, label=f"{label} (n={n})")
        ax.fill_between(ages, q25, q75, color=color, alpha=0.15)

    ax.axvline(15, color="gray", linestyle="--", alpha=0.5)
    ax.annotate("First qualification\nmilestone (UM)", xy=(15, ax.get_ylim()[1] * 0.92),
                xytext=(15.3, ax.get_ylim()[1] * 0.85),
                fontsize=8, color="gray",
                arrowprops=dict(arrowstyle="->", color="gray", alpha=0.5))
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Competitions per year (median + IQR)")
    ax.set_title("Competition volume trajectory: retainers vs. dropouts")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    lagre_figur(fig, "fig1_volume_trajectory.png")

    # Tabular form
    tab_rows = []
    for retainer, label in [(1, "Senior retainers"), (0, "Dropouts")]:
        sub = df_traj[df_traj["retainer"] == retainer]
        row = {"Group": label, "N": len(sub)}
        for a, c in zip(ages, vol_cols):
            row[f"Age {a} median"] = sub[c].median()
            row[f"Age {a} IQR"] = f"{sub[c].quantile(0.25):.0f}-{sub[c].quantile(0.75):.0f}"
        tab_rows.append(row)
    tab = pd.DataFrame(tab_rows)
    lagre_tabell(tab, "table2_volume_trajectory.csv")
    return tab


# =============================================================================
# 4. COX MODELS
# =============================================================================

def cox_modeller(df):
    logger.info("\n=== 4. COX PROPORTIONAL HAZARDS ===")

    # Bygg cox-data
    cox_df = df.copy()

    # Baseline age
    cox_df["baseline_age"] = cox_df["stevne_aar"] - cox_df["birth_year"]
    cox_df["duration_age"] = (cox_df["alder_ved_slutt"] - cox_df["baseline_age"]).clip(lower=0.5)

    # Encode
    cox_df["female"] = (cox_df["gender"] == "F").astype(int)
    cox_df["tyrving_z"] = (cox_df["tyrving_best"] - cox_df["tyrving_best"].mean()) / cox_df["tyrving_best"].std()
    cox_df["vol_milepael_z"] = (cox_df["vol_milepael"] - cox_df["vol_milepael"].mean()) / cox_df["vol_milepael"].std()
    cox_df["hhi_early_z"] = (cox_df["hhi_early"] - cox_df["hhi_early"].mean()) / cox_df["hhi_early"].std()

    # Stepwise modeller
    models = {
        "M1: Sex only": ["female"],
        "M2: + Performance": ["female", "tyrving_z"],
        "M3: + Specialization": ["female", "tyrving_z", "hhi_early_z"],
        "M4: + Volume at milestone": ["female", "tyrving_z", "hhi_early_z", "vol_milepael_z"],
        "M5: + Championship types": ["female", "tyrving_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"],
    }

    results_rows = []
    for name, covars in models.items():
        sub = cox_df[["duration_age", "event"] + covars].dropna()
        cph = CoxPHFitter()
        try:
            cph.fit(sub, duration_col="duration_age", event_col="event")
            c_idx = cph.concordance_index_
            for cov in covars:
                hr = np.exp(cph.params_[cov])
                ci_lo = np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"])
                ci_hi = np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"])
                p = cph.summary.loc[cov, "p"]
                results_rows.append({
                    "Model": name,
                    "Covariate": cov,
                    "HR": round(hr, 3),
                    "CI low": round(ci_lo, 3),
                    "CI high": round(ci_hi, 3),
                    "p": round(p, 4),
                    "C-index": round(c_idx, 3),
                    "n": len(sub),
                })
            logger.info(f"  {name}: C-index={c_idx:.3f}, n={len(sub)}")
        except Exception as e:
            logger.warning(f"  {name} failed: {e}")

    tab = pd.DataFrame(results_rows)
    lagre_tabell(tab, "table3_cox_stepwise.csv")
    return tab


# =============================================================================
# 5. RANDOM FOREST + AUC
# =============================================================================

def random_forest(df):
    logger.info("\n=== 5. RANDOM FOREST VARIABLE IMPORTANCE ===")

    # Pre-baseline + behavioral prediktorer for aktiv_senior
    candidate_features = [
        "female", "birth_year", "tyrving_best", "baseline_n_kategorier",
        "stevner_baseline_ar", "stevner_per_ar_tidlig",
        "hhi_early", "early_n_kategorier",
        "vol_age_13", "vol_age_14", "vol_age_15", "vol_age_16",
        "vol_milepael", "vol_pre_milepael", "vol_trend_milepael",
        "hhi_age_15", "hhi_change",
        "n_msk_typer", "um_15_16", "helaars_sum_13_16",
        "tyrving_peak_pre15", "tyrving_slope_13_16",
    ]

    rf_df = df.copy()
    rf_df["female"] = (rf_df["gender"] == "F").astype(int)
    rf_df = rf_df[candidate_features + ["aktiv_senior"]].dropna()
    logger.info(f"  RF data: n={len(rf_df)}, features={len(candidate_features)}")

    X = rf_df[candidate_features]
    y = rf_df["aktiv_senior"]

    rf = RandomForestClassifier(n_estimators=500, max_depth=8,
                                  random_state=42, class_weight="balanced",
                                  n_jobs=-1)
    rf.fit(X, y)

    # Feature importance
    imp = pd.DataFrame({
        "Feature": candidate_features,
        "Importance": rf.feature_importances_,
    }).sort_values("Importance", ascending=False)
    imp["Importance"] = imp["Importance"].round(4)
    lagre_tabell(imp, "table4_rf_importance.csv")

    # Cross-validated AUC
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = cross_val_score(rf, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
    logger.info(f"  Full model AUC: {aucs.mean():.3f} ± {aucs.std():.3f}")

    # AUC for restricted subsets
    subsets = {
        "Baseline only (performance + sex)": ["female", "tyrving_best"],
        "Specialization only": ["female", "hhi_early", "early_n_kategorier"],
        "Volume only": ["female", "vol_age_13", "vol_age_14", "vol_age_15", "vol_age_16"],
        "Volume + Specialization (pre-baseline behavioral)": [
            "female", "vol_age_13", "vol_age_14", "vol_age_15", "vol_age_16",
            "hhi_age_15", "hhi_change", "helaars_sum_13_16"
        ],
        "Full (all candidates)": candidate_features,
    }

    auc_rows = []
    for name, feats in subsets.items():
        sub = rf_df[feats + ["aktiv_senior"]].dropna()
        X_sub = sub[feats]
        y_sub = sub["aktiv_senior"]
        lr = LogisticRegression(max_iter=2000, class_weight="balanced")
        rf_sub = RandomForestClassifier(n_estimators=300, max_depth=6,
                                          random_state=42, class_weight="balanced",
                                          n_jobs=-1)
        lr_auc = cross_val_score(lr, X_sub, y_sub, cv=cv, scoring="roc_auc", n_jobs=-1)
        rf_auc = cross_val_score(rf_sub, X_sub, y_sub, cv=cv, scoring="roc_auc", n_jobs=-1)
        auc_rows.append({
            "Model": name,
            "n features": len(feats),
            "n": len(sub),
            "AUC (logistic)": round(lr_auc.mean(), 3),
            "AUC SD (logistic)": round(lr_auc.std(), 3),
            "AUC (RF)": round(rf_auc.mean(), 3),
            "AUC SD (RF)": round(rf_auc.std(), 3),
        })

    auc_tab = pd.DataFrame(auc_rows)
    lagre_tabell(auc_tab, "table5_auc_comparison.csv")

    # Plot RF importance (top 15)
    top = imp.head(15)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.barh(top["Feature"][::-1], top["Importance"][::-1], color="#4A90E2")
    ax.set_xlabel("Feature importance (random forest)")
    ax.set_title("Predictors of senior retention (age ≥20)")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    lagre_figur(fig, "fig5_rf_importance.png")

    return imp, auc_tab


# =============================================================================
# 6. REPLIKASJON PÅ TVERS AV KOHORTER
# =============================================================================

def replikasjon_kohorter(df):
    logger.info("\n=== 6. CROSS-COHORT REPLICATION ===")

    cox_df = df.copy()
    cox_df["baseline_age"] = cox_df["stevne_aar"] - cox_df["birth_year"]
    cox_df["duration_age"] = (cox_df["alder_ved_slutt"] - cox_df["baseline_age"]).clip(lower=0.5)
    cox_df["female"] = (cox_df["gender"] == "F").astype(int)
    cox_df["tyrving_z"] = (cox_df["tyrving_best"] - cox_df["tyrving_best"].mean()) / cox_df["tyrving_best"].std()
    cox_df["vol_milepael_z"] = (cox_df["vol_milepael"] - cox_df["vol_milepael"].mean()) / cox_df["vol_milepael"].std()
    cox_df["hhi_early_z"] = (cox_df["hhi_early"] - cox_df["hhi_early"].mean()) / cox_df["hhi_early"].std()

    rows = []
    for cohort in ["1998-2000", "2001-2002"]:
        sub = cox_df[cox_df["kohort"] == cohort]
        covars = ["female", "tyrving_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
        cox_sub = sub[["duration_age", "event"] + covars].dropna()
        cph = CoxPHFitter()
        try:
            cph.fit(cox_sub, duration_col="duration_age", event_col="event")
            for cov in covars:
                rows.append({
                    "Cohort": cohort,
                    "n": len(cox_sub),
                    "Covariate": cov,
                    "HR": round(np.exp(cph.params_[cov]), 3),
                    "CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
                    "CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
                    "p": round(cph.summary.loc[cov, "p"], 4),
                    "C-index": round(cph.concordance_index_, 3),
                })
            logger.info(f"  {cohort}: n={len(cox_sub)}, C={cph.concordance_index_:.3f}")
        except Exception as e:
            logger.warning(f"  {cohort} failed: {e}")

    tab = pd.DataFrame(rows)
    lagre_tabell(tab, "table6_cohort_replication.csv")
    return tab


# =============================================================================
# MAIN
# =============================================================================

def main():
    df = load_data()

    tab1 = deskriptiv(df)
    df_km = kaplan_meier_plots(df)
    tab2 = volum_trajectory(df)
    cox_tab = cox_modeller(df)
    rf_imp, auc_tab = random_forest(df)
    rep_tab = replikasjon_kohorter(df)

    logger.info("\n=== ALLE ANALYSER FERDIG ===")
    logger.info(f"Output: {OUT_DIR}")
    logger.info(f"  Figurer: {FIG_DIR}")
    logger.info(f"  Tabeller: {TAB_DIR}")


if __name__ == "__main__":
    main()
