"""
Scrape historical athletes by iterating through ID ranges.
These athletes don't appear on the regular rankings but have profiles.
"""

import json
import time
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
OUTPUT_DIR = Path(__file__).parent / "data"
REQUEST_DELAY = 0.2  # Be polite to the server

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettsstatistikkScraper/1.0'
})


def parse_date(date_str):
    """Convert date from DD.MM.YY or DD.MM.YYYY to YYYY-MM-DD."""
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
            'nat': 'final',
        }
        round_type = round_map.get(round_type, round_type)

        return place, round_type, heat_num

    return None, None, None


def scrape_athlete_profile(athlete_id):
    """Scrape ALL results for an athlete from their profile page."""
    url = f"{BASE_URL}/UtoverStatistikk.php"

    # Use POST with type=RES to get ALL results
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
        logger.debug(f"Error fetching athlete {athlete_id}: {e}")
        return None, []

    if not html or 'Utøver ikke funnet' in html:
        return None, []

    soup = BeautifulSoup(html, 'lxml')
    results = []

    # Get athlete name from page header
    name_elem = soup.find('h2')
    athlete_name = name_elem.get_text(strip=True) if name_elem else None

    if not athlete_name:
        return None, []

    # Get birth date and gender
    birth_date = None
    gender = None

    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text.startswith('Født:'):
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if match:
                birth_date = parse_date(match.group(1))
        elif 'Mann' in text or 'Gutt' in text:
            gender = 'M'
        elif 'Kvinne' in text or 'Jente' in text:
            gender = 'F'

    athlete_info = {
        'id': str(athlete_id),
        'name': athlete_name,
        'birth_date': birth_date,
        'gender': gender
    }

    # Track current context
    current_indoor = False
    current_event = None
    is_invalid_section = False

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
            if text and not text.startswith('Født') and not text.startswith('Klubb'):
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

            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) < 6:
                    continue

                try:
                    # Parse year
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

                    # Parse location
                    location_text = cols[location_idx].get_text(strip=True)
                    if ',' in location_text:
                        parts = location_text.split(',', 1)
                        city = parts[0].strip()
                        meet_name = parts[1].strip()
                    else:
                        city = location_text
                        meet_name = location_text

                    results.append({
                        'athlete_id': str(athlete_id),
                        'name': athlete_name,
                        'birth_date': birth_date,
                        'gender': gender,
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
                        'valid': not is_invalid_section,
                    })

                except Exception as e:
                    logger.debug(f"Error parsing row for athlete {athlete_id}: {e}")
                    continue

    return athlete_info, results


def main():
    parser = argparse.ArgumentParser(description='Scrape historical athletes by ID range')
    parser.add_argument('--start', type=int, default=50000, help='Start ID (default: 50000)')
    parser.add_argument('--end', type=int, default=70000, help='End ID (default: 70000)')
    parser.add_argument('--output', type=str, default='historical_athletes_results.json', help='Output filename')
    args = parser.parse_args()

    output_file = OUTPUT_DIR / args.output
    athletes_file = OUTPUT_DIR / args.output.replace('_results', '_info').replace('.json', '.json')

    # Load existing data to resume
    all_results = []
    all_athletes = []
    scraped_ids = set()

    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
        scraped_ids = set(r.get('athlete_id') for r in all_results)
        logger.info(f"Loaded {len(all_results)} existing results from {len(scraped_ids)} athletes")

    if athletes_file.exists():
        with open(athletes_file, 'r', encoding='utf-8') as f:
            all_athletes = json.load(f)

    # Scrape the ID range
    total_ids = args.end - args.start
    new_athletes = 0
    new_results = 0
    failed = 0
    save_interval = 100

    logger.info(f"Scraping athlete IDs from {args.start} to {args.end}")

    pbar = tqdm(range(args.start, args.end), desc="Scraping historical athletes")

    for athlete_id in pbar:
        if str(athlete_id) in scraped_ids:
            continue

        try:
            athlete_info, results = scrape_athlete_profile(athlete_id)

            if athlete_info:
                all_athletes.append(athlete_info)
                all_results.extend(results)
                new_athletes += 1
                new_results += len(results)
                scraped_ids.add(str(athlete_id))

                pbar.set_postfix({
                    'athletes': new_athletes,
                    'results': new_results,
                    'last': athlete_info['name'][:20] if athlete_info['name'] else '?'
                })
            else:
                failed += 1

            # Save periodically
            if new_athletes > 0 and new_athletes % save_interval == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
                with open(athletes_file, 'w', encoding='utf-8') as f:
                    json.dump(all_athletes, f, ensure_ascii=False, indent=2, default=str)
                logger.info(f"Progress saved: {len(all_athletes)} athletes, {len(all_results)} results")

        except Exception as e:
            logger.warning(f"Failed to scrape athlete {athlete_id}: {e}")
            failed += 1

    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    with open(athletes_file, 'w', encoding='utf-8') as f:
        json.dump(all_athletes, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"Done! Scraped {new_athletes} new athletes with {new_results} results")
    logger.info(f"Failed/empty: {failed} IDs")
    logger.info(f"Total athletes: {len(all_athletes)}")
    logger.info(f"Total results: {len(all_results)}")
    logger.info(f"Saved to {output_file}")


if __name__ == '__main__':
    main()
