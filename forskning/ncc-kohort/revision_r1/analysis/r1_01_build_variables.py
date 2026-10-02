"""
r1_01_build_variables.py — Corrected baseline variables for the IJSSC revision (R1).

Built on the corrected data from r1_00_corrected_data.py (data audit of 2 October 2026).

1. HHI (reviewer comment 1). The submitted `hhi_early` pooled every result up to
   the baseline calendar year + 2, i.e. results from ages 11-16. It is replaced
   by `hhi_13_14`, computed only from results in the age-13 and age-14 calendar
   years, so the primary model is strictly baseline-only.

2. Tyrving (reviewer comment 4, missingness). The submitted scoring routine left
   all throws, hurdles, take-off-zone jumps and race walking unscored (event-code
   mapping gap), which produced the 19.7% missingness, and the data audit found that
   it also used the wrong formula for middle-distance races and for throws and pole
   vault. All Tyrving variables are rescored with the exact workbook formulas
   (tyrving_r2.py). Baseline results are those at the athlete's first edition of the
   meet, identified by venue and date (er_lekene, set in r1_00).

Inputs: data_private/corrected/{analysedata,karrieredata}_utvidet.csv; data/analysedata_utvidet.csv
        (submitted analysis file, for the coverage comparison only)
Output: revision_r1/data_private/r1_variables.csv (athlete-level; not in git)
        revision_r1/tables/r1_variable_coverage.csv
"""

import logging
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import tyrving_r2 as ty  # noqa: E402
from r1_paths import CDATA, DATA, PRIV  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TAB = HERE.parent / "tables"
PRIV.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)
CAP = 1500
EDITION_YEAR = {"ncc_2011": 2011, "ncc_2012": 2012, "peab_2013": 2013, "peab_2014": 2014,
                "bendit_2015": 2015, "ungdomslekene_2016": 2016}
OLD_MAPPING = {"60m", "80m", "100m", "200m", "300m", "400m", "600m", "800m", "1000m", "1500m",
               "2000m", "3000m", "5000m", "60mh", "80mh", "200mh", "300mh", "1500msc", "2000msc",
               "hoyde", "stav", "lengde", "tresteg", "kule", "diskos", "slegge", "spyd", "liten_ball"}
MIN_CS = {"60m": 600, "80m": 800, "100m": 1000, "200m": 2000, "300m": 3500, "400m": 4500,
          "600m": 8000, "800m": 11000, "1000m": 15000, "1500m": 23000, "2000m": 32000, "3000m": 50000}


def hhi(s):
    sh = s.value_counts(normalize=True)
    return float((sh ** 2).sum())


def score(kar, table, zone_as_board=True):
    ty.ZONE_AS_BOARD = zone_as_board
    pv = kar["performance_value"].where(kar["performance_value"].notna(), None)
    out = [ty.beregn_tyrving_poeng(None if pd.isna(v) else float(v), c, rt, g, a, table)
           for v, c, rt, g, a in zip(pv, kar["event_code"], kar["result_type"], kar["gender"], kar["age"])]
    ty.ZONE_AS_BOARD = True
    s = pd.Series(out, index=kar.index, dtype="float")
    return s.clip(lower=0, upper=CAP)


def main():
    df = pd.read_csv(CDATA / "analysedata_utvidet.csv", low_memory=False)
    sub = pd.read_csv(DATA / "analysedata_utvidet.csv", low_memory=False)          # as submitted
    kar = pd.read_csv(CDATA / "karrieredata_utvidet.csv", low_memory=False,
                      usecols=["athlete_id", "date", "event_code", "event_category", "result_type",
                               "meet_name", "performance_value", "er_lekene"])
    kar["year"] = pd.to_datetime(kar["date"], errors="coerce").dt.year
    kar = kar.merge(df[["athlete_id", "birth_year", "gender", "forste_utgave"]], on="athlete_id", how="inner")
    kar["age"] = kar["year"] - kar["birth_year"]

    # sanity filter for obviously wrong run times (as in the original pipeline), after M.SS repair
    rep = [ty.repair_time(v, c) if pd.notna(v) else v for v, c in zip(kar["performance_value"], kar["event_code"])]
    kar["pv_repaired"] = rep
    bad = pd.Series(False, index=kar.index)
    for code, mn in MIN_CS.items():
        bad |= (kar["event_code"] == code) & (kar["pv_repaired"] < mn)
    kar = kar[~bad].copy()

    table = ty.parse_tyrving_xls()
    kar["tyr"] = score(kar, table, zone_as_board=True)
    kar["tyr_nozone"] = score(kar, table, zone_as_board=False)

    # --- baseline meet: the athlete's first edition (venue-day definition, r1_00)
    base = kar[(kar["er_lekene"] == 1) & (kar["year"] == kar["forste_utgave"].map(EDITION_YEAR))]
    b = base.groupby("athlete_id").agg(tyrving_best_r1=("tyr", "max"), tyrving_mean_r1=("tyr", "mean"),
                                       tyrving_best_r1_nozone=("tyr_nozone", "max"),
                                       baseline_results=("event_code", "size"))

    # --- within-event rank at the meet (robustness check for Tyrving's cross-event calibration):
    # percentile among all participants of the same age, sex and event in that year's edition
    # (every participant of the relevant ages is a cohort member), best over the athlete's events
    lek = kar[kar["er_lekene"] == 1].copy()
    lek["better_is_low"] = lek["result_type"].eq("time")
    lek["perf"] = lek["pv_repaired"].where(lek["better_is_low"], -lek["performance_value"])
    grp = lek.groupby(["year", "age", "gender", "event_code"])["perf"]
    n = grp.transform("count")
    lek["pctile"] = (100 * (1 - (grp.rank(method="average") - 1) / (n - 1))).where(n >= 5)
    lek = lek[lek["year"] == lek["forste_utgave"].map(EDITION_YEAR)]
    b = b.join(lek.groupby("athlete_id")["pctile"].max().rename("pctile_best_r1"))

    # --- per-age maxima, ages 13-16, and pre-15 peak (all meets)
    per = kar[kar["age"].between(13, 16)].groupby(["athlete_id", "age"])["tyr"].max().unstack()
    per.columns = [f"tyrving_age_{a}_r1" for a in per.columns]
    pre15 = kar[kar["age"].between(13, 14)].groupby("athlete_id")["tyr"].max().rename("tyrving_peak_pre15_r1")

    # --- HHI from ages 13-14 only
    w = kar[kar["age"].between(13, 14)]
    h = pd.DataFrame({"hhi_13_14": w.groupby("athlete_id")["event_category"].apply(hhi),
                      "res_13_14": w.groupby("athlete_id").size(),
                      "nkat_13_14": w.groupby("athlete_id")["event_category"].nunique()})

    out = df[["athlete_id"]].merge(b, on="athlete_id", how="left").merge(per, on="athlete_id", how="left") \
        .merge(pre15, on="athlete_id", how="left").merge(h, on="athlete_id", how="left")
    out.to_csv(PRIV / "r1_variables.csv", index=False)

    # --- coverage report (submitted analysis file vs. corrected data)
    base_codes = base["event_code"]
    old_scored = base_codes.isin(OLD_MAPPING)
    both = sub[["athlete_id", "tyrving_best"]].merge(out, on="athlete_id")
    rows = [
        {"Quantity": "Cohort (n)", "Original scoring": len(sub), "Corrected scoring": len(df)},
        {"Quantity": "Baseline-meet results", "Original scoring": "", "Corrected scoring": len(base)},
        {"Quantity": "Baseline results with a Tyrving score (%)",
         "Original scoring": round(100 * float(old_scored.mean()), 1),
         "Corrected scoring": round(100 * float(base["tyr"].notna().mean()), 1)},
        {"Quantity": "Athletes without baseline Tyrving (n)", "Original scoring": int(sub["tyrving_best"].isna().sum()),
         "Corrected scoring": int(out["tyrving_best_r1"].isna().sum())},
        {"Quantity": "Athletes without baseline Tyrving, zone jumps unscored (n)", "Original scoring": "",
         "Corrected scoring": int(out["tyrving_best_r1_nozone"].isna().sum())},
        {"Quantity": "Mean baseline Tyrving best", "Original scoring": round(float(sub["tyrving_best"].mean()), 1),
         "Corrected scoring": round(float(out["tyrving_best_r1"].mean()), 1)},
        {"Quantity": "Correlation original vs corrected (athletes scored by both)",
         "Original scoring": "", "Corrected scoring": round(float(both[["tyrving_best", "tyrving_best_r1"]].corr().iloc[0, 1]), 3)},
        {"Quantity": "Athletes with HHI (ages 13-14) available (n)", "Original scoring": int(sub["hhi_early"].notna().sum()),
         "Corrected scoring": int(out["hhi_13_14"].notna().sum())},
        {"Quantity": "Baseline results at the 1,500-point cap (n)", "Original scoring": "",
         "Corrected scoring": int((base["tyr"] >= CAP).sum())},
    ]
    pd.DataFrame(rows).to_csv(TAB / "r1_variable_coverage.csv", index=False)
    unscored = base.loc[base["tyr"].isna(), "event_code"].value_counts()
    logger.info("Coverage:\n" + pd.DataFrame(rows).to_string(index=False))
    logger.info("Still-unscored baseline event codes:\n" + unscored.head(15).to_string())
    miss = out.loc[out["tyrving_best_r1"].isna(), "athlete_id"]
    logger.info(f"Athletes still missing baseline Tyrving: {len(miss)}")


if __name__ == "__main__":
    main()
