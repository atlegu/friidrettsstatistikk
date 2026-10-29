"""
00b_uttrekk_hekk.py — A6-tillegg (Atles forespørsel 29.10.2026): korthekk.

Henter alle resultater 2011-> for de ti korthekk-kodene med reelle vinddata.
Kodene bærer klassespesifikasjonen (distanse + hekkehøyde), så analyse per
kode er analyse per aldersklasse-spesifikasjon. Gjenbruker utovere/meets/
events fra hoveduttrekket i data_private/.

Output: data_private/resultater_hekk.csv (+ oppdatert uttrekksinfo_hekk.json)
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
LOGS.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(LOGS / f"uttrekk_hekk_{datetime.now():%Y%m%d_%H%M%S}.log")],
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv("/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/Statistikk/scraper/.env")
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

KODER = ["60mh_68cm", "60mh_76_2cm", "80mh_76_2cm", "80mh_84cm",
         "100mh_76_2cm", "100mh_84cm", "100mh_91_4cm",
         "110mh_91_4cm", "110mh_100cm", "110mh_106_7cm"]
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
    ev = pd.read_csv(DATA / "events.csv")
    id_per_kode = dict(zip(ev["code"], ev["id"]))
    mangler = [k for k in KODER if k not in id_per_kode]
    if mangler:
        raise SystemExit(f"finner ikke koder: {mangler}")

    info = {"uttrekk_start_utc": datetime.now(timezone.utc).isoformat(),
            "cutoff_dato": CUTOFF_DATO, "koder": KODER}
    ut_path = DATA / "resultater_hekk.csv"
    forste = True
    total = 0
    for kode in KODER:
        eid = id_per_kode[kode]
        rader = []
        for aar in range(2011, 2027):
            til = CUTOFF_DATO if aar == 2026 else f"{aar}-12-31"
            rader.extend(hent_alt(lambda a=aar, t=til: sb.table("results").select(RSEL)
                                  .eq("event_id", eid)
                                  .gte("date", f"{a}-01-01").lte("date", t)))
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
    with open(DATA / "uttrekksinfo_hekk.json", "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    logger.info(f"FERDIG: {total} rader")


if __name__ == "__main__":
    main()
