"""
Steg 1: Trekk ut karrieredata for NCC/PEAB-kohorten fra Supabase.

Forutsetter at kohort.csv allerede finnes (generert via SQL/MCP).
Produserer: karrieredata.csv — alle resultater for kohort-utøverne.

Bruk: python 01_trekk_data.py [--dry-run]
"""

import os
import csv
import logging
import argparse
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def _find_env():
    """Finn scraper/.env — fungerer både i worktree og vanlig checkout."""
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
KOHORT_FILE = DATA_DIR / "kohort.csv"
KARRIERE_FILE = DATA_DIR / "karrieredata.csv"

KARRIERE_KOLONNER = (
    "id, athlete_id, performance, performance_value, date, "
    "event_id, event_code, event_name, event_category, result_type, "
    "meet_id, meet_name, meet_city, meet_indoor, "
    "season_year, club_name, is_manual_time"
)


def les_kohort_ider():
    """Les athlete_id-er fra kohort.csv."""
    if not KOHORT_FILE.exists():
        raise FileNotFoundError(
            f"{KOHORT_FILE} finnes ikke. Generer den først via Supabase MCP/SQL."
        )
    ids = []
    with open(KOHORT_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.append(row["athlete_id"])
    return ids


def hent_karrieredata(sb, athlete_ids, dry_run=False):
    """Hent alle resultater for gitte utøvere via table API med paginering."""
    logger.info(f"Henter karrieredata for {len(athlete_ids)} utøvere...")

    if dry_run:
        batch = athlete_ids[:10]
        resp = (
            sb.table("results_full")
            .select("id", count="exact")
            .in_("athlete_id", batch)
            .eq("status", "OK")
            .limit(1)
            .execute()
        )
        est = (resp.count or 0) * len(athlete_ids) / len(batch)
        logger.info(f"  Estimert totalt: ~{est:.0f} resultater")
        return []

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
    parser = argparse.ArgumentParser(description="Trekk ut karrieredata for NCC/PEAB-kohort")
    parser.add_argument("--dry-run", action="store_true", help="Bare estimer, ikke last ned")
    args = parser.parse_args()

    athlete_ids = les_kohort_ider()
    logger.info(f"Kohort: {len(athlete_ids)} utøvere fra {KOHORT_FILE}")

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    karriere_rows = hent_karrieredata(sb, athlete_ids, dry_run=args.dry_run)

    if args.dry_run:
        return

    if not karriere_rows:
        logger.warning("Ingen karrieredata funnet!")
        return

    fieldnames = list(karriere_rows[0].keys())
    with open(KARRIERE_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(karriere_rows)

    logger.info(f"Lagret {len(karriere_rows)} rader til {KARRIERE_FILE}")


if __name__ == "__main__":
    main()
