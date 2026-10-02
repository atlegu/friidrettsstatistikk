"""
r1_02_rerun_original_scripts.py — Re-run the original analysis scripts (08-16)
unchanged, on the corrected data (r1_00) carrying the R1 variable corrections:

  * hhi_early   <- hhi_13_14 (ages-13-14 results only; reviewer comment 1)
  * tyrving_*   <- exact Tyrving scoring (tyrving_r2.py; reviewer comment 4 and data audit)

The scripts are copied into a private sandbox (revision_r1/_rerun/, not in git)
next to the corrected career and cohort data, a modified analysedata_utvidet.csv and a
shim `tyrvingtabellen.py` that re-exports the corrected scoring. With the ORIGINAL data
the same sandbox reproduces every submitted table byte-for-byte (verified 2026-10-01), so
any difference in the outputs is attributable to the corrections. The only code change is
that 16 counts meets as competition days (meet_day), as 07 does in r1_00.

Outputs: revision_r1/tables/rerun/*.csv (original file names) + rerun.log
"""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent
sys.path.insert(0, str(HERE))
from r1_paths import CDATA, DATA  # noqa: E402

SANDBOX = R1 / "_rerun"
OUT = R1 / "tables" / "rerun"
PY = sys.executable
SCRIPTS = ["08_analyser_pse.py", "09_sensitivity_pse.py", "10_time_varying_cox.py",
           "11_landmark_calibration.py", "13_reviewer_response_analyses.py",
           "15_specialization_confound_check.py", "16_revision_analyses.py"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SHIM = '''"""Shim: the R1 re-run uses the exact Tyrving scoring (revision_r1/analysis/tyrving_r2.py)."""
import sys
sys.path.insert(0, "{analysis}")
from tyrving_r2 import parse_tyrving_xls, beregn_tyrving_poeng  # noqa: F401
'''


def corrected_analysis_data():
    df = pd.read_csv(CDATA / "analysedata_utvidet.csv", low_memory=False)
    v = pd.read_csv(R1 / "data_private" / "r1_variables.csv")
    df = df.merge(v, on="athlete_id", how="left")
    df["hhi_early_07"] = df["hhi_early"]
    df["hhi_early"] = df["hhi_13_14"].round(3)
    for old, new in [("tyrving_best", "tyrving_best_r1"), ("tyrving_mean", "tyrving_mean_r1"),
                     ("tyrving_peak_pre15", "tyrving_peak_pre15_r1")] + \
                    [(f"tyrving_age_{a}", f"tyrving_age_{a}_r1") for a in (13, 14, 15, 16)]:
        df[old + "_07"] = df[old]
        df[old] = df[new]
    # slope over ages 13-16 from the corrected per-age maxima (as in the original builder)
    ages = np.array([13, 14, 15, 16])

    def slope(row):
        pts = [(a, row[f"tyrving_age_{a}"]) for a in ages if pd.notna(row[f"tyrving_age_{a}"])]
        return round(float(np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)[0]), 1) if len(pts) >= 2 else np.nan

    df["tyrving_slope_13_16"] = df.apply(slope, axis=1)
    df["prestasjonskategori"] = pd.cut(df["tyrving_best"], bins=[-np.inf, 600, 800, 1000, 1200, np.inf],
                                       labels=["Svak", "Under snitt", "Middels", "God", "Sterk"])
    keep = [c for c in df.columns if not c.endswith("_r1") and not c.endswith("_r1_nozone")]
    return df[keep]


def main():
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    (SANDBOX / "data").mkdir(parents=True)
    (SANDBOX / "submission_pse" / "tables").mkdir(parents=True)
    (SANDBOX / "submission_pse" / "figures").mkdir(parents=True)
    for s in SCRIPTS:
        shutil.copy(DATA / s, SANDBOX / "data" / s)
    # meets are counted as competition days (r1_00, correction 6): the one meet count outside 07
    f16 = SANDBOX / "data" / "16_revision_analyses.py"
    src = f16.read_text()
    assert src.count('["meet_id"].nunique()') == 1
    f16.write_text(src.replace('["meet_id"].nunique()', '["meet_day"].nunique()'))
    for f in ["karrieredata_utvidet.csv", "kohort_utvidet.csv"]:
        (SANDBOX / "data" / f).symlink_to(CDATA / f)
    (SANDBOX / "data" / "poengtabell-tyrvingtabellen.xls").symlink_to(DATA / "poengtabell-tyrvingtabellen.xls")
    (SANDBOX / "data" / "tyrvingtabellen.py").write_text(SHIM.format(analysis=HERE))
    corrected_analysis_data().to_csv(SANDBOX / "data" / "analysedata_utvidet.csv", index=False)

    log = open(R1 / "tables" / "rerun.log", "w")
    for s in SCRIPTS:
        logger.info(f"running {s}")
        log.write(f"##### {s}\n")
        r = subprocess.run([PY, s], cwd=SANDBOX / "data", capture_output=True, text=True,
                           env={"MPLBACKEND": "Agg", "PATH": "/usr/bin:/bin"})
        log.write(r.stdout + r.stderr)
        if r.returncode != 0:
            logger.error(f"{s} failed:\n{r.stderr[-2000:]}")
            raise SystemExit(1)
    log.close()
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SANDBOX / "submission_pse" / "tables", OUT)
    logger.info(f"done -> {OUT}")


if __name__ == "__main__":
    main()
