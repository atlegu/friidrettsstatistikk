"""
Scraper that processes athletes by letter
Run with: python scrape_by_letter.py A
Or: python scrape_by_letter.py A 0 500  (for first 500 of letter A)
"""

import requests
import json
import csv
import os
import re
import sys
import time
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Tuple
import logging

# Configuration
OUTPUT_DIR = "scraped_data"
SEARCH_HTML_DIR = "athlete_search_html"
DELAY_BETWEEN_REQUESTS = 0.2  # seconds

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup logging
def setup_logging(letter: str):
    log_file = os.path.join(OUTPUT_DIR, f"scrape_{letter}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
        force=True
    )
    return logging.getLogger(__name__)


def fetch_athlete_results(athlete_id: int) -> str:
    """Fetch ALL results for an athlete"""
    url = "https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php"

    data = {
        "athlete": athlete_id,
        "type": "RES"
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
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            day, month, year = parts
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
        match = re.match(r'(\d{4})', year_age_str.strip())
        if match:
            return int(match.group(1)), None
    except:
        pass
    return None, None


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str]]:
    """Parse result and wind from formats like '9,17(+0,9)'"""
    if not result_str:
        return '', None

    result_str = result_str.strip()
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
        return data

    # Track current context
    current_section = None
    current_event = None
    is_approved_section = True

    # Process all elements
    for element in soup.find_all(['div', 'table', 'h4']):
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                text = h2.get_text(strip=True)
                if 'UTENDØRS' in text:
                    current_section = 'outdoor'
                elif 'INNENDØRS' in text:
                    current_section = 'indoor'

        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)
                is_approved_section = True

        elif element.name == 'h4':
            text = element.get_text(strip=True)
            if 'Ikke godkjente' in text:
                is_approved_section = False

        elif element.name == 'table' and current_event and current_section:
            rows = element.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if not cells or len(cells) < 6:
                    continue

                year, age = parse_year_age(cells[0].get_text())
                result_raw = cells[1].get_text(strip=True)
                result, wind = parse_result_wind(result_raw)
                placement = cells[2].get_text(strip=True)
                club = cells[3].get_text(strip=True)
                date_str = cells[4].get_text(strip=True)
                date = parse_date(date_str)

                location_cell = cells[5]
                venue_full = location_cell.get('title', '')
                competition_name = location_cell.get_text(strip=True)

                rejection_reason = None
                if len(cells) >= 7 and not is_approved_section:
                    rejection_reason = cells[6].get_text(strip=True)

                # Generate a competition key for grouping by meet
                comp_key = f"{date}|{venue_full}|{competition_name}" if date and venue_full else None

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
                    'competition_key': comp_key,  # For grouping by meet
                    'is_approved': is_approved_section,
                    'rejection_reason': rejection_reason
                }

                data['results'].append(result_data)

    return data


def get_athletes_for_letter(letter: str) -> List[Tuple[int, str]]:
    """Get all athlete IDs and names for a given letter from the search HTML"""
    search_file = os.path.join(SEARCH_HTML_DIR, f"search_{letter}.html")

    if not os.path.exists(search_file):
        raise FileNotFoundError(f"Search file not found: {search_file}")

    with open(search_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract athlete IDs and names
    pattern = r'showathl=(\d+)[^>]*>([^<]+)'
    matches = re.findall(pattern, html)

    return [(int(aid), name.strip()) for aid, name in matches]


def load_progress(letter: str) -> int:
    """Load progress for a specific letter"""
    checkpoint_file = os.path.join(OUTPUT_DIR, f"checkpoint_{letter}.json")
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            return data.get('last_index', 0)
    return 0


def save_progress(letter: str, index: int, total: int):
    """Save progress for a specific letter"""
    checkpoint_file = os.path.join(OUTPUT_DIR, f"checkpoint_{letter}.json")
    with open(checkpoint_file, 'w') as f:
        json.dump({
            'letter': letter,
            'last_index': index,
            'total': total,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)


def scrape_letter(letter: str, start_idx: int = None, end_idx: int = None):
    """Scrape all athletes for a given letter"""
    logger = setup_logging(letter)

    logger.info(f"=" * 60)
    logger.info(f"SCRAPING LETTER: {letter}")
    logger.info(f"=" * 60)

    # Get athletes for this letter
    athletes = get_athletes_for_letter(letter)
    total = len(athletes)
    logger.info(f"Found {total} athletes for letter {letter}")

    # Handle start/end indices
    if start_idx is None:
        start_idx = load_progress(letter)
    if end_idx is None:
        end_idx = total

    end_idx = min(end_idx, total)

    if start_idx > 0:
        logger.info(f"Resuming from index {start_idx}")

    logger.info(f"Processing athletes {start_idx} to {end_idx}")

    # Prepare output files
    batch_suffix = f"{start_idx}-{end_idx}" if start_idx > 0 or end_idx < total else ""
    athletes_file = os.path.join(OUTPUT_DIR, f"athletes_{letter}{batch_suffix}.csv")
    results_file = os.path.join(OUTPUT_DIR, f"results_{letter}{batch_suffix}.csv")

    # Open CSV files
    athletes_csv = open(athletes_file, 'w', newline='', encoding='utf-8')
    results_csv = open(results_file, 'w', newline='', encoding='utf-8')

    athletes_writer = csv.DictWriter(athletes_csv, fieldnames=['id', 'name', 'birth_date'])
    athletes_writer.writeheader()

    results_fieldnames = [
        'athlete_id', 'event', 'is_outdoor', 'year', 'age',
        'result', 'wind', 'placement', 'club', 'date',
        'venue', 'competition', 'competition_key', 'is_approved', 'rejection_reason'
    ]
    results_writer = csv.DictWriter(results_csv, fieldnames=results_fieldnames)
    results_writer.writeheader()

    # Process athletes
    total_results = 0
    processed = 0
    errors = 0

    for i in range(start_idx, end_idx):
        athlete_id, athlete_name = athletes[i]

        try:
            html = fetch_athlete_results(athlete_id)
            data = parse_athlete_page(html, athlete_id)

            # Write athlete
            if data['name']:
                athletes_writer.writerow({
                    'id': data['athlete_id'],
                    'name': data['name'],
                    'birth_date': data['birth_date']
                })

                # Write results
                for result in data['results']:
                    row = {'athlete_id': data['athlete_id']}
                    row.update(result)
                    results_writer.writerow(row)

                total_results += len(data['results'])

            processed += 1

            # Progress logging
            if (i + 1) % 50 == 0 or i == end_idx - 1:
                progress = ((i - start_idx + 1) / (end_idx - start_idx)) * 100
                logger.info(f"Progress: {i + 1}/{end_idx} ({progress:.1f}%) - {data['name'] or 'empty'} - {len(data['results'])} results")

                # Flush files periodically
                athletes_csv.flush()
                results_csv.flush()

            # Save checkpoint every 100 athletes
            if (i + 1) % 100 == 0:
                save_progress(letter, i + 1, total)

            time.sleep(DELAY_BETWEEN_REQUESTS)

        except Exception as e:
            logger.error(f"Error processing athlete {athlete_id} ({athlete_name}): {e}")
            errors += 1
            continue

    # Close files
    athletes_csv.close()
    results_csv.close()

    # Final checkpoint
    save_progress(letter, end_idx, total)

    logger.info(f"\n{'=' * 60}")
    logger.info(f"LETTER {letter} COMPLETE!")
    logger.info(f"Athletes processed: {processed}")
    logger.info(f"Total results: {total_results}")
    logger.info(f"Errors: {errors}")
    logger.info(f"Output: {athletes_file}, {results_file}")
    logger.info(f"{'=' * 60}")

    return {
        'letter': letter,
        'athletes_processed': processed,
        'total_results': total_results,
        'errors': errors
    }


def show_status():
    """Show scraping status for all letters"""
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWYZÆØÅ")

    print("\nSCRAPING STATUS")
    print("=" * 60)
    print(f"{'Letter':<8} {'Progress':<20} {'Status'}")
    print("-" * 60)

    for letter in letters:
        checkpoint_file = os.path.join(OUTPUT_DIR, f"checkpoint_{letter}.json")
        results_file = os.path.join(OUTPUT_DIR, f"results_{letter}.csv")

        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            progress = f"{data['last_index']}/{data['total']}"
            if data['last_index'] >= data['total']:
                status = "✓ Complete"
            else:
                status = "⏸ Partial"
        elif os.path.exists(results_file):
            status = "✓ Complete"
            progress = "Done"
        else:
            status = "○ Not started"
            progress = "-"

        print(f"{letter:<8} {progress:<20} {status}")

    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scrape_by_letter.py <LETTER>           # Scrape all athletes for letter")
        print("  python scrape_by_letter.py <LETTER> <START> <END>  # Scrape range")
        print("  python scrape_by_letter.py status             # Show progress")
        print()
        print("Examples:")
        print("  python scrape_by_letter.py A                  # Scrape all of letter A")
        print("  python scrape_by_letter.py S 0 5000           # Scrape first 5000 of letter S")
        print("  python scrape_by_letter.py S 5000 10000       # Scrape next 5000 of letter S")
        print("  python scrape_by_letter.py status             # Check progress")
        return

    arg = sys.argv[1]

    if arg.lower() == 'status':
        show_status()
        return

    letter = arg.upper()

    # Validate letter
    valid_letters = list("ABCDEFGHIJKLMNOPQRSTUVWYZÆØÅ")
    if letter not in valid_letters:
        print(f"Invalid letter: {letter}")
        print(f"Valid letters: {' '.join(valid_letters)}")
        return

    # Parse optional start/end
    start_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
    end_idx = int(sys.argv[3]) if len(sys.argv) > 3 else None

    scrape_letter(letter, start_idx, end_idx)


if __name__ == "__main__":
    main()
