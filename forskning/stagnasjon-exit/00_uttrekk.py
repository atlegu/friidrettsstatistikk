"""
00_uttrekk.py — A1 «Stagnasjon før exit»: frosset uttrekk fra registeret.

Henter alle utøvere født 1998-2006 og alle deres resultater fra og med
kalenderåret de fylte 13 (registeret er komplett fra 2011), med øvelseskode,
kategori og resultattype innbakt. Beholder utøvere med minst ett OK-resultat
ved kalenderårsalder 13-14; øvrige telles i flytdiagrammet. Skriver frosne
CSV-er til data_private/ (git-ignorert; regenererbart fra basen).

Se ANALYSEPLAN.md: uttrekket fryses FØR noen eksponering-utfall-modell kjøres.
Kjøres én gang; en ny kjøring overskriver og skal i så fall dokumenteres.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

HERE = Path(__file__).parent
DATA = HERE / "data_private"
LOGS = HERE / "logs"
DATA.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(LOGS / f"uttrekk_{datetime.now():%Y%m%d_%H%M%S}.log")],
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/.env")
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

KULL_FRA, KULL_TIL = 1998, 2006   # 2006 brukes bare for sekundærutfallet aktiv ved >=18
CUTOFF_DATO = "2026-10-29"        # resultater t.o.m. denne datoen
RSEL = ("id,athlete_id,meet_id,club_id,date,performance,performance_value,wind,"
        "is_wind_legal,is_manual_time,status,round,events(code,category,result_type)")


def hent_alt(bygg_sporring):
    """Deterministisk paginering: ORDER BY id, 1000 rader per side (jf. audit_01 i IJSSC-arbeidet)."""
    rader, offset = [], 0
    while True:
        res = bygg_sporring().order("id").range(offset, offset + 999).execute()
        rader.extend(res.data)
        if len(res.data) < 1000:
            return rader
        offset += 1000


def main():
    info = {
        "uttrekk_start_utc": datetime.now(timezone.utc).isoformat(),
        "cutoff_dato": CUTOFF_DATO,
        "kull": [KULL_FRA, KULL_TIL],
        "merknad": "Levende base per uttrekksdato (etter dublettoppryddingen okt. 2026); "
                   "created_at-filtre gjenskaper ikke historiske tilstander og brukes ikke.",
    }

    # 1) Utøvere
    utv = pd.DataFrame(hent_alt(lambda: sb.table("athletes")
                                .select("id,gender,birth_year,birth_date")
                                .gte("birth_year", KULL_FRA).lte("birth_year", KULL_TIL)))
    utv.to_csv(DATA / "utovere.csv", index=False)
    info["utovere_fodt_1998_2006"] = len(utv)
    logger.info(f"utøvere født {KULL_FRA}-{KULL_TIL}: {len(utv)}")

    # 2) Oppslagstabeller
    ev = pd.DataFrame(hent_alt(lambda: sb.table("events")
                               .select("id,code,name,category,result_type,wind_measured")))
    ev.to_csv(DATA / "events.csv", index=False)
    me = pd.DataFrame(hent_alt(lambda: sb.table("meets").select("id,krets,indoor,start_date")))
    me.to_csv(DATA / "meets.csv", index=False)
    kl = pd.DataFrame(hent_alt(lambda: sb.table("clubs").select("id,name")))
    kl.to_csv(DATA / "clubs.csv", index=False)
    logger.info(f"oppslag: {len(ev)} events, {len(me)} meets, {len(kl)} clubs")

    # 3) Resultater per kull, fra året utøveren fylte 13
    raa_path = DATA / "resultater_raa.csv"
    forste = True
    for aar in range(KULL_FRA, KULL_TIL + 1):
        ids = utv.loc[utv["birth_year"] == aar, "id"].tolist()
        start = f"{aar + 13}-01-01"
        rader = []
        for i in range(0, len(ids), 40):
            batch = ids[i:i + 40]
            rader.extend(hent_alt(lambda b=batch: sb.table("results").select(RSEL)
                                  .in_("athlete_id", b)
                                  .gte("date", start).lte("date", CUTOFF_DATO)))
        d = pd.DataFrame(rader)
        if len(d):
            evn = pd.json_normalize(d["events"]).rename(
                columns={"code": "event_code", "category": "event_category"})
            d = pd.concat([d.drop(columns="events"), evn], axis=1)
            d.to_csv(raa_path, index=False, mode="w" if forste else "a", header=forste)
            forste = False
        info[f"kull_{aar}"] = {"utovere": len(ids), "resultater_13plus": len(d)}
        logger.info(f"kull {aar}: {len(ids)} utøvere, {len(d)} resultater fra {start}")

    # 4) Flyt-telling og endelig fil: utøvere med >=1 OK-resultat ved 13-14
    r = pd.read_csv(raa_path, parse_dates=["date"])
    r = r.merge(utv[["id", "birth_year"]].rename(columns={"id": "athlete_id"}),
                on="athlete_id", how="left")
    r["alder"] = r["date"].dt.year - r["birth_year"]
    info["resultater_raa"] = len(r)
    info["resultater_ikke_godkjent"] = int((r["status"] == "IKKE_GODKJENT").sum())
    info["resultater_status_nm"] = int((r["status"] == "NM").sum())

    ok1314 = set(r.loc[(r["status"] == "OK") & (r["alder"].isin([13, 14])), "athlete_id"])
    info["utovere_med_ok_resultat_13_14"] = len(ok1314)
    endelig = r[r["athlete_id"].isin(ok1314)].drop(columns=["alder"])
    endelig.to_csv(DATA / "resultater.csv", index=False)
    info["resultater_endelig"] = len(endelig)
    info["uttrekk_slutt_utc"] = datetime.now(timezone.utc).isoformat()

    with open(DATA / "uttrekksinfo.json", "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    logger.info(f"FERDIG: {len(ok1314)} utøvere med OK-resultat ved 13-14, "
                f"{len(endelig)} resultater i resultater.csv")


if __name__ == "__main__":
    main()
