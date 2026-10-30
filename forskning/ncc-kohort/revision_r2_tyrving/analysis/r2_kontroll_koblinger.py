"""
r2_kontroll_koblinger.py — check the complete Tyrving mapping (tyrving_r3) against the career data.

For every code that tyrving_r3 maps and tyrving_r2 does not: results scored, by sex and age, with
the median score; every added code must score some result at ages 13-16 (otherwise the mapping is
wrong or unnecessary). Then: baseline-meet results whose score changes (expected: none), and the
codes still unscored at ages 13-16 with a count (no table row for the athlete's sex and age).

Output: tables/r2_koblinger.csv, tables/r2_uskaarede_13_16.csv; summary to the log.
"""

import logging

import pandas as pd

import tyrving_r2 as t2
import tyrving_r3 as t3
from r1_paths import CDATA, R1

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
TAB = R1 / "tables"
EDITION_YEAR = {"ncc_2011": 2011, "ncc_2012": 2012, "peab_2013": 2013, "peab_2014": 2014,
                "bendit_2015": 2015, "ungdomslekene_2016": 2016}


def main():
    kar = pd.read_csv(CDATA / "karrieredata_utvidet.csv", low_memory=False,
                      usecols=["athlete_id", "date", "event_code", "result_type", "performance_value", "er_lekene"])
    coh = pd.read_csv(CDATA / "kohort_utvidet.csv", usecols=["athlete_id", "gender", "birth_year", "forste_utgave"])
    kar = kar.merge(coh, on="athlete_id")
    kar["year"] = pd.to_datetime(kar["date"]).dt.year
    kar["age"] = kar["year"] - kar["birth_year"]
    tab2, tab3 = t2.parse_tyrving_xls(), t3.parse_tyrving_xls()

    def score(mod, tab, d):
        return pd.Series([mod.beregn_tyrving_poeng(None if pd.isna(v) else float(v), c, rt, g, a, tab)
                          for v, c, rt, g, a in zip(d["performance_value"], d["event_code"], d["result_type"],
                                                    d["gender"], d["age"])], index=d.index, dtype="float")

    nye = sorted(set(t3._SPEC) - set(t2._SPEC))
    d = kar[kar["event_code"].isin(nye) & kar["age"].between(10, 19)].copy()
    d["p"] = score(t3, tab3, d)
    g = (d.groupby(["event_code", "gender", "age"])
         .agg(resultater=("p", "size"), skaaret=("p", lambda s: int(s.notna().sum())), median=("p", "median"))
         .reset_index())
    g = g[g["skaaret"] > 0]
    g.to_csv(TAB / "r2_koblinger.csv", index=False)
    finnes = set(kar.loc[kar["age"].between(13, 16), "event_code"])
    fravaerende = [k for k in nye if k not in finnes]
    feil = [k for k in nye if k in finnes and k not in set(g.loc[g["age"].between(13, 16), "event_code"])]
    logger.info(f"nye koblinger: {len(nye)}; ikke i dataene ved 13-16 (uskadelige): {fravaerende}")
    if feil:
        raise SystemExit(f"koder i dataene som aldri får poeng ved 13-16 (feil kobling?): {feil}")
    lb = d[d["event_code"] == "liten_ball_150gram"]["p"]
    logger.info(f"liten ball 150 g etter cm-reparasjon: n {lb.notna().sum()}, median {lb.median():.0f}, "
                f"andel 0 poeng {(lb == 0).mean():.2f}")

    base = kar[(kar["er_lekene"] == 1) & (kar["year"] == kar["forste_utgave"].map(EDITION_YEAR))].copy()
    endret = (score(t2, tab2, base).fillna(-1) != score(t3, tab3, base).fillna(-1)).sum()
    logger.info(f"baseline-resultater med endret poengsum: {int(endret)} av {len(base)}")

    a = kar[kar["age"].between(13, 16)].copy()
    a["p2"], a["p3"] = score(t2, tab2, a), score(t3, tab3, a)
    logger.info(f"resultater 13-16 med poeng: tyrving_r2 {int(a['p2'].notna().sum())}, "
                f"tyrving_r3 {int(a['p3'].notna().sum())} av {len(a)}")
    rest = (a[a["p3"].isna()].groupby("event_code").size().rename("uskaaret_13_16")
            .sort_values(ascending=False).reset_index())
    rest.to_csv(TAB / "r2_uskaarede_13_16.csv", index=False)


if __name__ == "__main__":
    main()
