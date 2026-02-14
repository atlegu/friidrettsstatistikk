"""
Backfill birth years for athletes missing them.

Uses the UtoverSok.php (athlete search) on minfriidrettsstatistikk.info
to fetch birth dates for all athletes, then matches by external_id
and updates athletes in the database where birth_year IS NULL.

Usage:
    python backfill_birth_years.py --dry-run        # Show what would be updated
    python backfill_birth_years.py                   # Run the update
"""

import argparse
import json
import os
import re
import time
import logging
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
REQUEST_DELAY = 0.5

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettStats/1.0'
})

LETTERS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ')


def parse_birth_date_to_year(date_str: str) -> Optional[int]:
    """Parse birth date string to year.

    Formats: DD.MM.YYYY, DD.MM.YY, YYYY, DD.0.YYYY, etc.
    """
    if not date_str:
        return None
    date_str = date_str.strip()

    # Full date: DD.MM.YYYY
    m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', date_str)
    if m:
        return int(m.group(3))

    # Short date: DD.MM.YY
    m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{2})$', date_str)
    if m:
        year = int(m.group(3))
        return 2000 + year if year <= 30 else 1900 + year

    # Just year: YYYY
    m = re.match(r'^(\d{4})$', date_str)
    if m:
        return int(m.group(1))

    return None


def fetch_athletes_for_letter(letter: str) -> List[Dict]:
    """Fetch all athletes starting with a given letter.

    Returns list of {external_id, name, birth_year} dicts.
    """
    url = f"{BASE_URL}/UtoverSok.php"
    data = {'cmd': 'SearchAthlete', 'showchar': letter}

    try:
        r = session.post(url, data=data, timeout=60)
        r.raise_for_status()
    except Exception as e:
        logger.warning(f"Failed to fetch letter {letter}: {e}")
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    athletes = []

    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) < 2:
                continue

            # Find link with external ID
            link = row.find('a', href=lambda h: h and 'UtoverStatistikk' in h)
            if not link:
                continue

            href = link.get('href', '')
            ext_match = re.search(r'showathl=(\d+)', href)
            if not ext_match:
                continue

            external_id = ext_match.group(1)
            name_text = cells[0].get_text(strip=True)  # "Lastname, Firstname"
            birth_text = cells[1].get_text(strip=True) if len(cells) > 1 else ''

            birth_year = parse_birth_date_to_year(birth_text)

            athletes.append({
                'external_id': external_id,
                'name_raw': name_text,
                'birth_year': birth_year,
                'birth_date_str': birth_text,
            })

    return athletes


def load_athletes_without_birthyear() -> Dict[str, Dict]:
    """Load all athletes without birth_year that have external_id.

    Returns dict: external_id -> {id, full_name, gender}
    """
    logger.info("Loading athletes without birth_year...")
    athletes_by_ext_id: Dict[str, Dict] = {}

    offset = 0
    page_size = 1000
    total = 0

    while True:
        response = supabase.table('athletes').select(
            'id, full_name, gender, external_id'
        ).is_('birth_year', 'null').not_.is_('external_id', 'null').range(
            offset, offset + page_size - 1
        ).execute()

        if not response.data:
            break

        for a in response.data:
            ext_id = a.get('external_id', '').strip()
            if ext_id:
                athletes_by_ext_id[ext_id] = {
                    'id': a['id'],
                    'full_name': a.get('full_name', ''),
                    'gender': a.get('gender'),
                }
            total += 1

        if len(response.data) < page_size:
            break
        offset += page_size

    logger.info(f"Loaded {total} athletes without birth_year ({len(athletes_by_ext_id)} with external_id)")
    return athletes_by_ext_id


def main():
    parser = argparse.ArgumentParser(description='Backfill athlete birth years')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated')
    parser.add_argument('--letters', nargs='+', help='Only process specific letters')
    args = parser.parse_args()

    letters = args.letters or LETTERS

    # Load athletes needing birth year
    athletes_by_ext_id = load_athletes_without_birthyear()
    if not athletes_by_ext_id:
        logger.info("No athletes need birth_year updates!")
        return

    # Scrape athlete search and match by external_id
    updates = {}  # athlete_db_id -> birth_year
    total_scraped = 0
    no_birth_year_in_source = 0

    for i, letter in enumerate(letters):
        logger.info(f"[{i+1}/{len(letters)}] Fetching athletes starting with '{letter}'...")

        source_athletes = fetch_athletes_for_letter(letter)
        total_scraped += len(source_athletes)

        matched_this_letter = 0
        for sa in source_athletes:
            ext_id = sa['external_id']
            if ext_id in athletes_by_ext_id:
                if sa['birth_year']:
                    db_athlete = athletes_by_ext_id[ext_id]
                    updates[db_athlete['id']] = {
                        'birth_year': sa['birth_year'],
                        'full_name': db_athlete['full_name'],
                    }
                    matched_this_letter += 1
                else:
                    no_birth_year_in_source += 1

        logger.info(f"  {len(source_athletes)} athletes from source, {matched_this_letter} matched to update")
        time.sleep(REQUEST_DELAY)

    logger.info(f"\nScraping complete:")
    logger.info(f"  Total from source: {total_scraped}")
    logger.info(f"  Matched to update: {len(updates)}")
    logger.info(f"  No birth_year in source: {no_birth_year_in_source}")
    logger.info(f"  Remaining unmatched: {len(athletes_by_ext_id) - len(updates) - no_birth_year_in_source}")

    if args.dry_run:
        logger.info("\nDRY RUN — no updates applied. Samples:")
        for aid, info in list(updates.items())[:20]:
            logger.info(f"  {info['full_name']} -> birth_year={info['birth_year']}")
        return

    # Save mapping to JSON file for batch SQL updates
    mapping_file = os.path.join(os.path.dirname(__file__), 'new_meets_data', 'birth_year_mapping.json')
    # Map: athlete_uuid -> birth_year
    mapping = {aid: info['birth_year'] for aid, info in updates.items()}

    with open(mapping_file, 'w') as f:
        json.dump(mapping, f)
    logger.info(f"Saved {len(mapping)} uuid->birth_year mappings to {mapping_file}")
    logger.info("Run with --apply-json to apply the saved mappings via batch SQL")


if __name__ == '__main__':
    main()
