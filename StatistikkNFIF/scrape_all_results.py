"""
Main scraper for Norwegian Athletics Statistics
Fetches ALL results for ALL athletes and exports to CSV for Supabase import
"""

import requests
import json
import csv
import os
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrape.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
OUTPUT_DIR = "scraped_data"
ATHLETE_IDS_FILE = "athlete_search_html/_all_athlete_ids.json"
DELAY_BETWEEN_REQUESTS = 0.2  # seconds
BATCH_SIZE = 1000  # Save progress every N athletes

os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_athlete_results(athlete_id: int) -> str:
    """Fetch ALL results for an athlete"""
    url = "https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php"

    data = {
        "athlete": athlete_id,
        "type": "RES"  # All results
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    response = requests.post(url, data=data, headers=headers, timeout=30)
    response.encoding = 'utf-8'

    return response.text


def parse_date(date_str: str) -> Optional[str]:
    """Parse date from DD.MM.YY format to YYYY-MM-DD"""
    if not date_str:
        return None
    try:
        # Handle DD.MM.YY format
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            day, month, year = parts
            # Convert 2-digit year to 4-digit
            year = int(year)
            if year > 50:
                year = 1900 + year
            else:
                year = 2000 + year
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None


def parse_birth_date(birth_str: str) -> Optional[str]:
    """Parse birth date from 'Født: DD.MM.YYYY' format"""
    if not birth_str:
        return None
    try:
        match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', birth_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"
    except:
        pass
    return None


def parse_year_age(year_age_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse year and age from '2015 (14)' format"""
    if not year_age_str:
        return None, None
    try:
        match = re.match(r'(\d{4})\s*\((\d+)\)', year_age_str.strip())
        if match:
            return int(match.group(1)), int(match.group(2))
        # Try just year
        match = re.match(r'(\d{4})', year_age_str.strip())
        if match:
            return int(match.group(1)), None
    except:
        pass
    return None, None


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str]]:
    """
    Parse result and wind from formats like:
    - '9,17(+0,9)' -> ('9,17', '+0,9')
    - '5,80' -> ('5,80', None)
    - '1,45,04' -> ('1,45,04', None)
    """
    if not result_str:
        return '', None

    result_str = result_str.strip()

    # Check for wind in parentheses
    match = re.match(r'(.+?)\(([+-]?\d+[,.]?\d*)\)$', result_str)
    if match:
        return match.group(1), match.group(2)

    return result_str, None


def parse_athlete_page(html: str, athlete_id: int) -> Dict:
    """Parse athlete page HTML and extract all data"""
    soup = BeautifulSoup(html, 'html.parser')

    data = {
        'athlete_id': athlete_id,
        'name': None,
        'birth_date': None,
        'results': []
    }

    # Extract athlete name
    athlete_div = soup.find('div', id='athlete')
    if athlete_div:
        name_tag = athlete_div.find('h2')
        if name_tag:
            data['name'] = name_tag.get_text(strip=True)

        birth_tag = athlete_div.find('h3')
        if birth_tag:
            data['birth_date'] = parse_birth_date(birth_tag.get_text())

    if not data['name']:
        return data  # Empty athlete

    # Track current context
    current_section = None  # 'UTENDØRS' or 'INNENDØRS'
    current_event = None
    is_approved_section = True

    # Process all elements in order
    for element in soup.find_all(['div', 'table', 'h4']):
        # Check for outdoor/indoor header
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                text = h2.get_text(strip=True)
                if 'UTENDØRS' in text:
                    current_section = 'outdoor'
                elif 'INNENDØRS' in text:
                    current_section = 'indoor'

        # Check for event header
        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)
                is_approved_section = True  # Reset for new event

        # Check for disqualified section
        elif element.name == 'h4':
            text = element.get_text(strip=True)
            if 'Ikke godkjente' in text:
                is_approved_section = False

        # Process results table
        elif element.name == 'table' and current_event and current_section:
            rows = element.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if not cells:
                    continue

                # Determine if this is a 6-column (approved) or 7-column (rejected) row
                if len(cells) >= 6:
                    year, age = parse_year_age(cells[0].get_text())
                    result_raw = cells[1].get_text(strip=True)
                    result, wind = parse_result_wind(result_raw)
                    placement = cells[2].get_text(strip=True)
                    club = cells[3].get_text(strip=True)
                    date_str = cells[4].get_text(strip=True)
                    date = parse_date(date_str)

                    # Location - get title attribute for full venue name
                    location_cell = cells[5]
                    venue_full = location_cell.get('title', '')
                    competition_name = location_cell.get_text(strip=True)

                    # Rejection reason (7th column for disqualified)
                    rejection_reason = None
                    if len(cells) >= 7 and not is_approved_section:
                        rejection_reason = cells[6].get_text(strip=True)

                    result_data = {
                        'event': current_event,
                        'is_outdoor': current_section == 'outdoor',
                        'year': year,
                        'age': age,
                        'result': result,
                        'wind': wind,
                        'placement': placement,
                        'club': club,
                        'date': date,
                        'venue': venue_full,
                        'competition': competition_name,
                        'is_approved': is_approved_section,
                        'rejection_reason': rejection_reason
                    }

                    data['results'].append(result_data)

    return data


def save_to_csv(athletes_data: List[Dict], batch_num: int):
    """Save parsed data to CSV files"""

    # Athletes CSV
    athletes_file = os.path.join(OUTPUT_DIR, f"athletes_batch_{batch_num}.csv")
    with open(athletes_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'birth_date'])
        writer.writeheader()
        for athlete in athletes_data:
            if athlete['name']:
                writer.writerow({
                    'id': athlete['athlete_id'],
                    'name': athlete['name'],
                    'birth_date': athlete['birth_date']
                })

    # Results CSV
    results_file = os.path.join(OUTPUT_DIR, f"results_batch_{batch_num}.csv")
    with open(results_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'athlete_id', 'event', 'is_outdoor', 'year', 'age',
            'result', 'wind', 'placement', 'club', 'date',
            'venue', 'competition', 'is_approved', 'rejection_reason'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for athlete in athletes_data:
            for result in athlete['results']:
                row = {'athlete_id': athlete['athlete_id']}
                row.update(result)
                writer.writerow(row)

    logger.info(f"Saved batch {batch_num}: {athletes_file}, {results_file}")


def load_progress() -> int:
    """Load progress from checkpoint file"""
    checkpoint_file = os.path.join(OUTPUT_DIR, "_checkpoint.json")
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            return data.get('last_index', 0)
    return 0


def save_progress(index: int):
    """Save progress to checkpoint file"""
    checkpoint_file = os.path.join(OUTPUT_DIR, "_checkpoint.json")
    with open(checkpoint_file, 'w') as f:
        json.dump({'last_index': index, 'timestamp': datetime.now().isoformat()}, f)


def main():
    # Load athlete IDs
    logger.info("Loading athlete IDs...")
    with open(ATHLETE_IDS_FILE, 'r') as f:
        athlete_ids = json.load(f)

    total_athletes = len(athlete_ids)
    logger.info(f"Found {total_athletes:,} athletes to scrape")

    # Check for resume point
    start_index = load_progress()
    if start_index > 0:
        logger.info(f"Resuming from index {start_index}")

    # Process athletes
    batch_data = []
    batch_num = start_index // BATCH_SIZE
    total_results = 0

    for i, athlete_id in enumerate(athlete_ids[start_index:], start=start_index):
        try:
            # Fetch and parse
            html = fetch_athlete_results(int(athlete_id))
            data = parse_athlete_page(html, int(athlete_id))
            batch_data.append(data)

            results_count = len(data['results'])
            total_results += results_count

            # Progress logging
            if (i + 1) % 100 == 0:
                progress = ((i + 1) / total_athletes) * 100
                logger.info(f"Progress: {i + 1:,}/{total_athletes:,} ({progress:.1f}%) - {data['name'] or 'empty'} - {results_count} results")

            # Save batch
            if len(batch_data) >= BATCH_SIZE:
                batch_num += 1
                save_to_csv(batch_data, batch_num)
                save_progress(i + 1)
                batch_data = []

            # Rate limiting
            time.sleep(DELAY_BETWEEN_REQUESTS)

        except Exception as e:
            logger.error(f"Error processing athlete {athlete_id}: {e}")
            continue

    # Save final batch
    if batch_data:
        batch_num += 1
        save_to_csv(batch_data, batch_num)
        save_progress(total_athletes)

    logger.info(f"\n{'='*60}")
    logger.info(f"COMPLETE!")
    logger.info(f"Total athletes processed: {total_athletes:,}")
    logger.info(f"Total results extracted: {total_results:,}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
