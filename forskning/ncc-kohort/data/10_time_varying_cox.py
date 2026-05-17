"""
Steg 10: Tidsvarierende HR for volum-effekten (håndterer PH-brudd).

Splitter follow-up i tre perioder (early/mid/late) og estimerer HR
for volum-ved-milepælen i hver. Hvis effekten er i samme retning men
varierer i størrelse, viser dette PH-bruddet OK uten å rokke ved
hovedkonklusjonen.
"""

import logging
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent
ANALYSE_FILE = DATA_DIR / "analysedata_utvidet.csv"
TAB_DIR = DATA_DIR.parent / "submission_pse" / "tables"


def load_data():
    df = pd.read_csv(ANALYSE_FILE)
    df["event"] = (df["aktiv_naa"] == 0).astype(int)
    df["baseline_age"] = df["stevne_aar"] - df["birth_year"]
    df["duration_age"] = (df["alder_ved_slutt"] - df["baseline_age"]).clip(lower=0.5)
    df["female"] = (df["gender"] == "F").astype(int)
    for c in ["tyrving_best", "vol_milepael", "hhi_early"]:
        df[f"{c}_z"] = (df[c] - df[c].mean()) / df[c].std()
    return df


def time_split_cox(df):
    """Cox in three follow-up periods to characterize time-varying HR."""
    covars = ["female", "tyrving_best_z", "hhi_early_z", "vol_milepael_z", "n_msk_typer"]
    base = df[["duration_age", "event"] + covars].dropna()

    # Create person-time split: 0-3 years, 3-6 years, 6+ years
    cuts = [0, 3, 6, 100]
    labels = ["Years 0-3 (age 13-17)", "Years 3-6 (age 16-19)", "Years 6+ (age 19+)"]

    rows = []
    for low, high, lbl in zip(cuts[:-1], cuts[1:], labels):
        # Split person-time: each athlete contributes to each interval up to their event/censoring
        sub = base.copy()
        # Athletes still at risk at start of interval
        at_risk = sub[sub["duration_age"] > low].copy()
        # Truncate duration to interval upper bound
        at_risk["interval_duration"] = at_risk["duration_age"].clip(upper=high) - low
        # Event happens only if duration_age <= high
        at_risk["interval_event"] = ((at_risk["duration_age"] <= high) &
                                       (at_risk["event"] == 1)).astype(int)
        at_risk = at_risk[at_risk["interval_duration"] > 0]

        cph = CoxPHFitter()
        try:
            cph.fit(at_risk[["interval_duration", "interval_event"] + covars],
                    duration_col="interval_duration", event_col="interval_event")
            for cov in covars:
                rows.append({
                    "Period": lbl,
                    "n at risk": len(at_risk),
                    "events in interval": int(at_risk["interval_event"].sum()),
                    "Covariate": cov,
                    "HR": round(np.exp(cph.params_[cov]), 3),
                    "CI low": round(np.exp(cph.confidence_intervals_.loc[cov, "95% lower-bound"]), 3),
                    "CI high": round(np.exp(cph.confidence_intervals_.loc[cov, "95% upper-bound"]), 3),
                    "p": round(cph.summary.loc[cov, "p"], 4),
                })
            logger.info(f"  {lbl}: n={len(at_risk)}, events={int(at_risk['interval_event'].sum())}, "
                        f"C-index={cph.concordance_index_:.3f}")
        except Exception as e:
            logger.warning(f"  {lbl} failed: {e}")

    tab = pd.DataFrame(rows)
    tab.to_csv(TAB_DIR / "tableS8_time_varying.csv", index=False)

    # Print volume coefficient evolution
    logger.info("\n  Volume effect across periods (key finding):")
    vol_rows = tab[tab["Covariate"] == "vol_milepael_z"]
    for _, row in vol_rows.iterrows():
        logger.info(f"    {row['Period']}: HR={row['HR']} [{row['CI low']}, {row['CI high']}], p={row['p']}")

    return tab


def main():
    df = load_data()
    logger.info(f"Lastet {len(df)} utøvere\n")
    logger.info("=== TIDSVARIERENDE HR FOR VOLUM (håndterer PH-brudd) ===")
    time_split_cox(df)
    logger.info("\nFerdig. Output i tables/tableS8_time_varying.csv")


if __name__ == "__main__":
    main()
