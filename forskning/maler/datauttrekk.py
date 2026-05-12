"""
Mal for datauttrekk fra friidrett.live (Supabase).

Bruk:
    cd forskning/<prosjektnavn>
    cp ../maler/datauttrekk.py data/uttrekk.py
    # Tilpass query og output
    python data/uttrekk.py
"""

import os
import csv
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Konfigurasjon ---

# Last .env fra scraper-mappen (eller sett SUPABASE_URL/SUPABASE_SERVICE_KEY manuelt)
ENV_PATH = Path(__file__).resolve().parents[2] / "scraper" / ".env"
load_dotenv(ENV_PATH)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

OUTPUT_DIR = Path(__file__).parent
OUTPUT_FILE = OUTPUT_DIR / "datasett.csv"


def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def hent_data(supabase):
    """
    Tilpass denne funksjonen til ditt datauttrekk.

    Eksempler på vanlige uttrekk:

    1. Alle 100m-resultater for senior menn, elektronisk tidtaking:
        query = supabase.rpc("get_all_time_best", {
            "p_event_code": "100m",
            "p_gender": "M",
            "p_manual": False,
        })

    2. Via results_full-viewet med filtre:
        query = (
            supabase.table("results_full")
            .select("*")
            .eq("event_code", "100m")
            .eq("gender", "M")
            .gte("date", "2015-01-01")
            .eq("status", "OK")
            .order("performance_value")
            .limit(10000)
        )

    3. Rå SQL via postgrest (for komplekse joins):
        Se Supabase docs for RPC-funksjoner.
    """

    # --- TILPASS HERFRA ---

    query = (
        supabase.table("results_full")
        .select(
            "athlete_id, athlete_name, gender, birth_date, age_group, "
            "event_code, event_name, result_type, "
            "performance, performance_value, wind, is_manual_time, is_wind_legal, "
            "date, meet_name, meet_city, meet_indoor, meet_level, "
            "club_name, season_year"
        )
        .eq("event_code", "100m")
        .eq("gender", "M")
        .eq("status", "OK")
        .gte("date", "2015-01-01")
        .order("performance_value")
        .limit(10000)
    )

    # --- TIL HIT ---

    logger.info("Henter data fra Supabase...")
    response = query.execute()
    logger.info(f"Hentet {len(response.data)} rader")
    return response.data


def lagre_csv(data, output_path):
    if not data:
        logger.warning("Ingen data å lagre")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = data[0].keys()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    logger.info(f"Lagret {len(data)} rader til {output_path}")


def main():
    supabase = get_supabase()
    data = hent_data(supabase)
    lagre_csv(data, OUTPUT_FILE)


if __name__ == "__main__":
    main()
