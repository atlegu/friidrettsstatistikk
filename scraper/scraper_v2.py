"""
Scraper v2 for minfriidrettsstatistikk.info
Oppdatert basert på faktisk HTML-struktur.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL
BASE_URL = "https://www.minfriidrettsstatistikk.info/php"

# Output directory
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Rate limiting
REQUEST_DELAY = 0.3

# Session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettsstatistikkScraper/1.0'
})

# ============================================================
# KLASSE-KODER
# ============================================================
CLASS_CODES = {
    11: {'name': 'Menn senior', 'gender': 'M', 'age_group': 'Senior'},
    12: {'name': 'Kvinner senior', 'gender': 'F', 'age_group': 'Senior'},
    21: {'name': 'Menn U23', 'gender': 'M', 'age_group': 'U23'},
    22: {'name': 'Kvinner U23', 'gender': 'F', 'age_group': 'U23'},
    31: {'name': 'Menn U20', 'gender': 'M', 'age_group': 'U20'},
    32: {'name': 'Kvinner U20', 'gender': 'F', 'age_group': 'U20'},
    41: {'name': 'Gutter U18', 'gender': 'M', 'age_group': 'U18'},
    42: {'name': 'Jenter U18', 'gender': 'F', 'age_group': 'U18'},
    51: {'name': 'Gutter 15', 'gender': 'M', 'age_group': 'G15'},
    52: {'name': 'Jenter 15', 'gender': 'F', 'age_group': 'J15'},
    61: {'name': 'Gutter 14', 'gender': 'M', 'age_group': 'G14'},
    62: {'name': 'Jenter 14', 'gender': 'F', 'age_group': 'J14'},
    71: {'name': 'Gutter 13', 'gender': 'M', 'age_group': 'G13'},
    72: {'name': 'Jenter 13', 'gender': 'F', 'age_group': 'J13'},
}

# ============================================================
# ØVELSE-KODER
# ============================================================
EVENT_CODES = {
    1: {'code': '60m', 'name': '60 meter'},
    2: {'code': '100m', 'name': '100 meter'},
    3: {'code': '200m', 'name': '200 meter'},
    4: {'code': '400m', 'name': '400 meter'},
    5: {'code': '800m', 'name': '800 meter'},
    6: {'code': '1500m', 'name': '1500 meter'},
    7: {'code': '3000m', 'name': '3000 meter'},
    8: {'code': '5000m', 'name': '5000 meter'},
    9: {'code': '10000m', 'name': '10000 meter'},
    10: {'code': '60mh', 'name': '60 meter hekk'},
    11: {'code': '100mh', 'name': '100 meter hekk'},
    12: {'code': '110mh', 'name': '110 meter hekk'},
    13: {'code': '400mh', 'name': '400 meter hekk'},
    14: {'code': '3000mhinder', 'name': '3000 meter hinder'},
    15: {'code': 'hoyde', 'name': 'Høyde'},
    16: {'code': 'stav', 'name': 'Stav'},
    17: {'code': 'lengde', 'name': 'Lengde'},
    18: {'code': 'tresteg', 'name': 'Tresteg'},
    19: {'code': 'kule', 'name': 'Kule'},
    20: {'code': 'diskos', 'name': 'Diskos'},
    21: {'code': 'slegge', 'name': 'Slegge'},
    22: {'code': 'spyd', 'name': 'Spyd'},
    23: {'code': '5kamp', 'name': 'Femkamp'},
    24: {'code': '7kamp', 'name': 'Sjukamp'},
    25: {'code': '10kamp', 'name': 'Tikamp'},
}


def fetch_page(url, params=None, method='GET'):
    """Hent en side med rate limiting."""
    time.sleep(REQUEST_DELAY)
    try:
        if method == 'POST':
            response = session.post(url, data=params, timeout=30)
        else:
            response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        logger.error(f"Feil ved henting av {url}: {e}")
        return None


def parse_date(date_str):
    """Konverter dato fra DD.MM.YY til YYYY-MM-DD."""
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
    """Konverter fødselsdato fra DD.MM.YY til YYYY-MM-DD."""
    if not date_str or date_str.strip() == '':
        return None
    try:
        date_str = date_str.strip()
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year < 100:
                # Fødselsdato: 00-25 = 2000s, 26-99 = 1900s
                year = 2000 + year if year <= 25 else 1900 + year
            return f"{year:04d}-{int(month):02d}-{int(day):02d}"
    except Exception:
        pass
    return None


def parse_result_with_wind(result_str):
    """Parse resultat med eventuell vind, f.eks. '6,82(+1,3)' -> ('6.82', 1.3)"""
    if not result_str:
        return None, None

    result_str = result_str.strip()

    # Finn vind i parentes
    wind_match = re.search(r'\(([\+\-]?\d+[,\.]\d+)\)', result_str)
    wind = None
    if wind_match:
        wind_str = wind_match.group(1).replace(',', '.')
        try:
            wind = float(wind_str)
        except ValueError:
            pass
        result_str = re.sub(r'\s*\([^\)]+\)', '', result_str).strip()

    # Konverter komma til punktum
    result = result_str.replace(',', '.')

    return result, wind


def parse_placement(place_str):
    """Parse plassering som '1-h2' -> (1, 'heat', 2)"""
    if not place_str:
        return None, None, None

    place_str = place_str.strip()

    # Enkel plassering (bare tall)
    if place_str.isdigit():
        return int(place_str), None, None

    # Med heat/finale info: "1-h2", "2-fi", "1 (G-20/22)"
    # Først, fjern aldersklasse-info i parentes
    place_str = re.sub(r'\s*\([^)]+\)', '', place_str).strip()

    match = re.match(r'(\d+)-?([a-z]+)?-?(\d*)', place_str, re.IGNORECASE)
    if match:
        place = int(match.group(1)) if match.group(1) else None
        round_type = match.group(2) if match.group(2) else None
        heat_num = int(match.group(3)) if match.group(3) else None

        # Map round types
        round_map = {
            'h': 'heat',
            'fi': 'final',
            'sf': 'semi',
            'kv': 'qualification',
        }
        round_type = round_map.get(round_type, round_type)

        return place, round_type, heat_num

    return None, None, None


def extract_athlete_id(href):
    """Ekstraher utøver-ID fra href."""
    if not href:
        return None
    match = re.search(r'showathl=(\d+)', href)
    return int(match.group(1)) if match else None


def scrape_landsstatistikk(class_code, event_code, season=2025, outdoor='Y'):
    """Scrape landsstatistikk for en gitt klasse og øvelse.

    Hvis event_code=0, scrapes alle øvelser.
    """
    url = f"{BASE_URL}/LandsStatistikk.php"
    params = {
        'showclass': class_code,
        'showevent': event_code,
        'showseason': season,
        'outdoor': outdoor,
        'showclub': 0
    }

    # Bruker POST - GET returnerer bare søkeskjemaet
    html = fetch_page(url, params=params, method='POST')
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    results = []

    # Finn alle tabeller med resultater
    tables = soup.find_all('table')

    # Spesialkategorier vi ønsker å markere
    special_categories = [
        'utenlandske statsborgere',
        'manuelt supplement',
        'for mye vind',
        'manglende informasjon om vind',
        'for liten medvind',
        'ujevn bane'
    ]

    for table in tables:
        # Finn øvelsesnavnet fra nærmeste h4 før tabellen
        current_event = None
        result_category = 'main'  # main, foreign, manual, wind_assisted, etc.

        # Søk bakover etter h4 (øvelsesnavn) eller div (spesialkategori)
        for prev in table.find_all_previous(['h4', 'h5', 'div']):
            text = prev.get_text(strip=True).lower()

            # Sjekk om dette er en spesialkategori
            is_special = False
            for cat in special_categories:
                if cat in text:
                    is_special = True
                    if 'utenlandske' in text:
                        result_category = 'foreign'
                    elif 'manuelt' in text:
                        result_category = 'manual'
                    elif 'for mye vind' in text or 'medvind' in text:
                        result_category = 'wind_assisted'
                    elif 'manglende' in text:
                        result_category = 'wind_missing'
                    break

            if is_special:
                continue

            # Hvis det er et h4 element, er det sannsynligvis øvelsesnavnet
            if prev.name == 'h4':
                current_event = prev.get_text(strip=True)
                break

        if not current_event:
            continue

        rows = table.find_all('tr')

        for row in rows:
            # Sjekk om dette er en header-rad
            ths = row.find_all('th')
            if ths:
                continue

            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            try:
                # Struktur: Resultat | Navn, Klubb | F.Dato | Plassering | Sted | R.Dato
                result_td = cols[0]
                name_club_td = cols[1]
                birth_td = cols[2]
                place_td = cols[3]
                location_td = cols[4]
                date_td = cols[5]

                # Parse resultat
                result_str = result_td.get_text(strip=True)
                performance, wind = parse_result_with_wind(result_str)

                if not performance or not re.match(r'^\d', performance):
                    continue

                # Parse navn og klubb - navn er i <a>-tag
                name_link = name_club_td.find('a')
                if name_link:
                    name = name_link.get_text(strip=True)
                    athlete_id = extract_athlete_id(name_link.get('href'))
                    # Klubb er etter ", "
                    full_text = name_club_td.get_text(strip=True)
                    if ', ' in full_text:
                        club = full_text.split(', ', 1)[1]
                    else:
                        club = None
                else:
                    name = name_club_td.get_text(strip=True).split(',')[0].strip()
                    athlete_id = None
                    club = None

                # Parse fødselsdato
                birth_date_str = birth_td.get_text(strip=True)
                birth_date = parse_birth_date(birth_date_str)

                # Parse plassering
                place_str = place_td.get_text(strip=True)
                place, round_type, heat_num = parse_placement(place_str)

                # Parse sted - by og stevnenavn
                location_text = location_td.get_text(strip=True)
                # Format: "Lillehammer,Heisekompanisprinten" (komma uten mellomrom)
                if ',' in location_text:
                    parts = location_text.split(',', 1)
                    city = parts[0].strip()
                    meet_name = parts[1].strip() if len(parts) > 1 else location_text
                else:
                    city = location_text
                    meet_name = location_text

                # Parse dato
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
                    'event_name': current_event,  # Fra HTML, ikke fra event_code
                    'category': result_category,  # main, foreign, manual, etc.
                    'season': season,
                    'indoor': outdoor != 'Y',
                    'gender': CLASS_CODES.get(class_code, {}).get('gender')
                })

            except Exception as e:
                logger.warning(f"Feil ved parsing av rad: {e}")
                continue

    return results


def scrape_athlete_profile(athlete_id):
    """Hent komplett profil for en utøver."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    params = {
        'showathl': athlete_id,
        'showevent': 0,
        'showseason': 0,
        'outdoor': 'A',
        'listtype': 'All'
    }

    html = fetch_page(url, params=params)
    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml')

    profile = {
        'external_id': athlete_id,
        'first_name': '',
        'last_name': '',
        'gender': None,
        'birth_date': None,
        'club': '',
        'results': []
    }

    # Finn utøvernavn fra h1/h2
    headers = soup.find_all(['h1', 'h2', 'h3'])
    for header in headers:
        text = header.get_text(strip=True)
        if text and not text.startswith('Født') and text not in ['UTENDØRS', 'INNENDØRS']:
            parts = text.split()
            if len(parts) >= 2:
                profile['first_name'] = parts[0]
                profile['last_name'] = ' '.join(parts[1:])
            else:
                profile['last_name'] = text
            break

    # Finn fødselsdato
    for header in headers:
        text = header.get_text(strip=True)
        if text.startswith('Født:'):
            birth_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
            if birth_match:
                profile['birth_date'] = parse_birth_date(birth_match.group(1))
            break

    # Parse resultater fra tabeller
    tables = soup.find_all('table')
    current_indoor = False

    for table in tables:
        # Sjekk om vi er i innendørs-seksjonen
        prev = table.find_previous(['h3', 'h2'])
        if prev and 'INNENDØRS' in prev.get_text():
            current_indoor = True

        rows = table.find_all('tr')
        if not rows:
            continue

        # Sjekk header
        header_row = rows[0]
        headers_text = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

        if 'ØVELSE' not in headers_text:
            continue

        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue

            try:
                event = cols[0].get_text(strip=True)
                result_str = cols[1].get_text(strip=True)
                place_str = cols[2].get_text(strip=True)
                club = cols[3].get_text(strip=True)
                date_str = cols[4].get_text(strip=True)
                location = cols[5].get_text(strip=True) if len(cols) > 5 else ''

                performance, wind = parse_result_with_wind(result_str)
                place, round_type, heat_num = parse_placement(place_str)
                date = parse_date(date_str)

                if event and performance:
                    profile['results'].append({
                        'event': event,
                        'performance': performance,
                        'wind': wind,
                        'place': place,
                        'round': round_type,
                        'heat': heat_num,
                        'club': club,
                        'date': date,
                        'location': location,
                        'indoor': current_indoor
                    })

                    # Oppdater klubb fra nyeste resultat
                    if club and not profile['club']:
                        profile['club'] = club

            except Exception as e:
                logger.warning(f"Feil ved parsing av resultatrad: {e}")
                continue

    return profile


def scrape_all_landsstatistikk(seasons=[2024, 2025], classes=None):
    """Scrape all landsstatistikk for gitte sesonger.

    Hver forespørsel returnerer alle øvelser for en klasse,
    så vi trenger bare å iterere over klasser.
    """
    all_results = []

    if classes is None:
        # Alle aldersklasser
        classes = list(CLASS_CODES.keys())

    total = len(seasons) * len(classes) * 2  # *2 for ute/inne
    pbar = tqdm(total=total, desc="Scraper landsstatistikk")

    for season in seasons:
        for class_code in classes:
            for outdoor in ['Y', 'N']:
                venue = 'ute' if outdoor == 'Y' else 'inne'
                class_name = CLASS_CODES.get(class_code, {}).get('name', f'Klasse {class_code}')

                try:
                    logger.info(f"Scraper {class_name} {season} {venue}...")
                    results = scrape_landsstatistikk(
                        class_code, event_code=0, season=season, outdoor=outdoor
                    )
                    all_results.extend(results)
                    pbar.set_postfix({
                        'season': season,
                        'class': class_name[:15],
                        'venue': venue,
                        'total': len(all_results)
                    })
                except Exception as e:
                    logger.error(f"Feil ved scraping av {class_name} {season} {venue}: {e}")
                pbar.update(1)

    pbar.close()
    return all_results


def extract_unique_entities(results):
    """Ekstraher unike utøvere, klubber og stevner fra resultater."""
    athletes = {}
    clubs = set()
    meets = {}

    for r in results:
        # Utøver
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
                'gender': r.get('gender')
            }

        # Klubb
        if r.get('club'):
            clubs.add(r['club'])

        # Stevne
        meet_key = (r.get('meet_name'), r.get('date'), r.get('city'))
        if meet_key[0] and meet_key not in meets:
            meets[meet_key] = {
                'name': r.get('meet_name'),
                'date': r.get('date'),
                'city': r.get('city'),
                'indoor': r.get('indoor', False)
            }

    return {
        'athletes': list(athletes.values()),
        'clubs': [{'name': c} for c in sorted(clubs)],
        'meets': list(meets.values())
    }


def save_data(data, filename):
    """Lagre data til JSON."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Lagret {len(data) if isinstance(data, list) else 'data'} til {filepath}")


def main():
    """Hovedfunksjon."""
    logger.info("Starter scraping av minfriidrettsstatistikk.info")

    # Scrape landsstatistikk for alle klasser, 2024-2025
    logger.info("Scraper landsstatistikk...")
    results = scrape_all_landsstatistikk(
        seasons=[2024, 2025],
        classes=None  # Alle klasser
    )

    logger.info(f"Hentet {len(results)} resultater")

    # Lagre rå resultater
    save_data(results, 'results_raw.json')

    # Ekstraher unike entiteter
    entities = extract_unique_entities(results)

    save_data(entities['athletes'], 'athletes.json')
    save_data(entities['clubs'], 'clubs.json')
    save_data(entities['meets'], 'meets.json')

    logger.info(f"""
    Scraping fullført!
    - Resultater: {len(results)}
    - Utøvere: {len(entities['athletes'])}
    - Klubber: {len(entities['clubs'])}
    - Stevner: {len(entities['meets'])}

    Filer lagret i: {OUTPUT_DIR}
    """)

    # Lagre også som CSV
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_DIR / 'results_raw.csv', index=False, encoding='utf-8')
    logger.info(f"Lagret CSV til {OUTPUT_DIR / 'results_raw.csv'}")


if __name__ == '__main__':
    main()
