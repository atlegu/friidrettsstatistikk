"""
r1_00_corrected_data.py — Corrected cohort, career and analysis data (data audit, 2 October 2026).

The audit of the original pipeline (data/01, 06, 07) found the data problems below. This script
rebuilds the three data files from the register as it stood at the original extraction (results
created on or before 18 May 2026) and corrects them:

1. Extraction. The career data were paginated on a non-unique sort key (date): 332 rows were
   returned twice and 334 rows (240 athletes) were skipped (audit/audit_01, audit_02). Rows are
   de-duplicated by id and the skipped rows added.
2. Baseline meet and cohort membership. The national 13-14 meet was identified by meet name, but
   two venue-days are registered under other names (Jessheim 13 Sep 2014 "Nasjonalt stevne";
   Osterøy 28 Aug 2016 "Seriestevne"), some events under city-only records, and the name patterns
   used for the baseline results ("NCC", "eab", "endit", "ngdomsleken") also matched unrelated
   meets in the baseline year. The meet is now identified by venue and date: every result on the
   meet weekend at one of the three venues by an athlete aged 13-14 that year (audit/audit_04).
3. Follow-up. The career data included the partial 2026 season (extracted in May 2026). Follow-up
   ends 31 December 2025, as the manuscript states.
4. Sex. Register values after the register-wide correction of sex coding in July 2026. For every
   recoded athlete with implement evidence, the sex-specific implements and hurdle heights the
   athlete used at ages 12-17 agree with the corrected value.
5. Region. The venue of the athlete's editions of the meet. The 600 m, 1500 m and race-walk
   results of all three venues are filed under one venue's record in 2013-2015, so venue is read
   from the athlete's other events (the venue is then the same in both editions for every athlete
   who took part twice); athletes with endurance results only take their club's venue that year.
6. Volume. The register stores each day of a multi-day meet as a separate meet, and some days'
   results are filed under two meet records (above all the endurance lists in 5). Meets are
   therefore counted as competition days (distinct dates with a result): column meet_day, used
   in place of meet_id wherever meets are counted (07 and 16 are patched accordingly).

Tyrving scores in the analysis file use the exact workbook formulas (tyrving_r2.py, via a shim).

Outputs (data_private/corrected/, git-ignored): kohort_utvidet.csv, karrieredata_utvidet.csv,
analysedata_utvidet.csv, lekene_meets.csv; summary in audit/r1_00_summary.csv
"""

import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from r1_paths import CDATA, CUTOFF, DATA, ENV, FOLLOW_UP_END, PRIV, R1  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# meet weekends (both days) and venue cities; city-only records ("Jessheim", "Osterøy", ...) hold
# single events registered apart from the main venue record
WEEKENDS = {2011: ["2011-09-03", "2011-09-04"], 2012: ["2012-09-08", "2012-09-09"],
            2013: ["2013-08-31", "2013-09-01"], 2014: ["2014-09-13", "2014-09-14"],
            2015: ["2015-09-05", "2015-09-06"], 2016: ["2016-08-27", "2016-08-28"]}
VENUES = {"Romerike Friidrettstadion": "Østlandet", "Lillestrøm": "Østlandet",
          "Jessheim Friidrettsstadion": "Østlandet", "Jessheim": "Østlandet",
          "Osterøy Stadion": "Vestlandet", "Osterøy": "Vestlandet",
          "Øverlands Minde": "Midt-Norge", "Stjørdal": "Midt-Norge"}
MAIN_VENUES = {"Romerike Friidrettstadion", "Jessheim Friidrettsstadion", "Osterøy Stadion", "Øverlands Minde"}
NOT_LEKENE = re.compile(r"3xl", re.I)   # "Ungdomslekene 3XL", Jessheim 27 Aug 2016: 600 m for older athletes
ENDURANCE = {"600m", "800m", "1000m", "1500m", "2000m", "3000m", "kappgang_1000_m", "1000mg", "kappgang_2000_m"}
EDITION = {2011: "ncc_2011", 2012: "ncc_2012", 2013: "peab_2013", 2014: "peab_2014",
           2015: "bendit_2015", 2016: "ungdomslekene_2016"}
KOL = ("id,athlete_id,performance,performance_value,date,event_id,event_code,event_name,event_category,"
       "result_type,meet_id,meet_name,meet_city,meet_indoor,season_year,club_name,is_manual_time,status")
SANDBOX = R1 / "_rebuild"
SHIM = '''"""Shim: the corrected rebuild scores Tyrving with the exact workbook formulas (tyrving_r2.py)."""
import sys
sys.path.insert(0, "{analysis}")
from tyrving_r2 import parse_tyrving_xls, beregn_tyrving_poeng  # noqa: F401
'''
SUMMARY = []


def note(check, value):
    SUMMARY.append((check, value))
    logger.info(f"{check}: {value}")


def client():
    load_dotenv(ENV)
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def paged(make_query):
    """All rows of a query, paginated on the unique key id (deterministic)."""
    out, offset = [], 0
    while True:
        res = make_query().order("id").range(offset, offset + 999).execute().data
        out += res
        if len(res) < 1000:
            return out
        offset += 1000


def by_ids(sb, table, select, ids, chunk=150):
    out, ids = [], [i for i in dict.fromkeys(ids) if isinstance(i, str)]
    for i in range(0, len(ids), chunk):
        out += sb.table(table).select(select).in_("id", ids[i:i + chunk]).execute().data
    return out


def modal(s):
    """Most frequent value; None when missing or tied."""
    vc = s.dropna().value_counts()
    if vc.empty or (len(vc) > 1 and vc.iloc[0] == vc.iloc[1]):
        return None
    return vc.index[0]


# ----------------------------------------------------------------------------- cohort membership
def lekene_meets(sb):
    rows = []
    for year, days in WEEKENDS.items():
        res = sb.table("meets").select("id,name,city,start_date").in_("start_date", days).execute().data
        rows += [dict(r, year=year) for r in res if r["city"] in VENUES and not NOT_LEKENE.search(r["name"] or "")]
    m = pd.DataFrame(rows).rename(columns={"id": "meet_id", "name": "meet_record", "city": "venue_city"})
    m["region"] = m["venue_city"].map(VENUES)
    return m


def participants(sb, meets, old_kar):
    res = []
    for mid in meets["meet_id"]:
        res += paged(lambda: sb.table("results").select("id,athlete_id,meet_id,status")
                     .eq("meet_id", mid).lte("created_at", CUTOFF))
    res = pd.DataFrame(res)
    note("results at the meet's venue-days (register state 18 May 2026), by status",
         res["status"].fillna("NA").value_counts().to_dict())
    res = res[res["status"].fillna("OK").str.upper() != "DNS"]
    old_lek = old_kar.loc[old_kar["meet_id"].isin(meets["meet_id"]) & ~old_kar["id"].isin(res["id"]),
                          ["id", "athlete_id", "meet_id"]]
    note("venue-day rows in the original extract no longer in the register (kept)", len(old_lek))
    lek = pd.concat([res[["id", "athlete_id", "meet_id"]], old_lek], ignore_index=True)
    lek = lek.merge(meets[["meet_id", "year"]], on="meet_id")
    ath = pd.DataFrame(by_ids(sb, "athletes", "id,gender,birth_year,birth_date", lek["athlete_id"].tolist()))
    lek = lek.merge(ath.rename(columns={"id": "athlete_id"}), on="athlete_id", how="left")
    lek = lek[(lek["year"] - lek["birth_year"]).isin([13, 14])]
    agg = lek.groupby("athlete_id").agg(first_year=("year", "min"), antall_utgaver=("year", "nunique"),
                                        alle_utgaver=("year", lambda s: ",".join(EDITION[y] for y in sorted(set(s)))))
    coh = ath.rename(columns={"id": "athlete_id"}).set_index("athlete_id").join(agg, how="inner")
    note("participants aged 13-14 at the venue-days (any birth year)", len(coh))
    coh = coh[coh["birth_year"].between(1998, 2002)].copy()
    coh["forste_utgave"] = coh["first_year"].map(EDITION)
    coh["deltok_begge_aar"] = (coh["antall_utgaver"] >= 2).astype(int)
    return coh.reset_index(), set(lek["id"])


# ----------------------------------------------------------------------------- career data
def build_career(sb, coh, old_kar, reextract):
    ids = set(coh["athlete_id"])
    old = old_kar[old_kar["athlete_id"].isin(ids)]
    note("original extract rows for cohort members / duplicate ids",
         f"{len(old):,} / {int(old['id'].duplicated().sum())}")
    old = old.drop_duplicates("id")
    skipped = reextract.loc[reextract["athlete_id"].isin(ids) & ~reextract["id"].isin(old_kar["id"]), "id"].tolist()
    new_members = sorted(ids - set(old_kar["athlete_id"]))
    new_ids = []
    for i in range(0, len(new_members), 40):
        batch = new_members[i:i + 40]
        new_ids += [r["id"] for r in paged(lambda: sb.table("results").select("id").in_("athlete_id", batch)
                                           .lte("created_at", CUTOFF))]
    add = pd.DataFrame(by_ids(sb, "results_full", KOL, skipped + new_ids, chunk=100))
    add = add[add["status"] == "OK"].drop(columns="status")
    note("rows skipped by the original extraction, added", int(add["id"].isin(skipped).sum()))
    note("rows of the newly included cohort members", f"{int(add['id'].isin(new_ids).sum())} ({len(new_members)} athletes)")
    kar = pd.concat([old, add[old.columns]], ignore_index=True)
    n_late = int((kar["date"] > FOLLOW_UP_END).sum())
    kar = kar[kar["date"] <= FOLLOW_UP_END].copy()
    note("rows after 31 Dec 2025 removed (partial 2026 season)", n_late)
    kar["meet_indoor"] = kar["meet_indoor"].astype(str).str.lower().eq("true")
    kar["meet_day"] = kar["date"]
    return kar


def flag_lekene(kar, coh, lek_ids, meets):
    """er_lekene = 1 for a result at the meet (venue-day record, or venue city on the weekend) at age 13-14."""
    by = kar["athlete_id"].map(coh.set_index("athlete_id")["birth_year"])
    year = pd.to_datetime(kar["date"]).dt.year
    days = {d for v in WEEKENDS.values() for d in v}
    at_meet = kar["id"].isin(lek_ids) | kar["meet_id"].isin(meets["meet_id"]) | (
        kar["date"].isin(days) & kar["meet_city"].isin(VENUES) & ~kar["meet_name"].fillna("").str.contains("3XL", case=False))
    return (at_meet & (year - by).isin([13, 14])).astype(int)


def region_and_club(kar, coh):
    """Club at the first edition (as registered on the athlete's results) and venue region."""
    lek = kar[kar["er_lekene"] == 1].copy()
    lek["year"] = pd.to_datetime(lek["date"]).dt.year
    lek = lek.merge(coh[["athlete_id", "first_year"]], on="athlete_id")
    lek["region"] = lek["meet_city"].map(VENUES)
    first = lek[lek["year"] == lek["first_year"]]
    klubb = first.groupby("athlete_id")["club_name"].agg(lambda s: s.value_counts().idxmax() if s.notna().any() else None)
    clean = lek[lek["meet_city"].isin(MAIN_VENUES) & ~lek["event_code"].isin(ENDURANCE)]
    own = clean.groupby("athlete_id")["region"].agg(modal)
    # validation: athletes with clear venues in two editions
    ay = clean.groupby(["athlete_id", "year"])["region"].agg(modal).dropna().reset_index()
    two = ay.groupby("athlete_id").filter(lambda g: len(g) == 2)
    note("athletes with a clear venue in both editions: same venue both years",
         f"{two.groupby('athlete_id')['region'].nunique().eq(1).mean():.3f} (n = {two['athlete_id'].nunique()})")
    clean = clean.assign(klubb=clean["athlete_id"].map(klubb))
    club_year = clean.groupby(["klubb", "year"])["region"].agg(modal)
    club_all = clean.groupby("klubb")["region"].agg(modal)
    # leave-one-out check of the club rule on athletes with a clear own venue
    ok, tot = 0, 0
    for (k, y), g in clean[clean["athlete_id"].isin(own.dropna().index)].groupby(["klubb", "year"]):
        for aid in g["athlete_id"].unique():
            r = modal(g.loc[g["athlete_id"] != aid, "region"])
            if r is not None:
                tot += 1
                ok += int(r == own[aid])
    note("club rule (club's other athletes, same year) agrees with clear own venue", f"{ok / max(tot, 1):.3f} (n = {tot})")
    region, source = {}, {}
    for aid, fy in zip(coh["athlete_id"], coh["first_year"]):
        k = klubb.get(aid)
        for lab, val in [("own events", own.get(aid)), ("club, same year", club_year.get((k, fy))),
                         ("club, all years", club_all.get(k)),
                         ("own, incl. endurance", modal(lek.loc[lek["athlete_id"] == aid, "region"]))]:
            if val is not None and val == val:
                region[aid], source[aid] = val, lab
                break
    note("region source", pd.Series(source).value_counts().to_dict())
    return klubb, pd.Series(region), pd.Series(source)


# ----------------------------------------------------------------------------- analysis data
def patch(src, old, new, count):
    assert src.count(old) == count, f"patch target found {src.count(old)} times, expected {count}: {old}"
    return src.replace(old, new)


def build_analysis_data():
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    src = (DATA / "07_bygg_analysedata_utvidet.py").read_text()
    src = patch(src, '(karriere["meet_name"].str.contains(pattern, case=False, na=False))', '(karriere["er_lekene"] == 1)', 1)
    src = patch(src, '"meet_id"', '"meet_day"', 4)          # meets counted as competition days
    (SANDBOX / "07_bygg_analysedata_utvidet.py").write_text(src)
    (SANDBOX / "tyrvingtabellen.py").write_text(SHIM.format(analysis=HERE))
    for f in ["kohort_utvidet.csv", "karrieredata_utvidet.csv"]:
        shutil.copy(CDATA / f, SANDBOX / f)
    r = subprocess.run([sys.executable, "07_bygg_analysedata_utvidet.py"], cwd=SANDBOX, capture_output=True, text=True,
                       env={"MPLBACKEND": "Agg", "PATH": "/usr/bin:/bin"})
    (PRIV / "r1_00_build07.log").write_text(r.stdout + r.stderr)
    if r.returncode != 0:
        raise SystemExit(f"07 failed:\n{r.stderr[-3000:]}")
    shutil.copy(SANDBOX / "analysedata_utvidet.csv", CDATA / "analysedata_utvidet.csv")


def main():
    CDATA.mkdir(parents=True, exist_ok=True)
    sb = client()
    old_kar = pd.read_csv(DATA / "karrieredata_utvidet.csv", low_memory=False)
    old_coh = pd.read_csv(DATA / "kohort_utvidet.csv")
    reextract = pd.read_csv(PRIV / "audit_reextract.csv", low_memory=False, usecols=["id", "athlete_id"])

    meets = lekene_meets(sb)
    meets.to_csv(CDATA / "lekene_meets.csv", index=False)
    note("meet records on the venue-days", len(meets))
    coh, lek_ids = participants(sb, meets, old_kar)
    note("cohort (born 1998-2002)", len(coh))

    kar = build_career(sb, coh, old_kar, reextract)
    kar["er_lekene"] = flag_lekene(kar, coh, lek_ids, meets)
    klubb, region, source = region_and_club(kar, coh)
    coh["klubb"] = coh["athlete_id"].map(klubb)
    coh["region"] = coh["athlete_id"].map(region)
    main_city = {"Østlandet": "Jessheim Friidrettsstadion", "Vestlandet": "Osterøy Stadion", "Midt-Norge": "Øverlands Minde"}
    coh["forste_city"] = [("Romerike Friidrettstadion" if (r == "Østlandet" and y <= 2012) else main_city.get(r))
                          for r, y in zip(coh["region"], coh["first_year"])]
    coh = coh[["athlete_id", "gender", "birth_date", "birth_year", "forste_utgave", "forste_city", "region",
               "antall_utgaver", "alle_utgaver", "deltok_begge_aar", "klubb"]]

    # comparison with the original cohort
    j = old_coh.merge(coh, on="athlete_id", how="outer", suffixes=("_orig", ""), indicator=True)
    note("original cohort members confirmed", int((j["_merge"] == "both").sum()))
    note("original cohort members not confirmed (dropped)", int((j["_merge"] == "left_only").sum()))
    note("participants added to the cohort", int((j["_merge"] == "right_only").sum()))
    b = j[j["_merge"] == "both"]
    note("first edition changed", int((b["forste_utgave_orig"] != b["forste_utgave"]).sum()))
    note("region changed", int((b["region_orig"] != b["region"]).sum()))
    note("club changed", int((b["klubb_orig"].fillna("") != b["klubb"].fillna("")).sum()))
    sx = pd.crosstab(b["gender_orig"].fillna("unknown"), b["gender"].fillna("unknown"))
    note("sex: original -> register now", {f"{r}->{c}": int(sx.loc[r, c]) for r in sx.index for c in sx.columns if sx.loc[r, c]})
    note("birth year changed", int((b["birth_year_orig"] != b["birth_year"]).sum()))
    coh.to_csv(CDATA / "kohort_utvidet.csv", index=False)

    base = kar.merge(coh[["athlete_id", "forste_utgave"]], on="athlete_id")
    base = base[(pd.to_datetime(base["date"]).dt.year == base["forste_utgave"].map({v: k for k, v in EDITION.items()}))
                & (base["er_lekene"] == 1)]
    note("cohort members with baseline-meet results in the career data", f"{base['athlete_id'].nunique()} of {len(coh)}")
    md = kar.groupby("meet_id")["date"].nunique()
    ad = kar.groupby(["athlete_id", "date"])["meet_id"].nunique()
    note("meet records spanning more than one date", f"{int((md > 1).sum())} of {len(md):,}")
    note("athlete-days with results under more than one meet record", f"{int((ad > 1).sum()):,} of {len(ad):,}")
    kar.to_csv(CDATA / "karrieredata_utvidet.csv", index=False)
    note("career data rows / athletes", f"{len(kar):,} / {kar['athlete_id'].nunique():,}")

    build_analysis_data()
    df = pd.read_csv(CDATA / "analysedata_utvidet.csv", low_memory=False)
    note("analysis data rows", len(df))
    note("active senior (n, %)", f"{int(df['aktiv_senior'].sum())} ({100 * df['aktiv_senior'].mean():.1f}%)")
    pd.DataFrame(SUMMARY, columns=["Check", "Value"]).to_csv(R1 / "audit" / "r1_00_summary.csv", index=False)


if __name__ == "__main__":
    main()
