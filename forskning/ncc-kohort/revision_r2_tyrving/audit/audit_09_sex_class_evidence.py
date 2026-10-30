"""
audit_09_sex_class_evidence.py - class evidence behind the sex coding of the cohort (Supplementary Methods S-M3).

The register publishes results under sex-specific classes (boys/girls, men/women). In July 2026 the sex
variable of the register extract was re-derived from the class headings of the federation's meet pages
(scraper/fix_gender_from_source.py; evidence rows in scraper/new_meets_data/gender_evidence_*.jsonl.gz,
with meet, event, class, name and birth year per result), with first names used only where no class is
published (ages 10-12). This script checks, for the cohort athletes whose sex changed or became known
between the submitted analysis file and the corrected data, whether class headings were found for them and
whether they agree with the sex now used.

Input:  ../data/kohort_utvidet.csv (submitted), data_private/corrected/kohort_utvidet.csv, the athletes table
        (names, read-only), the evidence files.
Output: audit/audit_09_summary.csv (counts only; no athlete-level output)
"""

import gzip
import json
import logging
import sys
import unicodedata
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "analysis"))
from r1_paths import CDATA, DATA  # noqa: E402

EVIDENCE = [Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/new_meets_data") / f
            for f in ["gender_evidence_20260704_004330.jsonl.gz", "gender_evidence_recovered_20260704.jsonl.gz"]]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def norm(s):
    return unicodedata.normalize("NFC", str(s)).strip().lower()


def class_sex(c):
    c = c.strip().upper()
    return "F" if c.startswith(("J", "K", "W")) else "M" if c.startswith(("G", "M")) else None


def main():
    import r1_00_corrected_data as r0          # register client (read-only)
    old = pd.read_csv(DATA / "kohort_utvidet.csv", usecols=["athlete_id", "gender"]).set_index("athlete_id")["gender"]
    new = pd.read_csv(CDATA / "kohort_utvidet.csv", usecols=["athlete_id", "gender"]).set_index("athlete_id")["gender"]
    changed = [a for a in new.index if a in old.index and str(old[a]) != str(new[a])]
    added = [a for a in new.index if a not in old.index]
    sb = r0.client()
    rows = []
    ids = changed + added
    for i in range(0, len(ids), 50):
        rows += sb.table("athletes").select("id,first_name,last_name,birth_year").in_("id", ids[i:i + 50]).execute().data
    ath = pd.DataFrame(rows).set_index("id")
    key = {a: (norm(f"{ath.loc[a, 'first_name']} {ath.loc[a, 'last_name']}"), int(ath.loc[a, "birth_year"])) for a in ath.index}
    wanted = set(key.values())
    seen = {}
    for f in EVIDENCE:
        with gzip.open(f, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                k = (norm(r["name"]), r.get("birth_year"))
                if k in wanted:
                    seen.setdefault(k, set()).add(class_sex(r["class"]))
    out = []
    for lab, group in [("original members whose sex changed or became known", changed), ("members added in the revision", added)]:
        ev = [a for a in group if key.get(a) in seen]
        agree = [a for a in ev if new[a] in seen[key[a]] and len(seen[key[a]] - {None}) == 1]
        out += [(f"{lab}: n", len(group)), (f"{lab}: with class headings on the meet pages", len(ev)),
                (f"{lab}: class headings agree with the sex used (one sex only)", len(agree))]
    pd.DataFrame(out, columns=["Check", "Value"]).to_csv(HERE / "audit_09_summary.csv", index=False)
    for c, v in out:
        logger.info(f"{c}: {v}")


if __name__ == "__main__":
    main()
