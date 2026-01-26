"""
Incremental scraper for minfriidrettsstatistikk.info
Only scrapes NEW meets that are not already in the database.
Focuses on recent meets (from December 15, 2025 onwards).
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import re
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
OUTPUT_DIR = Path(__file__).parent / "new_meets_data"
OUTPUT_DIR.mkdir(exist_ok=True)
REQUEST_DELAY = 0.3  # seconds between requests
MIN_DATE = datetime(2025, 12, 15)  # Only scrape meets from this date onwards

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Service role for admin operations

# Session for requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettLive/1.0'
})


def get_supabase_client() -> Optional[Client]:
    """Create Supabase client if credentials available"""
    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None


def fetch_page(url: str, method: str = 'GET', data: dict = None) -> Optional[str]:
    """Fetch a page with rate limiting"""
    time.sleep(REQUEST_DELAY)
    try:
        if method == 'POST':
            response = session.post(url, data=data, timeout=30)
        else:
            response = session.get(url, params=data, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date from DD.MM.YYYY or DD.MM.YY format"""
    if not date_str:
        return None
    try:
        date_str = date_str.strip()
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            return datetime(year, int(month), int(day))
    except:
        pass
    return None


def format_date(dt: datetime) -> str:
    """Format date as YYYY-MM-DD"""
    return dt.strftime('%Y-%m-%d')


def fetch_meets_from_source(season: int = 2026, outdoor: str = 'N') -> List[Dict]:
    """Fetch all meets from minfriidrettsstatistikk.info for a season"""
    logger.info(f"Fetching meet list for season {season}, outdoor={outdoor}...")

    url = f"{BASE_URL}/Stevner.php"
    params = {'outdoor': outdoor, 'showseason': season}

    html = fetch_page(url, data=params)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    meets = []

    # Find all links with javascript:void posttoresultlist()
    for link in soup.find_all('a', href=re.compile(r'posttoresultlist')):
        # Extract meet ID from javascript:void posttoresultlist(12345)
        href = link.get('href', '')
        match = re.search(r'posttoresultlist\((\d+)\)', href)
        if not match:
            continue

        meet_id = int(match.group(1))
        meet_name = link.get_text(strip=True)

        # Find parent row to get date and location
        parent_row = link.find_parent('tr')
        if not parent_row:
            continue

        cells = parent_row.find_all('td')
        if len(cells) < 4:
            continue

        # Structure: Date | Name | Arena | Location
        date_str = cells[0].get_text(strip=True)
        arena = cells[2].get_text(strip=True) if len(cells) > 2 else ''
        location = cells[3].get_text(strip=True) if len(cells) > 3 else ''

        meet_date = parse_date(date_str)
        if not meet_date:
            continue

        # Skip meets before our minimum date
        if meet_date < MIN_DATE:
            continue

        meets.append({
            'external_id': meet_id,
            'name': meet_name,
            'date': format_date(meet_date),
            'date_obj': meet_date,
            'arena': arena,
            'location': location,
            'outdoor': outdoor == 'Y'
        })

    logger.info(f"Found {len(meets)} meets from {MIN_DATE.strftime('%Y-%m-%d')} onwards")
    return meets


def get_existing_meets_from_db() -> List[Dict]:
    """Get existing meets from Supabase database with result counts"""
    supabase = get_supabase_client()
    if not supabase:
        logger.warning("No Supabase connection - will output to files only")
        return []

    try:
        # Get meets from December 15, 2025 onwards
        result = supabase.table('meets').select(
            'id, name, city, start_date'
        ).gte('start_date', '2025-12-15').execute()

        meets = []
        for m in result.data:
            # Get result count for this meet
            count_result = supabase.table('results').select(
                'id', count='exact'
            ).eq('meet_id', m['id']).execute()

            meets.append({
                'id': m['id'],
                'name': m['name'],
                'city': m['city'],
                'date': m['start_date'],
                'result_count': count_result.count or 0
            })

        logger.info(f"Found {len(meets)} existing meets in database")
        return meets
    except Exception as e:
        logger.error(f"Error fetching from database: {e}")
        return []


def normalize_meet_name(name: str) -> str:
    """Normalize meet name for comparison"""
    # Remove common prefixes like city names
    name = name.lower().strip()
    # Remove special characters
    name = re.sub(r'[^\w\s]', '', name)
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name


MIN_RESULTS_THRESHOLD = 10  # Meets with fewer results are considered incomplete


def find_missing_meets(source_meets: List[Dict], db_meets: List[Dict]) -> List[Dict]:
    """Find meets that are missing or have too few results in database"""

    # Create lookup dict from database meets (includes result count)
    db_lookup = {}
    for m in db_meets:
        # Create key from normalized name + date
        key = (normalize_meet_name(m['name']), m['date'])
        db_lookup[key] = m.get('result_count', 0)

        # Also add without city prefix (e.g., "Bærum, Nyttårsstevnet" -> "Nyttårsstevnet")
        if ',' in m['name']:
            short_name = m['name'].split(',', 1)[1].strip()
            db_lookup[(normalize_meet_name(short_name), m['date'])] = m.get('result_count', 0)

    missing = []
    incomplete = []

    for m in source_meets:
        key = (normalize_meet_name(m['name']), m['date'])
        full_key = (normalize_meet_name(f"{m['location']}, {m['name']}"), m['date'])

        # Check if meet exists
        result_count = db_lookup.get(key) or db_lookup.get(full_key)

        if result_count is None:
            # Meet doesn't exist at all
            missing.append(m)
        elif result_count < MIN_RESULTS_THRESHOLD:
            # Meet exists but has too few results - needs re-scraping
            incomplete.append(m)
            logger.info(f"  Incomplete meet: {m['name']} ({m['date']}) - only {result_count} results")

    logger.info(f"Found {len(missing)} missing meets and {len(incomplete)} incomplete meets")

    # Return both missing and incomplete meets
    return missing + incomplete


def fetch_meet_results(meet_id: int) -> Optional[str]:
    """Fetch results page for a specific meet"""
    url = f"{BASE_URL}/StevneResultater.php"
    data = {'competition': meet_id}
    return fetch_page(url, method='POST', data=data)


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str]]:
    """Parse result and wind from formats like '9,17(+0,9)'"""
    if not result_str:
        return '', None

    result_str = result_str.strip()

    # Check for wind in parentheses
    match = re.match(r'(.+?)\(([+-]?\d+[,.]?\d*)\)$', result_str)
    if match:
        return match.group(1).strip(), match.group(2).replace(',', '.')

    return result_str, None


def parse_meet_results(html: str, meet: Dict) -> List[Dict]:
    """Parse results from meet results page"""
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    results = []

    current_event = None
    current_class = None

    # Process all elements in order
    for element in soup.find_all(['div', 'table']):
        # Check for class header (e.g., "Menn Senior", "Kvinner U20")
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                current_class = h2.get_text(strip=True)

        # Check for event header (e.g., "60 meter", "Høyde")
        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)

        # Parse result table
        # Structure: PLASSERING | RESULTAT | NAVN | KLUBB
        elif element.name == 'table' and current_event:
            rows = element.find_all('tr')

            for row in rows:
                # Skip header row
                if row.find('th'):
                    continue

                cells = row.find_all('td')
                if len(cells) < 4:
                    continue

                try:
                    # Column structure: PLASSERING | RESULTAT | NAVN | KLUBB
                    place_text = cells[0].get_text(strip=True)
                    result_raw = cells[1].get_text(strip=True)
                    name_text = cells[2].get_text(strip=True)
                    club = cells[3].get_text(strip=True)

                    # Parse place (can be "1", "2-h3", "DNS", etc.)
                    place = None
                    place_match = re.match(r'^(\d+)', place_text)
                    if place_match:
                        place = int(place_match.group(1))

                    # Parse result and wind
                    result, wind = parse_result_wind(result_raw)

                    # Parse name and birth year
                    # Format: "Herman Sandor Baranyi-Berge(2003)"
                    name = name_text
                    birth_year = None
                    year_match = re.search(r'\((\d{4})\)$', name_text)
                    if year_match:
                        birth_year = int(year_match.group(1))
                        name = name_text[:year_match.start()].strip()

                    # Skip invalid rows
                    if not name or not result:
                        continue

                    # Skip DNS, DNF, DQ, etc.
                    if result.upper() in ['DNS', 'DNF', 'DQ', 'NM', '-']:
                        continue

                    results.append({
                        'meet_external_id': meet['external_id'],
                        'meet_name': meet['name'],
                        'meet_date': meet['date'],
                        'event': current_event,
                        'event_class': current_class,
                        'place': place,
                        'athlete_name': name,
                        'birth_year': birth_year,
                        'club': club,
                        'result': result.replace(',', '.'),
                        'wind': wind,
                        'is_indoor': not meet['outdoor']
                    })
                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue

    return results


def scrape_missing_meets(missing_meets: List[Dict]) -> List[Dict]:
    """Scrape results for all missing meets"""
    all_results = []

    for i, meet in enumerate(missing_meets):
        logger.info(f"Scraping {i+1}/{len(missing_meets)}: {meet['name']} ({meet['date']})")

        html = fetch_meet_results(meet['external_id'])
        if html:
            results = parse_meet_results(html, meet)
            all_results.extend(results)
            logger.info(f"  Found {len(results)} results")
        else:
            logger.warning(f"  Failed to fetch results")

    return all_results


def save_results_to_csv(results: List[Dict], filename: str):
    """Save results to CSV file"""
    if not results:
        logger.info("No results to save")
        return

    filepath = OUTPUT_DIR / filename
    fieldnames = [
        'meet_external_id', 'meet_name', 'meet_date', 'event', 'event_class',
        'place', 'athlete_name', 'birth_year', 'club', 'result', 'wind', 'is_indoor'
    ]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    logger.info(f"Saved {len(results)} results to {filepath}")


def save_meets_to_json(meets: List[Dict], filename: str):
    """Save meets list to JSON"""
    filepath = OUTPUT_DIR / filename
    # Remove date_obj before saving
    clean_meets = [{k: v for k, v in m.items() if k != 'date_obj'} for m in meets]

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(clean_meets, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(meets)} meets to {filepath}")


def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Starting incremental meet scraper")
    logger.info(f"Looking for meets from {MIN_DATE.strftime('%Y-%m-%d')} onwards")
    logger.info("=" * 60)

    # Step 1: Fetch meets from source
    source_meets = fetch_meets_from_source(season=2026, outdoor='N')  # Indoor 2026
    save_meets_to_json(source_meets, 'source_meets.json')

    # Step 2: Get existing meets from database
    db_meets = get_existing_meets_from_db()

    # Step 3: Find missing meets
    if db_meets:
        missing_meets = find_missing_meets(source_meets, db_meets)
    else:
        # If no database connection, show all meets
        logger.info("No database connection - showing all source meets")
        missing_meets = source_meets

    save_meets_to_json(missing_meets, 'missing_meets.json')

    if not missing_meets:
        logger.info("No missing meets found - database is up to date!")
        return

    # Step 4: Scrape results for missing meets
    logger.info(f"\nScraping results for {len(missing_meets)} missing meets...")
    results = scrape_missing_meets(missing_meets)

    # Step 5: Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_results_to_csv(results, f'new_results_{timestamp}.csv')

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Source meets (from {MIN_DATE.strftime('%Y-%m-%d')}): {len(source_meets)}")
    logger.info(f"Existing in database: {len(db_meets)}")
    logger.info(f"Missing meets scraped: {len(missing_meets)}")
    logger.info(f"Total new results: {len(results)}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
