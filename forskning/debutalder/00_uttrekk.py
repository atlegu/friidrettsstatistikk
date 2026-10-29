"""
00_uttrekk.py — A3 «Debutalder»: frosset uttrekk fra registeret.

Henter alle utøvere født 2001-2008 og alle deres godkjente resultater fra
2011, som RENE DELTAKELSESDATA: utøver, dato, stevne, klubb, status.
Ingen prestasjonskolonner hentes (jf. ANALYSEPLAN.md §3 — ingen nivåanalyse).

Skriver frosne CSV-er til data_private/ (git-ignorert; regenererbart).
Samme uttrekksmønster som A1 (deterministisk paginering på id).
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

KULL_FRA, KULL_TIL = 2001, 2008
CUTOFF_DATO = "2026-10-29"
RSEL = "id,athlete_id,meet_id,club_id,date,status"


def hent_alt(bygg_sporring):
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
        "merknad": "Ren deltakelse: ingen prestasjonskolonner. Levende base per uttrekksdato.",
    }

    utv = pd.DataFrame(hent_alt(lambda: sb.table("athletes")
                                .select("id,gender,birth_year,birth_date")
                                .gte("birth_year", KULL_FRA).lte("birth_year", KULL_TIL)))
    utv.to_csv(DATA / "utovere.csv", index=False)
    info["utovere_fodt_2001_2008"] = len(utv)
    logger.info(f"utøvere født {KULL_FRA}-{KULL_TIL}: {len(utv)}")

    me = pd.DataFrame(hent_alt(lambda: sb.table("meets").select("id,krets,indoor,start_date")))
    me.to_csv(DATA / "meets.csv", index=False)
    kl = pd.DataFrame(hent_alt(lambda: sb.table("clubs").select("id,name")))
    kl.to_csv(DATA / "clubs.csv", index=False)
    logger.info(f"oppslag: {len(me)} meets, {len(kl)} clubs")

    ut_path = DATA / "resultater.csv"
    forste = True
    total = 0
    for aar in range(KULL_FRA, KULL_TIL + 1):
        ids = utv.loc[utv["birth_year"] == aar, "id"].tolist()
        rader = []
        for i in range(0, len(ids), 40):
            batch = ids[i:i + 40]
            rader.extend(hent_alt(lambda b=batch: sb.table("results").select(RSEL)
                                  .in_("athlete_id", b)
                                  .gte("date", "2011-01-01").lte("date", CUTOFF_DATO)))
        d = pd.DataFrame(rader)
        if len(d):
            d.to_csv(ut_path, index=False, mode="w" if forste else "a", header=forste)
            forste = False
        total += len(d)
        info[f"kull_{aar}"] = {"utovere": len(ids), "resultater": len(d)}
        logger.info(f"kull {aar}: {len(ids)} utøvere, {len(d)} resultater (sum {total})")

    info["resultater_totalt"] = total
    info["uttrekk_slutt_utc"] = datetime.now(timezone.utc).isoformat()
    with open(DATA / "uttrekksinfo.json", "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    logger.info(f"FERDIG: {total} resultatrader")


if __name__ == "__main__":
    main()
