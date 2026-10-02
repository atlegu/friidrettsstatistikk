"""
01_uttrekk.py - Henter alle resultater for 13-14-årslekene fra 2012 og fram til i dag
fra Supabase og lagrer et deduplisert analysedatasett (ett resultat per utøver x
øvelse x år). Serien: NCC (2012), PEAB (2013-14), Bendit (2015), Ungdomslekene (2016),
Lerøy (2017-2025), Extra-lekene (2026-). Extralekene på Ålgård i juni (KM Rogaland)
er et annet stevne og holdes utenfor via måned.

Kjør:  scraper/venv/bin/python forskning/lekene-trend/01_uttrekk.py
Ut:    forskning/lekene-trend/data/lekene.csv
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

HERE = Path(__file__).parent
import sys; sys.path.insert(0, str(HERE))
from felles import DATAFIL, START_AAR, manuell_presisjon, parse_verdi
ROOT = HERE.parent.parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)
(HERE / "logs").mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(HERE / "logs" / f"uttrekk_{datetime.now():%Y%m%d_%H%M%S}.log"))

load_dotenv(ROOT / "scraper" / ".env")
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def serie_meets() -> pd.DataFrame:
    """Alle stevnerader i serien (NCC/PEAB/Bendit/Ungdomslekene/Lerøy/Extra), 2012 til i dag."""
    q = (sb.table("meets").select("id,name,city,start_date")
         .gte("start_date", f"{START_AAR}-01-01").lte("start_date", datetime.now().strftime("%Y-%m-%d"))
         .or_("name.ilike.%ncc%lek%,name.ilike.%peab%lek%,name.ilike.%bendit%lek%,"
              "name.ilike.%lerøy%,name.ilike.%leroy%,name.ilike.%ungdomslekene%,name.ilike.%extra%lek%"))
    m = pd.DataFrame(q.execute().data)
    m["start_date"] = pd.to_datetime(m["start_date"])
    m["yr"] = m["start_date"].dt.year
    name = m["name"].str.lower()
    keep = (
        ~name.str.contains("naperville|nattstevne|stavstevne|kvalifisering|oppkjøring|samling", regex=True)
        & (
            name.str.contains(r"(?:ncc|peab|bendit)[- ]?lek", regex=True)
            | name.str.contains("lerøy|leroy", regex=True)
            | (name.str.contains("ungdomslekene")
               & m["start_date"].between("2016-08-26", "2016-08-29"))
            # Extra-lekene fra 2026 (august/september); Extralekene på Ålgård i juni er KM Rogaland
            | (name.str.contains(r"extra[- ]?lek", regex=True)
               & (m["yr"] >= 2026) & m["start_date"].dt.month.isin([8, 9]))
        )
    )
    m = m[keep].copy()
    logger.info(f"Serie: {len(m)} stevnerader, år {sorted(m['yr'].unique().tolist())}")
    for yr, g in m.groupby("yr"):
        logger.info(f"  {yr}: " + "; ".join(f"{n} ({c}, {d:%d.%m})" for n, c, d in
                                            zip(g["name"], g["city"], g["start_date"])))
    return m


def fetch_results(meet_ids: list[str]) -> pd.DataFrame:
    """Resultater for gitte stevner med utøver-, øvelses- og stevneinfo (paginert)."""
    out, page, size = [], 0, 1000
    sel = ("id,athlete_id,event_id,meet_id,performance,performance_value,date,wind,"
           "is_wind_legal,is_manual_time,round,place,"
           "athletes(gender,birth_date,birth_year),events(code,name,result_type,category),"
           "meets(city,start_date)")
    while True:
        res = (sb.table("results").select(sel).in_("meet_id", meet_ids)
               .range(page * size, (page + 1) * size - 1).execute())
        out.extend(res.data)
        logger.info(f"  side {page}: {len(res.data)} rader (totalt {len(out)})")
        if len(res.data) < size:
            break
        page += 1
    return pd.DataFrame(out)


def flatten(df: pd.DataFrame) -> pd.DataFrame:
    a = pd.json_normalize(df["athletes"]).add_prefix("a_")
    e = pd.json_normalize(df["events"]).add_prefix("e_")
    m = pd.json_normalize(df["meets"]).add_prefix("m_")
    d = pd.concat([df.drop(columns=["athletes", "events", "meets"]).reset_index(drop=True),
                   a, e, m], axis=1)
    d["m_start_date"] = pd.to_datetime(d["m_start_date"])
    d["yr"] = d["m_start_date"].dt.year
    d["klasse"] = d["yr"] - d["a_birth_year"]
    d["a_birth_date"] = pd.to_datetime(d["a_birth_date"], errors="coerce")
    d["alder_dager"] = (d["m_start_date"] - d["a_birth_date"]).dt.days
    d["alder_aar"] = d["alder_dager"] / 365.25
    d["fodt_kvartal"] = d["a_birth_date"].dt.quarter
    return d


def dedup_best(d: pd.DataFrame) -> pd.DataFrame:
    """Ett resultat per utøver x øvelse x år: beste (lavest tid / høyest mål),
    elektronisk foran manuell tid. Sorterer på tolket `verdi`, ikke på
    performance_value (som er feil for M.SS-rader i kilden)."""
    d = d[d["verdi"].notna() & (d["verdi"] > 0)].copy()
    d["_sort"] = d["verdi"] * d["e_result_type"].eq("time").map({True: 1, False: -1})
    d = (d.sort_values(["manuell", "_sort"])
          .drop_duplicates(["athlete_id", "e_code", "yr"], keep="first"))
    return d.drop(columns="_sort")


def main():
    meets = serie_meets()
    ids = meets["id"].tolist()
    raw = pd.DataFrame()
    for i in range(0, len(ids), 40):
        raw = pd.concat([raw, fetch_results(ids[i:i + 40])], ignore_index=True)
    logger.info(f"Rå resultater: {len(raw)}")
    d = flatten(raw)
    d = d[d["klasse"].isin([13, 14])].copy()
    logger.info(f"13-14-åringer: {len(d)} rader, {d['athlete_id'].nunique()} utøvere")
    # Slå sammen kappgang-kodene før dedup, ellers overlever samme resultat under to koder
    d["e_code"] = d["e_code"].replace({"1000mg": "kappgang_1000_m"})
    d["e_name"] = d["e_name"].where(d["e_code"] != "kappgang_1000_m", "Kappgang 1000 meter")
    d["verdi"] = [parse_verdi(p, c, r) for p, c, r in zip(d["performance"], d["e_code"], d["e_result_type"])]
    d["manuell"] = d["is_manual_time"].eq(True) | pd.Series(
        [manuell_presisjon(p, c) for p, c in zip(d["performance"], d["e_code"])], index=d.index)
    mss = (d["e_result_type"].eq("time") & ~d["performance"].astype(str).str.contains(":")
           & (d["verdi"] >= 60))
    logger.info(f"Tolket {int(mss.sum())} M.SS-tider som minutter.sekunder; "
                f"{int(d['manuell'].sum())} manuelle tider (flagg eller tideler i sprint/hekk)")
    d = dedup_best(d)
    d["sex"] = d["a_gender"].map({"M": "G", "F": "J"})
    d["klasse_kjonn"] = d["sex"] + d["klasse"].astype(str)
    cols = ["yr", "m_city", "m_start_date", "athlete_id", "sex", "klasse", "klasse_kjonn",
            "a_birth_date", "a_birth_year", "alder_dager", "alder_aar", "fodt_kvartal",
            "e_code", "e_name", "e_result_type", "e_category",
            "performance", "verdi", "manuell", "performance_value", "wind", "is_wind_legal",
            "is_manual_time", "round", "place"]
    d = d[cols].rename(columns={"m_city": "arena", "m_start_date": "dato",
                                "e_code": "ovelse", "e_name": "ovelse_navn",
                                "e_result_type": "resultattype", "e_category": "kategori",
                                "a_birth_date": "fodselsdato", "a_birth_year": "fodselsaar"})
    d = d.sort_values(["yr", "ovelse", "klasse_kjonn", "performance_value"])
    out = DATA / DATAFIL
    d.to_csv(out, index=False)
    logger.info(f"Lagret {len(d)} dedupliserte resultater, {d['athlete_id'].nunique()} utøvere -> {out}")
    logger.info("\n" + d.groupby("yr")["athlete_id"].nunique().to_string())


if __name__ == "__main__":
    main()
