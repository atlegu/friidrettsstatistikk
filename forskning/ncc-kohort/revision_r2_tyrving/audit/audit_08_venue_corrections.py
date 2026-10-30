"""
audit_08_venue_corrections.py - venue corrections for baseline-meet results filed under another venue's record.

The register audit of 3 October 2026 compared every meet record with the source pages
(scraper/rydd_feil_stevnepost.py, dry run; plan file below). For the IJSSC career data it lists 163
results of the baseline meet (31 Aug 2013 and 13 Sep 2014) that the register files under another
venue's record of the same meet: 148 are 600 m results (already ignored by the venue rule in r1_00,
see its docstring item 5), 15 are in other events. r1_00 reads the venue of these results from this
file before inferring region. Championship types were also re-derived with the source's meet names;
no athlete's count changes, so meet names are left as recorded.

Input:  the plan of the register audit (rows with a result id and the source's venue, y_sted)
        data_private/corrected/karrieredata_utvidet.csv (ids and baseline flag)
Output: data_private/baseline_venue_corrections.csv (id, meet_city): athlete-level, git-ignored
"""

import logging
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "analysis"))
from r1_paths import CDATA, PRIV  # noqa: E402

PLAN = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/.claude/worktrees/charming-mendel-062756/"
            "scraper/logs/feil_stevnepost_plan_20261003_154403.csv")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    plan = pd.read_csv(PLAN, usecols=["result_id", "y_sted", "gruppe", "handling"])
    kar = pd.read_csv(CDATA / "karrieredata_utvidet.csv", low_memory=False, usecols=["id", "er_lekene", "event_code"])
    base = kar[kar["er_lekene"] == 1].merge(plan, left_on="id", right_on="result_id")
    out = base[["id", "y_sted"]].rename(columns={"y_sted": "meet_city"}).sort_values("id")
    out.to_csv(PRIV / "baseline_venue_corrections.csv", index=False)
    logger.info(f"baseline-meet results in the plan: {len(base)} (by group: {base['gruppe'].value_counts().to_dict()})")
    logger.info(f"written: {len(out)} rows to {PRIV / 'baseline_venue_corrections.csv'}")


if __name__ == "__main__":
    main()
