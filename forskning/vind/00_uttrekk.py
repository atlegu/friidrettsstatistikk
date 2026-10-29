"""
00_uttrekk.py — A6 «Vind»: frosset uttrekk fra registeret.

Henter ALLE resultater i de ni vindøvelsene (60/80/100/150/200 m, lengde,
lengde sone, tresteg, tresteg sone) fra 2011, med og uten vindverdi (de
uten brukes bare i missingness-beskrivelsen), pluss utøver- og stevneoppslag.
Paginering per øvelse med deterministisk ORDER BY id (A1/A3-mønsteret).

Output i data_private/ (git-ignorert): resultater.csv, utovere.csv,
meets.csv, events.csv, uttrekksinfo.json
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

KODER = ["60m", "80m", "100m", "150m", "200m",
         "lengde", "lengde_sone_05m", "tresteg", "tresteg_sone_05m"]
CUTOFF_DATO = "2026-10-29"
RSEL = ("id,athlete_id,event_id,meet_id,date,performance,performance_value,"
        "wind,is_wind_legal,is_manual_time,status,round")


def hent_alt(bygg_sporring):
    rader, offset = [], 0
    while True:
        res = bygg_sporring().order("id").range(offset, offset + 999).execute()
        rader.extend(res.data)
        if len(res.data) < 1000:
            return rader
        offset += 1000


def main():
    info = {"uttrekk_start_utc": datetime.now(timezone.utc).isoformat(),
            "cutoff_dato": CUTOFF_DATO, "koder": KODER,
            "merknad": "Alle rader i vindøvelsene, med og uten vindverdi; "
                       "levende base per uttrekksdato."}

    ev = pd.DataFrame(hent_alt(lambda: sb.table("events")
                               .select("id,code,name,category,result_type,wind_measured")))
    ev.to_csv(DATA / "events.csv", index=False)
    id_per_kode = dict(zip(ev["code"], ev["id"]))
    mangler = [k for k in KODER if k not in id_per_kode]
    if mangler:
        raise SystemExit(f"finner ikke øvelseskoder: {mangler}")

    utv = pd.DataFrame(hent_alt(lambda: sb.table("athletes").select("id,gender,birth_year")))
    utv.to_csv(DATA / "utovere.csv", index=False)
    logger.info(f"utøvere: {len(utv)}")

    me = pd.DataFrame(hent_alt(lambda: sb.table("meets")
                               .select("id,indoor,krets,level,start_date")))
    me.to_csv(DATA / "meets.csv", index=False)
    logger.info(f"meets: {len(me)}")

    ut_path = DATA / "resultater.csv"
    forste = True
    total = 0
    for kode in KODER:
        eid = id_per_kode[kode]
        rader = hent_alt(lambda: sb.table("results").select(RSEL)
                         .eq("event_id", eid)
                         .gte("date", "2011-01-01").lte("date", CUTOFF_DATO))
        d = pd.DataFrame(rader)
        if len(d):
            d["event_code"] = kode
            d.to_csv(ut_path, index=False, mode="w" if forste else "a", header=forste)
            forste = False
        total += len(d)
        info[f"n_{kode}"] = len(d)
        logger.info(f"{kode}: {len(d)} rader (sum {total})")

    info["resultater_totalt"] = total
    info["uttrekk_slutt_utc"] = datetime.now(timezone.utc).isoformat()
    with open(DATA / "uttrekksinfo.json", "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    logger.info(f"FERDIG: {total} rader")


if __name__ == "__main__":
    main()
