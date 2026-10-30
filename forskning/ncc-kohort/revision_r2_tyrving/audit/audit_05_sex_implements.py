"""
audit_05_sex_implements.py — Checks registered sex against the sex-specific implements and hurdle heights
an athlete used at ages 12-17 (Supplementary Methods S-M3).

Throws, hurdles and race walking are registered with their implement or hurdle specification, and the
Tyrving table holds a row for a specification only for the sex and ages that use it (e.g. shot 4 kg for
boys aged 14-15, 3 kg for girls aged 14-17). For every such result at ages 12-17 we ask whether it can
be scored as a male and as a female result (tyrving_r2). Results that fit both sexes carry no
information. An athlete's implements give *clear evidence* for one sex when at least three more results
fit that sex than the other.

Compares the corrected sex (register after its July 2026 correction; data_private/corrected) with the
original analysis file, and reports how often clear evidence contradicts the registered sex.

Output: audit/audit_05_summary.csv
"""

import logging
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import tyrving_r2 as ty  # noqa: E402
from r1_paths import CDATA, DATA  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
MARGIN = 3


def main():
    coh = pd.read_csv(CDATA / "kohort_utvidet.csv")
    orig = pd.read_csv(DATA / "analysedata_utvidet.csv", usecols=["athlete_id", "gender"]).rename(columns={"gender": "gender_orig"})
    kar = pd.read_csv(CDATA / "karrieredata_utvidet.csv", low_memory=False,
                      usecols=["athlete_id", "date", "event_code", "result_type", "performance_value"])
    kar = kar[kar["event_code"].isin(ty._SPEC)].merge(coh[["athlete_id", "birth_year", "gender"]], on="athlete_id")
    kar["age"] = pd.to_datetime(kar["date"]).dt.year - kar["birth_year"]
    kar = kar[kar["age"].between(12, 17)]
    table = ty.parse_tyrving_xls()
    for g in ["M", "F"]:
        kar[f"fit_{g}"] = [ty.beregn_tyrving_poeng(None if pd.isna(v) else float(v), c, r, g, a, table) is not None
                           for v, c, r, a in zip(kar["performance_value"], kar["event_code"], kar["result_type"], kar["age"])]
    s = kar.groupby("athlete_id")[["fit_M", "fit_F"]].sum()
    for lab, k in [("evidence", MARGIN), ("leaning", 1)]:
        s[lab] = "none"
        s.loc[s["fit_M"] >= s["fit_F"] + k, lab] = "M"
        s.loc[s["fit_F"] >= s["fit_M"] + k, lab] = "F"
    s = s.join(coh.set_index("athlete_id")["gender"]).join(orig.set_index("athlete_id")["gender_orig"])
    clear = s[s["evidence"] != "none"]
    lean = s[s["leaning"] != "none"]
    in_orig = s.index.isin(orig["athlete_id"])          # athletes added by the corrected cohort definition excluded here
    changed = s[in_orig & (s["gender"].fillna("NA") != s["gender_orig"].fillna("NA"))]
    ch_lean = changed[changed["leaning"] != "none"]
    rows = [
        ("athletes with sex-specific results at ages 12-17", len(s)),
        (f"athletes with clear implement evidence (margin >= {MARGIN} results)", len(clear)),
        ("  clear evidence contradicts the register sex now", int((clear["evidence"] != clear["gender"]).sum())),
        ("  clear evidence contradicts the sex in the original analysis file", int((clear["evidence"] != clear["gender_orig"].fillna("NA")).sum())),
        ("athletes whose implements lean to one sex (margin >= 1)", len(lean)),
        ("  leaning contradicts the register sex now", int((lean["leaning"] != lean["gender"]).sum())),
        ("original cohort members whose sex differs from the register now (with implement results)", len(changed)),
        ("  of whom implements lean to one sex (margin >= 1)", len(ch_lean)),
        ("  ... leaning agrees with the register now", int((ch_lean["leaning"] == ch_lean["gender"]).sum())),
        ("  ... leaning agrees with the original file", int((ch_lean["leaning"] == ch_lean["gender_orig"]).sum())),
    ]
    out = pd.DataFrame(rows, columns=["Check", "Value"])
    out.to_csv(HERE / "audit_05_summary.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
