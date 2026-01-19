"""
Scraper for women's results from minfriidrettsstatistikk.info
Uses correct class codes discovered from the website.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

REQUEST_DELAY = 0.3

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettsstatistikkScraper/1.0'
})

# Correct class codes from website
WOMEN_CLASS_CODES = {
    15: {'name': 'Jenter 13', 'gender': 'F', 'age_group': 'J13'},
    16: {'name': 'Jenter 14', 'gender': 'F', 'age_group': 'J14'},
    17: {'name': 'Jenter 15', 'gender': 'F', 'age_group': 'J15'},
    18: {'name': 'Jenter 16', 'gender': 'F', 'age_group': 'J16'},
    19: {'name': 'Jenter 17', 'gender': 'F', 'age_group': 'J17'},
    20: {'name': 'Jenter 18/19', 'gender': 'F', 'age_group': 'J18'},
    21: {'name': 'Jenter 20/22', 'gender': 'F', 'age_group': 'J20'},
    104: {'name': 'Kvinner Junior 15-19', 'gender': 'F', 'age_group': 'JuniorF'},
    196: {'name': 'Kvinner Junior 15-22', 'gender': 'F', 'age_group': 'JuniorF2'},
    22: {'name': 'Kvinner Senior', 'gender': 'F', 'age_group': 'Senior'},
}

# For comparison, here are the men's codes we used before
MEN_CLASS_CODES = {
    4: {'name': 'Gutter 13', 'gender': 'M', 'age_group': 'G13'},
    5: {'name': 'Gutter 14', 'gender': 'M', 'age_group': 'G14'},
    6: {'name': 'Gutter 15', 'gender': 'M', 'age_group': 'G15'},
    7: {'name': 'Gutter 16', 'gender': 'M', 'age_group': 'G16'},
    8: {'name': 'Gutter 17', 'gender': 'M', 'age_group': 'G17'},
    9: {'name': 'Gutter 18/19', 'gender': 'M', 'age_group': 'G18'},
    10: {'name': 'Gutter 20/22', 'gender': 'M', 'age_group': 'G20'},
    102: {'name': 'Menn Junior 15-19', 'gender': 'M', 'age_group': 'JuniorM'},
    195: {'name': 'Menn Junior 15-22', 'gender': 'M', 'age_group': 'JuniorM2'},
    11: {'name': 'Menn Senior', 'gender': 'M', 'age_group': 'Senior'},
}


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


def parse_birth_date(date_str):
    """Convert birth date from DD.MM.YY to YYYY-MM-DD."""
    if not date_str or date_str.strip() == '':
        return None
    try:
        date_str = date_str.strip()
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year < 100:
                year = 2000 + year if year <= 25 else 1900 + year
            return f"{year:04d}-{int(month):02d}-{int(day):02d}"
    except Exception:
        pass
    return None


def parse_result_with_wind(result_str):
    """Parse result with optional wind."""
    if not result_str:
        return None, None

    result_str = result_str.strip()

    wind_match = re.search(r'\(([\+\-]?\d+[,\.]\d+)\)', result_str)
    wind = None
    if wind_match:
        wind_str = wind_match.group(1).replace(',', '.')
        try:
            wind = float(wind_str)
        except ValueError:
            pass
        result_str = re.sub(r'\s*\([^\)]+\)', '', result_str).strip()

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

        round_map = {'h': 'heat', 'fi': 'final', 'sf': 'semi', 'kv': 'qualification'}
        round_type = round_map.get(round_type, round_type)

        return place, round_type, heat_num

    return None, None, None


def extract_athlete_id(href):
    """Extract athlete ID from href."""
    if not href:
        return None
    match = re.search(r'showathl=(\d+)', href)
    return int(match.group(1)) if match else None


def scrape_landsstatistikk(class_code, season=2024, outdoor='Y'):
    """Scrape landsstatistikk for a given class and season.

    Uses GET request with query parameters (not POST).
    """
    url = f"{BASE_URL}/LandsStatistikk.php"
    params = {
        'showclass': class_code,
        'showevent': 0,  # All events
        'showseason': season,
        'outdoor': outdoor,
        'showclub': 0
    }

    time.sleep(REQUEST_DELAY)
    try:
        # Use GET request - POST doesn't work correctly
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html = response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching class {class_code}: {e}")
        return []

    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    results = []

    class_info = WOMEN_CLASS_CODES.get(class_code) or MEN_CLASS_CODES.get(class_code) or {}
    gender = class_info.get('gender', 'F')

    tables = soup.find_all('table')

    for table in tables:
        # Find event name from preceding h4
        current_event = None
        result_category = 'main'

        for prev in table.find_all_previous(['h4', 'h5', 'div']):
            text = prev.get_text(strip=True).lower()

            if 'utenlandske' in text:
                result_category = 'foreign'
                continue
            elif 'manuelt' in text:
                result_category = 'manual'
                continue
            elif 'for mye vind' in text or 'medvind' in text:
                result_category = 'wind_assisted'
                continue

            if prev.name == 'h4':
                current_event = prev.get_text(strip=True)
                break

        if not current_event:
            continue

        rows = table.find_all('tr')

        for row in rows:
            ths = row.find_all('th')
            if ths:
                continue

            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            try:
                result_td = cols[0]
                name_club_td = cols[1]
                birth_td = cols[2]
                place_td = cols[3]
                location_td = cols[4]
                date_td = cols[5]

                result_str = result_td.get_text(strip=True)
                performance, wind = parse_result_with_wind(result_str)

                if not performance or not re.match(r'^\d', performance):
                    continue

                name_link = name_club_td.find('a')
                if name_link:
                    name = name_link.get_text(strip=True)
                    athlete_id = extract_athlete_id(name_link.get('href'))
                    full_text = name_club_td.get_text(strip=True)
                    club = full_text.split(', ', 1)[1] if ', ' in full_text else None
                else:
                    name = name_club_td.get_text(strip=True).split(',')[0].strip()
                    athlete_id = None
                    club = None

                birth_date_str = birth_td.get_text(strip=True)
                birth_date = parse_birth_date(birth_date_str)

                place_str = place_td.get_text(strip=True)
                place, round_type, heat_num = parse_placement(place_str)

                location_text = location_td.get_text(strip=True)
                if ',' in location_text:
                    parts = location_text.split(',', 1)
                    city = parts[0].strip()
                    meet_name = parts[1].strip() if len(parts) > 1 else location_text
                else:
                    city = location_text
                    meet_name = location_text

                date_str = date_td.get_text(strip=True)
                date = parse_date(date_str)

                results.append({
                    'athlete_id': athlete_id,
                    'name': name,
                    'club': club,
                    'birth_date': birth_date,
                    'performance': performance,
                    'wind': wind,
                    'place': place,
                    'round': round_type,
                    'heat': heat_num,
                    'city': city,
                    'meet_name': meet_name,
                    'date': date,
                    'class_code': class_code,
                    'event_name': current_event,
                    'category': result_category,
                    'season': season,
                    'indoor': outdoor != 'Y',
                    'gender': gender
                })

            except Exception as e:
                logger.warning(f"Error parsing row: {e}")
                continue

    return results


def scrape_all_women(seasons=[2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]):
    """Scrape all women's classes for given seasons."""
    all_results = []

    classes = list(WOMEN_CLASS_CODES.keys())
    total = len(seasons) * len(classes) * 2  # *2 for outdoor/indoor
    pbar = tqdm(total=total, desc="Scraping women's results")

    for season in seasons:
        for class_code in classes:
            for outdoor in ['Y', 'N']:
                venue = 'ute' if outdoor == 'Y' else 'inne'
                class_name = WOMEN_CLASS_CODES.get(class_code, {}).get('name', f'Class {class_code}')

                try:
                    results = scrape_landsstatistikk(class_code, season=season, outdoor=outdoor)
                    all_results.extend(results)
                    pbar.set_postfix({
                        'season': season,
                        'class': class_name[:15],
                        'venue': venue,
                        'total': len(all_results)
                    })
                except Exception as e:
                    logger.error(f"Error scraping {class_name} {season} {venue}: {e}")
                pbar.update(1)

    pbar.close()
    return all_results


def extract_unique_athletes(results):
    """Extract unique athletes from results."""
    athletes = {}

    for r in results:
        athlete_key = (r.get('name'), r.get('birth_date'))
        if athlete_key[0] and athlete_key not in athletes:
            name_parts = r['name'].split()
            athletes[athlete_key] = {
                'external_id': r.get('athlete_id'),
                'first_name': name_parts[0] if name_parts else '',
                'last_name': ' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
                'full_name': r['name'],
                'birth_date': r.get('birth_date'),
                'club': r.get('club'),
                'gender': r.get('gender', 'F')
            }

    return list(athletes.values())


def main():
    """Main function - scrape all women's data."""
    logger.info("Starting women's data scrape from minfriidrettsstatistikk.info")

    # Scrape all seasons
    results = scrape_all_women()

    logger.info(f"Scraped {len(results)} women's results")

    # Save raw results
    output_file = OUTPUT_DIR / 'women_results_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Saved raw results to {output_file}")

    # Extract unique athletes
    athletes = extract_unique_athletes(results)

    athletes_file = OUTPUT_DIR / 'women_athletes.json'
    with open(athletes_file, 'w', encoding='utf-8') as f:
        json.dump(athletes, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Saved {len(athletes)} unique women athletes to {athletes_file}")

    # Summary
    logger.info(f"""
    Scraping complete!
    - Results: {len(results)}
    - Unique athletes: {len(athletes)}

    Files saved to: {OUTPUT_DIR}
    """)


if __name__ == '__main__':
    main()
