"""
Sensitivity analysis: does the HHI (specialization) effect on retention
survive after controlling for performance IN THE MAIN EVENT CATEGORY?

User concern: Higher HHI = fewer event categories.  Athletes who
specialize might just be BETTER in their main event, and that's
what drives retention. We control for Tyrving_best (max across all
events) but not for "Tyrving in the primary category specifically."

This script:
1. For each athlete, identifies their primary category (already in
   primaer_kategori_baseline)
2. Computes their best Tyrving score IN THAT CATEGORY during the
   baseline window (ages 13-14)
3. Adds this as a covariate to the primary L4 model alongside HHI
4. Reports whether the HHI effect changes
"""

import logging
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import statsmodels.api as sm

from tyrvingtabellen import parse_tyrving_xls, beregn_tyrving_poeng

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent


def load_data():
    df = pd.read_csv(DATA_DIR / "analysedata_utvidet.csv")
    karriere = pd.read_csv(DATA_DIR / "karrieredata_utvidet.csv", low_memory=False)
    karriere["date"] = pd.to_datetime(karriere["date"], errors="coerce")
    karriere["year"] = karriere["date"].dt.year
    karriere = karriere.merge(df[["athlete_id", "birth_year", "gender"]],
                                on="athlete_id", how="inner")
    karriere["age"] = karriere["year"] - karriere["birth_year"]
    return df, karriere


def compute_tyrving_in_main_category(df, karriere, tyrving_table):
    """For each athlete, compute the best Tyrving score in their
    primary baseline category during ages 13-14."""
    logger.info("Computing best Tyrving in primary category at baseline...")

    # Filter to baseline window (ages 13-14)
    baseline = karriere[karriere["age"].isin([13, 14])].copy()

    # Filter out clearly bad performance values
    from pathlib import Path
    min_cs = {
        "60m": 600, "80m": 800, "100m": 1000, "200m": 2000,
        "300m": 3500, "400m": 4500, "600m": 8000, "800m": 11000,
        "1000m": 15000, "1500m": 23000, "2000m": 32000, "3000m": 50000,
        "60mh": 700, "80mh": 1000, "200mh": 2500, "300mh": 4000,
    }
    for ec, m in min_cs.items():
        mask = (baseline["event_code"] == ec) & (baseline["performance_value"] < m)
        baseline = baseline[~mask]

    # Compute Tyrving for each result
    def calc(row):
        if pd.isna(row["performance_value"]) or pd.isna(row["gender"]) or pd.isna(row["age"]):
            return None
        pts = beregn_tyrving_poeng(
            int(row["performance_value"]), row["event_code"],
            row["result_type"], row["gender"], int(row["age"]), tyrving_table
        )
        if pts is not None:
            pts = max(0, min(pts, 1500))
        return pts

    baseline["tyrving"] = baseline.apply(calc, axis=1)

    # Best Tyrving by athlete × category
    by_cat = baseline.groupby(["athlete_id", "event_category"])["tyrving"].max().reset_index()
    by_cat.rename(columns={"tyrving": "tyrving_in_cat"}, inplace=True)

    # Merge with primary category
    df_sub = df[["athlete_id", "primaer_kategori_baseline"]].rename(
        columns={"primaer_kategori_baseline": "event_category"}
    )
    out = df_sub.merge(by_cat, on=["athlete_id", "event_category"], how="left")
    out.rename(columns={"tyrving_in_cat": "tyrving_main"}, inplace=True)

    n_nonna = out["tyrving_main"].notna().sum()
    logger.info(f"  {n_nonna} of {len(out)} athletes have Tyrving in their primary category")
    return out[["athlete_id", "tyrving_main"]]


def main():
    df, karriere = load_data()
    tyrving_table = parse_tyrving_xls()

    main_cat_perf = compute_tyrving_in_main_category(df, karriere, tyrving_table)
    df = df.merge(main_cat_perf, on="athlete_id", how="left")

    # Set up covariates
    df["female"] = (df["gender"] == "F").astype(int)
    for c in ["tyrving_best", "vol_pre_milepael", "hhi_early", "tyrving_main"]:
        if c in df.columns:
            v = df[c]
            if v.std() > 0:
                df[f"{c}_z"] = (v - v.mean()) / v.std()

    # Correlation check
    logger.info("\n=== Correlations between performance variables ===")
    sub = df[["tyrving_best_z", "tyrving_main_z", "hhi_early_z"]].dropna()
    logger.info(sub.corr().round(3).to_string())

    # Model 1: PRIMARY model (no tyrving_main) — reference
    logger.info("\n=== Model A: Primary L4 (without tyrving_main) ===")
    covars_a = ["female", "tyrving_best_z", "hhi_early_z", "vol_pre_milepael_z"]
    da = df[covars_a + ["aktiv_senior"]].dropna()
    Xa = sm.add_constant(da[covars_a])
    ma = sm.Logit(da["aktiv_senior"], Xa).fit(disp=0)
    for c in covars_a:
        or_v = np.exp(ma.params[c])
        ci = np.exp(ma.conf_int().loc[c].values)
        logger.info(f"  {c}: OR={or_v:.3f} [{ci[0]:.3f}, {ci[1]:.3f}], p={ma.pvalues[c]:.4f}")
    logger.info(f"  n={len(da)}, pseudo-R²={ma.prsquared:.4f}")

    # Model 2: + tyrving_main (Tyrving in primary category)
    logger.info("\n=== Model B: + Tyrving in primary category ===")
    covars_b = covars_a + ["tyrving_main_z"]
    db = df[covars_b + ["aktiv_senior"]].dropna()
    Xb = sm.add_constant(db[covars_b])
    mb = sm.Logit(db["aktiv_senior"], Xb).fit(disp=0)
    for c in covars_b:
        or_v = np.exp(mb.params[c])
        ci = np.exp(mb.conf_int().loc[c].values)
        logger.info(f"  {c}: OR={or_v:.3f} [{ci[0]:.3f}, {ci[1]:.3f}], p={mb.pvalues[c]:.4f}")
    logger.info(f"  n={len(db)}, pseudo-R²={mb.prsquared:.4f}")

    # Model 3: REPLACE tyrving_best with tyrving_main
    logger.info("\n=== Model C: tyrving_main REPLACES tyrving_best ===")
    covars_c = ["female", "tyrving_main_z", "hhi_early_z", "vol_pre_milepael_z"]
    dc = df[covars_c + ["aktiv_senior"]].dropna()
    Xc = sm.add_constant(dc[covars_c])
    mc = sm.Logit(dc["aktiv_senior"], Xc).fit(disp=0)
    for c in covars_c:
        or_v = np.exp(mc.params[c])
        ci = np.exp(mc.conf_int().loc[c].values)
        logger.info(f"  {c}: OR={or_v:.3f} [{ci[0]:.3f}, {ci[1]:.3f}], p={mc.pvalues[c]:.4f}")
    logger.info(f"  n={len(dc)}, pseudo-R²={mc.prsquared:.4f}")

    # Summary
    logger.info("\n=== Summary: Effect of HHI across model specifications ===")
    logger.info(f"  Model A (no tyrving_main):                 HHI OR = {np.exp(ma.params['hhi_early_z']):.3f}")
    logger.info(f"  Model B (+ tyrving_main):                  HHI OR = {np.exp(mb.params['hhi_early_z']):.3f}")
    logger.info(f"  Model C (tyrving_main replaces tyrving_best): HHI OR = {np.exp(mc.params['hhi_early_z']):.3f}")

    # Save table
    rows = []
    for label, model, covars in [
        ("Model A: with tyrving_best", ma, covars_a),
        ("Model B: + tyrving_main", mb, covars_b),
        ("Model C: tyrving_main replaces tyrving_best", mc, covars_c),
    ]:
        for c in covars:
            rows.append({
                "Model": label,
                "Covariate": c,
                "OR": round(np.exp(model.params[c]), 3),
                "CI low": round(np.exp(model.conf_int().loc[c, 0]), 3),
                "CI high": round(np.exp(model.conf_int().loc[c, 1]), 3),
                "p": round(model.pvalues[c], 4),
            })
    tab = pd.DataFrame(rows)
    out_path = DATA_DIR.parent / "submission_pse" / "tables" / "tableS18_specialization_confound.csv"
    tab.to_csv(out_path, index=False)
    logger.info(f"\n  Saved to {out_path}")


if __name__ == "__main__":
    main()
