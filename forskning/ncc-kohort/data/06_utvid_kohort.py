"""
Steg 6: Utvid kohorten til 2001-2002 (Bendit-lekene 2015 / Ungdomslekene 2016).

Hele serien av ungdomsleker:
  NCC-lekene 2011-2012 -> PEAB-lekene 2013-2014 -> Bendit-lekene 2015 -> Ungdomslekene 2016
  Alle: Jessheim, Stjørdal/Øverlands Minde, Osterøy.

Produserer: kohort_utvidet.csv, karrieredata_utvidet.csv
"""

import os
import csv
import logging
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def _find_env():
    p = Path(__file__).resolve()
    for ancestor in p.parents:
        candidate = ancestor / "scraper" / ".env"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Fant ikke scraper/.env")

load_dotenv(_find_env())

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

DATA_DIR = Path(__file__).parent
ORIG_KOHORT = DATA_DIR / "kohort.csv"
ORIG_KARRIERE = DATA_DIR / "karrieredata.csv"
UTVIDET_KOHORT = DATA_DIR / "kohort_utvidet.csv"
UTVIDET_KARRIERE = DATA_DIR / "karrieredata_utvidet.csv"

REGION_MAP = {
    "Jessheim Friidrettsstadion": "Østlandet",
    "Jessheim": "Østlandet",
    "Øverlands Minde": "Midt-Norge",
    "Osterøy Stadion": "Vestlandet",
    "Osterøy": "Vestlandet",
}

EDITIONS = {
    "peab_2014": {
        "patterns": ["Peab-lekene", "PEAB-lekene", "peab-lekene"],
        "year": 2014,
    },
    "bendit_2015": {
        "patterns": ["Bendit-lekene"],
        "year": 2015,
    },
    "ungdomslekene_2016": {
        "patterns": ["Ungdomslekene"],
        "year": 2016,
    },
}

NCC_PEAB_EDITIONS = {
    "ncc_2011": 2011, "ncc_2012": 2012,
    "peab_2013": 2013, "peab_2014": 2014,
    "bendit_2015": 2015, "ungdomslekene_2016": 2016,
}

KARRIERE_KOLONNER = (
    "id, athlete_id, performance, performance_value, date, "
    "event_id, event_code, event_name, event_category, result_type, "
    "meet_id, meet_name, meet_city, meet_indoor, "
    "season_year, club_name, is_manual_time"
)


def hent_nye_utovere(sb):
    """Hent 2001-2002 utøvere fra extended editions."""
    logger.info("Henter utøvere født 2001-2002 fra ungdomslekene...")

    utovere = {}  # aid -> {data, editions set}

    for utgave_key, config in EDITIONS.items():
        stevne_aar = config["year"]
        for pattern in config["patterns"]:
            logger.info(f"  Søker {utgave_key}: '{pattern}'...")
            offset = 0
            batch_count = 0
            while True:
                resp = (
                    sb.table("results_full")
                    .select("athlete_id, gender, birth_date, meet_city, club_name")
                    .ilike("meet_name", f"%{pattern}%")
                    .gte("date", f"{stevne_aar}-08-01")
                    .lte("date", f"{stevne_aar}-10-31")
                    .range(offset, offset + 999)
                    .execute()
                )
                for row in resp.data:
                    aid = row["athlete_id"]
                    bd = row.get("birth_date") or ""
                    if len(bd) >= 4:
                        by = int(bd[:4])
                    else:
                        continue
                    if by not in (2001, 2002):
                        continue

                    if aid not in utovere:
                        region = REGION_MAP.get(row.get("meet_city"), None)
                        utovere[aid] = {
                            "athlete_id": aid,
                            "gender": row.get("gender"),
                            "birth_date": bd,
                            "birth_year": by,
                            "forste_utgave": utgave_key,
                            "region": region,
                            "deltok_begge_aar": 0,
                            "klubb": row.get("club_name"),
                            "_editions": {stevne_aar},
                        }
                    else:
                        utovere[aid]["_editions"].add(stevne_aar)
                        if region and not utovere[aid]["region"]:
                            utovere[aid]["region"] = region

                batch_count += len(resp.data)
                if len(resp.data) < 1000:
                    break
                offset += 1000
            logger.info(f"    -> {batch_count} rader")

    for aid, data in utovere.items():
        if len(data["_editions"]) >= 2:
            data["deltok_begge_aar"] = 1
        earliest = min(data["_editions"])
        for key, cfg in EDITIONS.items():
            if cfg["year"] == earliest:
                data["forste_utgave"] = key
                break
        del data["_editions"]

    logger.info(f"Totalt {len(utovere)} unike utøvere født 2001-2002")
    by_counts = defaultdict(int)
    for d in utovere.values():
        by_counts[d["birth_year"]] += 1
    for by, n in sorted(by_counts.items()):
        logger.info(f"  f. {by}: {n} utøvere")

    return list(utovere.values())


def hent_karrieredata(sb, athlete_ids):
    """Hent alle resultater for gitte utøvere."""
    logger.info(f"Henter karrieredata for {len(athlete_ids)} nye utøvere...")
    alle_rader = []
    batch_size = 50

    for i in range(0, len(athlete_ids), batch_size):
        batch = athlete_ids[i : i + batch_size]
        if i % 200 == 0:
            logger.info(f"  Utøvere {i}/{len(athlete_ids)} — {len(alle_rader)} resultater hittil")

        offset = 0
        while True:
            resp = (
                sb.table("results_full")
                .select(KARRIERE_KOLONNER)
                .in_("athlete_id", batch)
                .eq("status", "OK")
                .order("date")
                .range(offset, offset + 999)
                .execute()
            )
            alle_rader.extend(resp.data)
            if len(resp.data) < 1000:
                break
            offset += 1000

    logger.info(f"  Hentet totalt {len(alle_rader)} resultater")
    return alle_rader


def main():
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    nye = hent_nye_utovere(sb)
    if not nye:
        logger.error("Fant ingen nye utøvere!")
        return

    # Les original kohort
    orig_kohort = []
    orig_ids = set()
    with open(ORIG_KOHORT, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            orig_kohort.append(row)
            orig_ids.add(row["athlete_id"])

    nye_clean = [r for r in nye if r["athlete_id"] not in orig_ids]
    logger.info(f"Original: {len(orig_kohort)}, nye (etter dedup): {len(nye_clean)}, totalt: {len(orig_kohort) + len(nye_clean)}")

    # Skriv utvidet kohort
    with open(UTVIDET_KOHORT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in orig_kohort:
            writer.writerow(row)
        for row in nye_clean:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    logger.info(f"Utvidet kohort: {len(orig_kohort) + len(nye_clean)} -> {UTVIDET_KOHORT}")

    # Hent karrieredata for nye
    nye_ids = [r["athlete_id"] for r in nye_clean]
    nye_karriere = hent_karrieredata(sb, nye_ids)

    # Les original karrieredata og kombiner
    with open(ORIG_KARRIERE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        karriere_fields = reader.fieldnames
        orig_karriere_rows = list(reader)

    with open(UTVIDET_KARRIERE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=karriere_fields)
        writer.writeheader()
        for row in orig_karriere_rows:
            writer.writerow(row)
        for row in nye_karriere:
            writer.writerow({k: row.get(k, "") for k in karriere_fields})

    total_karriere = len(orig_karriere_rows) + len(nye_karriere)
    logger.info(f"Utvidet karriere: {total_karriere} rader -> {UTVIDET_KARRIERE}")


if __name__ == "__main__":
    main()
