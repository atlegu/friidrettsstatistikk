"""
Backfill birth_date for athletes who only have birth_year.

This is critical for RAE analysis — many athletes were registered in youth
competitions (age 10-11) without birth_date. Those who continued got the
date registered later; those who dropped out did not.

Reuses the UtoverSok.php approach from backfill_birth_years.py to fetch
full birth_date_str for matched athletes and updates the DB only when:
  1. The source has a full DD.MM.YY or DD.MM.YYYY format (not just year)
  2. The parsed year matches existing birth_year in DB (sanity check)

Usage:
    python backfill_birth_dates.py --dry-run        # Sample, no updates
    python backfill_birth_dates.py --letters A B    # Specific letters only
    python backfill_birth_dates.py                   # Full run
"""

import argparse
import os
import re
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, f'backfill_birth_dates_{timestamp}.log')),
    ]
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


def parse_birth_date(date_str: str) -> Optional[str]:
    """Parse birth date to ISO YYYY-MM-DD format. Returns None if no day/month.

    Source uses: DD.MM.YYYY, DD.MM.YY, or just YYYY (no day/month).
    We only return ISO if we have day and month.
    """
    if not date_str:
        return None
    date_str = date_str.strip()

    # Full date: DD.MM.YYYY
    m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', date_str)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= d <= 31 and 1 <= mo <= 12:
            return f"{y:04d}-{mo:02d}-{d:02d}"

    # Short date: DD.MM.YY
    m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{2})$', date_str)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= d <= 31 and 1 <= mo <= 12:
            full_year = 2000 + y if y <= 30 else 1900 + y
            return f"{full_year:04d}-{mo:02d}-{d:02d}"

    # Just YYYY or partial — skip
    return None


def fetch_athletes_for_letter(letter: str) -> List[Dict]:
    """Fetch all athletes starting with a given letter.
    Returns list of {external_id, birth_date_str} dicts.
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

            link = row.find('a', href=lambda h: h and 'UtoverStatistikk' in h)
            if not link:
                continue

            href = link.get('href', '')
            ext_match = re.search(r'showathl=(\d+)', href)
            if not ext_match:
                continue

            external_id = ext_match.group(1)
            birth_text = cells[1].get_text(strip=True) if len(cells) > 1 else ''

            athletes.append({
                'external_id': external_id,
                'birth_date_str': birth_text,
            })

    return athletes


def load_athletes_without_birth_date() -> Dict[str, Dict]:
    """Load athletes with external_id but no birth_date.
    Returns dict: external_id -> {id, birth_year, full_name}
    """
    logger.info("Loading athletes without birth_date (with external_id)...")
    athletes_by_ext_id: Dict[str, Dict] = {}

    offset = 0
    page_size = 1000
    total = 0

    while True:
        response = supabase.table('athletes').select(
            'id, full_name, birth_year, external_id'
        ).is_('birth_date', 'null').not_.is_('external_id', 'null').range(
            offset, offset + page_size - 1
        ).execute()

        if not response.data:
            break

        for a in response.data:
            ext_id = (a.get('external_id') or '').strip()
            if ext_id:
                athletes_by_ext_id[ext_id] = {
                    'id': a['id'],
                    'full_name': a.get('full_name', ''),
                    'birth_year': a.get('birth_year'),
                }
            total += 1

        if len(response.data) < page_size:
            break
        offset += page_size

    logger.info(f"Loaded {total} athletes without birth_date, {len(athletes_by_ext_id)} with external_id")
    return athletes_by_ext_id


def main():
    parser = argparse.ArgumentParser(description='Backfill athlete birth_date')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated')
    parser.add_argument('--letters', nargs='+', help='Only process specific letters')
    args = parser.parse_args()

    letters = args.letters or LETTERS

    athletes_by_ext_id = load_athletes_without_birth_date()
    if not athletes_by_ext_id:
        logger.info("No athletes need birth_date updates!")
        return

    updates: Dict[str, Dict] = {}   # athlete_id -> {birth_date, full_name, source_str}
    total_scraped = 0
    source_only_year = 0
    year_mismatch = 0

    for i, letter in enumerate(letters):
        logger.info(f"[{i+1}/{len(letters)}] Fetching '{letter}'...")
        source_athletes = fetch_athletes_for_letter(letter)
        total_scraped += len(source_athletes)

        matched = 0
        for sa in source_athletes:
            ext_id = sa['external_id']
            if ext_id not in athletes_by_ext_id:
                continue

            iso = parse_birth_date(sa['birth_date_str'])
            if not iso:
                # Source only has year (or nothing)
                source_only_year += 1
                continue

            db_athlete = athletes_by_ext_id[ext_id]
            # Sanity: parsed year must match DB birth_year if present
            parsed_year = int(iso[:4])
            db_year = db_athlete.get('birth_year')
            if db_year is not None and db_year != parsed_year:
                year_mismatch += 1
                logger.debug(f"  Year mismatch {db_athlete['full_name']}: db={db_year}, src={parsed_year}")
                continue

            updates[db_athlete['id']] = {
                'birth_date': iso,
                'full_name': db_athlete['full_name'],
                'source_str': sa['birth_date_str'],
            }
            matched += 1

        logger.info(f"  {len(source_athletes)} athletes scraped, {matched} new dates to update")
        time.sleep(REQUEST_DELAY)

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Backfill summary:")
    logger.info(f"  Total scraped:            {total_scraped}")
    logger.info(f"  Needing birth_date in DB: {len(athletes_by_ext_id)}")
    logger.info(f"  Source has only year:     {source_only_year}")
    logger.info(f"  Year mismatch (skipped):  {year_mismatch}")
    logger.info(f"  Updates ready:            {len(updates)}")
    logger.info("=" * 60)

    if args.dry_run:
        logger.info("\nDRY RUN — sample updates:")
        for aid, info in list(updates.items())[:15]:
            logger.info(f"  {info['full_name']:40} {info['source_str']:12} -> {info['birth_date']}")
        return

    # Apply updates one by one (small enough to be OK; Supabase has no bulk update)
    applied = 0
    errors = 0
    for athlete_id, info in updates.items():
        try:
            supabase.table('athletes').update(
                {'birth_date': info['birth_date']}
            ).eq('id', athlete_id).execute()
            applied += 1
            if applied % 500 == 0:
                logger.info(f"  Applied {applied}/{len(updates)} updates...")
        except Exception as e:
            errors += 1
            logger.debug(f"  Update failed for {info['full_name']}: {e}")

    logger.info("")
    logger.info(f"Applied: {applied}")
    logger.info(f"Errors:  {errors}")


if __name__ == '__main__':
    main()
