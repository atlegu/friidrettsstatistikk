"""
Scrape all results from individual athlete profiles.
This gets ALL results, not just the best per event from rankings.
"""

import json
import time
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
OUTPUT_DIR = Path(__file__).parent / "data"
REQUEST_DELAY = 0.3

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettsstatistikkScraper/1.0'
})


def parse_date(date_str):
    """Convert date from DD.MM.YY to YYYY-MM-DD."""
    if not date_str or date_str.strip() == '':
        return None
    try:
        date_str = date_str.strip()
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            return f"{year:04d}-{int(month):02d}-{int(day):02d}"
    except Exception:
        pass
    return None


def parse_result_with_wind(result_str):
    """Parse result with optional wind, e.g. '6,82(+1,3)' -> ('6.82', 1.3)"""
    if not result_str:
        return None, None

    result_str = result_str.strip()

    # Find wind in parentheses
    wind_match = re.search(r'\(([\+\-]?\d+[,\.]\d+)\)', result_str)
    wind = None
    if wind_match:
        wind_str = wind_match.group(1).replace(',', '.')
        try:
            wind = float(wind_str)
        except ValueError:
            pass
        result_str = re.sub(r'\s*\([^\)]+\)', '', result_str).strip()

    # Convert comma to period
    result = result_str.replace(',', '.')

    return result, wind


def parse_placement(place_str):
    """Parse placement like '1-h2' -> (1, 'heat', 2)"""
    if not place_str:
        return None, None, None

    place_str = place_str.strip()

    if place_str.isdigit():
        return int(place_str), None, None

    place_str = re.sub(r'\s*\([^)]+\)', '', place_str).strip()

    match = re.match(r'(\d+)-?([a-z]+)?-?(\d*)', place_str, re.IGNORECASE)
    if match:
        place = int(match.group(1)) if match.group(1) else None
        round_type = match.group(2) if match.group(2) else None
        heat_num = int(match.group(3)) if match.group(3) else None

        round_map = {
            'h': 'heat',
            'fi': 'final',
            'sf': 'semi',
            'kv': 'qualification',
            'nat': 'final',  # national final
        }
        round_type = round_map.get(round_type, round_type)

        return place, round_type, heat_num

    return None, None, None


def scrape_athlete_all_results(athlete_id, athlete_name=None):
    """Scrape ALL results for an athlete from their profile page."""
    url = f"{BASE_URL}/UtoverStatistikk.php"

    # Use POST with type=RES to get ALL results (not just bests)
    data = {
        'athlete': athlete_id,
        'type': 'RES'
    }

    time.sleep(REQUEST_DELAY)
    try:
        response = session.post(url, data=data, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html = response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching athlete {athlete_id}: {e}")
        return []

    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    results = []

    # Get athlete name and birth date from page header
    name_elem = soup.find('h2')
    if name_elem and not athlete_name:
        athlete_name = name_elem.get_text(strip=True)

    birth_date = None
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text.startswith('Født:'):
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                birth_date = parse_date(match.group(1))
            break

    # Track current context
    current_indoor = False
    current_event = None
    is_invalid_section = False  # "Ikke godkjente resultater"

    # Process all elements in order
    for elem in soup.find_all(['h2', 'h3', 'h4', 'table']):
        if elem.name == 'h2':
            text = elem.get_text(strip=True).upper()
            if 'INNENDØRS' in text:
                current_indoor = True
            elif 'UTENDØRS' in text:
                current_indoor = False

        elif elem.name == 'h3':
            text = elem.get_text(strip=True)
            if text:  # Non-empty h3 is event name
                current_event = text
                is_invalid_section = False

        elif elem.name == 'h4':
            text = elem.get_text(strip=True).lower()
            if 'ikke godkjente' in text:
                is_invalid_section = True

        elif elem.name == 'table' and current_event:
            rows = elem.find_all('tr')
            if not rows:
                continue

            # Check header
            header_row = rows[0]
            headers = [th.get_text(strip=True).upper() for th in header_row.find_all(['th', 'td'])]

            # Expected columns: ÅR, RESULTAT, PLASSERING, KLUBB, DATO, STED, [ÅRSAK]
            if 'RESULTAT' not in headers:
                continue

            # Find column indices
            try:
                year_idx = headers.index('ÅR') if 'ÅR' in headers else 0
                result_idx = headers.index('RESULTAT') if 'RESULTAT' in headers else 1
                place_idx = headers.index('PLASSERING') if 'PLASSERING' in headers else 2
                club_idx = headers.index('KLUBB') if 'KLUBB' in headers else 3
                date_idx = headers.index('DATO') if 'DATO' in headers else 4
                location_idx = headers.index('STED') if 'STED' in headers else 5
            except (ValueError, IndexError):
                continue

            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) < 6:
                    continue

                try:
                    # Parse year (e.g., "2025 (27)" -> 2025)
                    year_text = cols[year_idx].get_text(strip=True)
                    year_match = re.search(r'(\d{4})', year_text)
                    season = int(year_match.group(1)) if year_match else None

                    # Parse result
                    result_str = cols[result_idx].get_text(strip=True)
                    performance, wind = parse_result_with_wind(result_str)

                    if not performance:
                        continue

                    # Parse placement
                    place_str = cols[place_idx].get_text(strip=True)
                    place, round_type, heat_num = parse_placement(place_str)

                    # Parse club
                    club = cols[club_idx].get_text(strip=True)

                    # Parse date
                    date_str = cols[date_idx].get_text(strip=True)
                    date = parse_date(date_str)

                    # Parse location (City, MeetName)
                    location_text = cols[location_idx].get_text(strip=True)
                    if ',' in location_text:
                        parts = location_text.split(',', 1)
                        city = parts[0].strip()
                        meet_name = parts[1].strip()
                    else:
                        city = location_text
                        meet_name = location_text

                    results.append({
                        'athlete_id': athlete_id,
                        'name': athlete_name,
                        'birth_date': birth_date,
                        'event_name': current_event,
                        'performance': performance,
                        'wind': wind,
                        'place': place,
                        'round': round_type,
                        'heat': heat_num,
                        'club': club,
                        'date': date,
                        'city': city,
                        'meet_name': meet_name,
                        'indoor': current_indoor,
                        'season': season,
                        'valid': not is_invalid_section,  # Mark wind-assisted etc.
                    })

                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue

    return results


def main():
    """Main function - scrape all athletes."""
    # Load athlete IDs from men/women results (has ALL athletes from rankings)
    men_file = OUTPUT_DIR / 'men_results_raw.json'
    women_file = OUTPUT_DIR / 'women_results_raw.json'

    if not men_file.exists() and not women_file.exists():
        logger.error("No results files found. Run scraper first.")
        return

    # Collect unique athletes from both files
    athlete_ids = []
    seen = set()

    for results_file in [men_file, women_file]:
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            for r in results:
                ext_id = r.get('athlete_id')
                name = r.get('name', '')
                if ext_id and ext_id not in seen:
                    seen.add(ext_id)
                    athlete_ids.append((ext_id, name))

    logger.info(f"Found {len(athlete_ids)} unique athletes to scrape")

    # Load existing results to avoid re-scraping
    all_results = []
    already_scraped = set()
    output_file = OUTPUT_DIR / 'all_athlete_results.json'
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
        already_scraped = set(r.get('athlete_id') for r in all_results)
        logger.info(f"Loaded {len(all_results)} existing results from {len(already_scraped)} athletes")

    # Filter out already scraped athletes
    athletes_to_scrape = [(aid, name) for aid, name in athlete_ids if aid not in already_scraped]
    logger.info(f"Skipping {len(already_scraped)} already scraped, {len(athletes_to_scrape)} remaining")
    failed = []

    # Save progress every N athletes
    save_interval = 500
    scraped_count = 0

    for athlete_id, athlete_name in tqdm(athletes_to_scrape, desc="Scraping athletes"):
        try:
            results = scrape_athlete_all_results(athlete_id, athlete_name)
            all_results.extend(results)
            scraped_count += 1

            # Save periodically
            if scraped_count % save_interval == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
                logger.info(f"Progress saved: {len(all_results)} results")

        except Exception as e:
            logger.warning(f"Failed to scrape athlete {athlete_id}: {e}")
            failed.append(athlete_id)

    logger.info(f"Scraped {len(all_results)} total results")
    logger.info(f"Failed: {len(failed)} athletes")

    # Save results
    output_file = OUTPUT_DIR / 'all_athlete_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Saved to {output_file}")

    # Also save as CSV
    import pandas as pd
    df = pd.DataFrame(all_results)
    df.to_csv(OUTPUT_DIR / 'all_athlete_results.csv', index=False, encoding='utf-8')
    logger.info(f"Saved CSV with {len(all_results)} results")


if __name__ == '__main__':
    main()
