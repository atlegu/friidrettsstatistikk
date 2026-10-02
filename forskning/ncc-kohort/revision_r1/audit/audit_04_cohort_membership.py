"""
audit_04_cohort_membership.py — Audit of cohort membership and of the baseline-meet definition.

The national 13-14 meet (NCC/PEAB/Bendit-lekene, Ungdomslekene) is held on one weekend a year at
three venues. The original pipeline identified it by meet name. Two venue-days are registered
under other names (2014-09-13 Jessheim: "Jessheim, Nasjonalt stevne" and "Peab-lekene";
2016-08-28 Osterøy: "Osterøy, Seriestevne"), and the name patterns used for the baseline
results ("eab", "endit", "NCC", ...) also match unrelated meets. This script identifies the meet
by venue and date instead (register state at extraction: created_at <= 2026-05-18), lists every
participant born 1998-2002, and compares with the analysis cohort.

Output: audit/audit_04_summary.csv, data_private/audit_lekene_participants.csv
"""

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

HERE = Path(__file__).parent
R1 = HERE.parent
DATA = Path("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/forskning/ncc-kohort/data")
load_dotenv("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/.env")
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
CUTOFF = "2026-05-18T00:00:00+00:00"

# lekene weekends (both days) and venue cities, from the meets table (see audit notes)
WEEKENDS = {2011: ["2011-09-03", "2011-09-04"], 2012: ["2012-09-08", "2012-09-09"],
            2013: ["2013-08-31", "2013-09-01"], 2014: ["2014-09-13", "2014-09-14"],
            2015: ["2015-09-05", "2015-09-06"], 2016: ["2016-08-27", "2016-08-28"]}
VENUES = {"Romerike Friidrettstadion": "Østlandet", "Lillestrøm": "Østlandet", "Jessheim Friidrettsstadion": "Østlandet",
          "Jessheim": "Østlandet", "Osterøy Stadion": "Vestlandet", "Osterøy": "Vestlandet",
          "Øverlands Minde": "Midt-Norge", "Stjørdal": "Midt-Norge"}
MAIN_VENUES = {"Romerike Friidrettstadion", "Jessheim Friidrettsstadion", "Osterøy Stadion", "Øverlands Minde"}


def lekene_meets():
    rows = []
    for year, days in WEEKENDS.items():
        res = sb.table("meets").select("id,name,city,start_date").in_("start_date", days).execute().data
        rows += [dict(r, year=year) for r in res if r["city"] in VENUES]
    m = pd.DataFrame(rows)
    m["region"] = m["city"].map(VENUES)
    return m


def participants(meet_ids):
    out = []
    for mid in meet_ids:
        offset = 0
        while True:
            res = (sb.table("results").select("id,athlete_id,meet_id,date,created_at")
                   .eq("meet_id", mid).lte("created_at", CUTOFF).order("id")
                   .range(offset, offset + 999).execute().data)
            out += res
            if len(res) < 1000:
                break
            offset += 1000
    return pd.DataFrame(out)


def athletes(ids):
    out = []
    ids = list(ids)
    for i in range(0, len(ids), 150):
        out += sb.table("athletes").select("id,gender,birth_year,birth_date").in_("id", ids[i:i + 150]).execute().data
    return pd.DataFrame(out).rename(columns={"id": "athlete_id"})


def main():
    m = lekene_meets()
    logger.info(f"lekene venue-day meet records: {len(m)}")
    logger.info("\n" + m.sort_values(["year", "city", "start_date"])[["year", "start_date", "city", "name"]].to_string(index=False))
    r = participants(m["id"].tolist()).merge(
        m.rename(columns={"id": "meet_id"})[["meet_id", "year", "region", "name", "city"]], on="meet_id")
    a = athletes(r["athlete_id"].unique())
    r = r.merge(a, on="athlete_id", how="left")
    r["age"] = r["year"] - r["birth_year"]
    r["first_year"] = r.groupby("athlete_id")["year"].transform("min")
    rf = r[r["year"] == r["first_year"]].copy()
    rf["main"] = rf["city"].isin(MAIN_VENUES)
    # region = venue of the first edition; majority of the athlete's results at the three main venue records
    # (small city-only records sometimes collect one event from several venues)
    reg = (rf[rf["main"]].groupby("athlete_id")["region"].agg(lambda s: s.value_counts().idxmax())
           .combine_first(rf.groupby("athlete_id")["region"].agg(lambda s: s.value_counts().idxmax())))
    n_reg = rf[rf["main"]].groupby("athlete_id")["region"].nunique()
    first = (r.groupby("athlete_id")
             .agg(first_year=("year", "min"), n_editions=("year", "nunique"),
                  gender=("gender", "first"), birth_year=("birth_year", "first"), n_results=("id", "size"))
             .join(reg.rename("region")).join(n_reg.rename("n_main_regions_first_year"))
             .reset_index())
    first.to_csv(R1 / "data_private" / "audit_lekene_participants.csv", index=False)
    pool = first[first["birth_year"].between(1998, 2002)]
    coh = pd.read_csv(DATA / "kohort_utvidet.csv")
    ana = pd.read_csv(DATA / "analysedata_utvidet.csv", usecols=["athlete_id"])
    coh = coh[coh["athlete_id"].isin(ana["athlete_id"])]
    ed_year = {"ncc_2011": 2011, "ncc_2012": 2012, "peab_2013": 2013, "peab_2014": 2014,
               "bendit_2015": 2015, "ungdomslekene_2016": 2016}
    coh["first_year_cohort"] = coh["forste_utgave"].map(ed_year)
    j = coh.merge(pool, on="athlete_id", how="left", suffixes=("", "_venue"))
    rows = [
        ("participants at the lekene venue-days (any birth year)", len(first)),
        ("  of whom born 1998-2002", len(pool)),
        ("analysis cohort", len(coh)),
        ("cohort members found among venue-day participants", int(j["first_year"].notna().sum())),
        ("cohort members NOT found (no venue-day result in register state May 2026)", int(j["first_year"].isna().sum())),
        ("participants born 1998-2002 NOT in the cohort", int((~pool["athlete_id"].isin(coh["athlete_id"])).sum())),
        ("cohort first edition differs from venue-day first edition", int((j["first_year"].notna() & (j["first_year"] != j["first_year_cohort"])).sum())),
        ("cohort region differs from venue region (first edition)", int((j["first_year"].notna() & (j["region"] != j["region_venue"])).sum())),
    ]
    missing = pool[~pool["athlete_id"].isin(coh["athlete_id"])]
    for (by, fy), n in missing.groupby(["birth_year", "first_year"]).size().items():
        rows.append((f"  not in cohort: born {int(by)}, first edition {int(fy)}", int(n)))
    out = pd.DataFrame(rows, columns=["Check", "Value"])
    out.to_csv(HERE / "audit_04_summary.csv", index=False)
    print(out.to_string(index=False))
    # which meet names do the non-cohort participants have?
    rr = r[r["athlete_id"].isin(missing["athlete_id"])]
    print("\nmeet records of participants not in the cohort:")
    print(rr.groupby(["year", "name"])["athlete_id"].nunique().to_string())


if __name__ == "__main__":
    main()
