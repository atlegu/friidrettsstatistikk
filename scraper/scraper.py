"""
Scraper for minfriidrettsstatistikk.info
Henter utøvere, klubber og resultater for import til Supabase.
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

# Rate limiting - vær snill mot serveren
REQUEST_DELAY = 0.5  # sekunder mellom requests

# Session for å bevare cookies
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettsstatistikkScraper/1.0'
})


def fetch_page(url, params=None, method='GET', data=None):
    """Hent en side med rate limiting."""
    time.sleep(REQUEST_DELAY)
    try:
        if method == 'GET':
            response = session.get(url, params=params, timeout=30)
        else:
            response = session.post(url, data=data, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        logger.error(f"Feil ved henting av {url}: {e}")
        return None


def parse_date(date_str):
    """Konverter dato fra DD.MM.YY til YYYY-MM-DD."""
    if not date_str:
        return None
    try:
        # Prøv DD.MM.YY
        if len(date_str.split('.')[-1]) == 2:
            dt = datetime.strptime(date_str, '%d.%m.%y')
            # Håndter århundre (00-30 = 2000s, 31-99 = 1900s)
            if dt.year > 2030:
                dt = dt.replace(year=dt.year - 100)
            return dt.strftime('%Y-%m-%d')
        # Prøv DD.MM.YYYY
        dt = datetime.strptime(date_str, '%d.%m.%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None


def parse_birth_date(date_str):
    """Konverter fødselsdato fra DD.MM.YYYY til YYYY-MM-DD."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str.strip(), '%d.%m.%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None


def extract_athlete_id(href):
    """Ekstraher utøver-ID fra lenke."""
    if not href:
        return None
    match = re.search(r'showathl=(\d+)', href)
    return int(match.group(1)) if match else None


def scrape_athletes_by_letter(letter):
    """Hent alle utøvere som starter på en gitt bokstav."""
    logger.info(f"Henter utøvere som starter på '{letter}'...")

    url = f"{BASE_URL}/UtoverSok.php"
    params = {'LicenseNo': '', 'athlname': letter}

    html = fetch_page(url, params=params)
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    athletes = []

    # Finn alle lenker til utøverprofiler
    for link in soup.find_all('a', href=re.compile(r'UtoverStatistikk\.php\?showathl=')):
        athlete_id = extract_athlete_id(link.get('href'))
        name = link.get_text(strip=True)

        if athlete_id and name:
            # Finn tilhørende info (klubb, født) - typisk i samme rad/element
            parent = link.find_parent('tr') or link.find_parent('div')
            club = ''
            birth_date = ''

            if parent:
                text = parent.get_text()
                # Prøv å ekstrahere klubb og fødselsdato fra teksten
                # Dette må tilpasses basert på faktisk HTML-struktur

            athletes.append({
                'external_id': athlete_id,
                'name': name,
                'club': club,
                'birth_date': birth_date
            })

    logger.info(f"  Fant {len(athletes)} utøvere på '{letter}'")
    return athletes


def scrape_athlete_profile(athlete_id):
    """Hent komplett profil for en utøver."""
    url = f"{BASE_URL}/UtoverStatistikk.php"
    params = {
        'showathl': athlete_id,
        'showevent': 0,
        'showseason': 0,  # Alle sesonger
        'outdoor': 'A',   # Både inne og ute
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
        'gender': '',
        'birth_date': None,
        'club': '',
        'results': []
    }

    # Finn utøvernavn - typisk i en header
    # Dette må tilpasses basert på faktisk HTML-struktur
    header = soup.find('h1') or soup.find('h2')
    if header:
        full_name = header.get_text(strip=True)
        parts = full_name.split()
        if len(parts) >= 2:
            profile['first_name'] = parts[0]
            profile['last_name'] = ' '.join(parts[1:])
        else:
            profile['last_name'] = full_name

    # Finn fødselsdato
    birth_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', soup.get_text())
    if birth_match:
        profile['birth_date'] = parse_birth_date(birth_match.group(1))

    # Finn klubb
    club_elem = soup.find(string=re.compile(r'Klubb:'))
    if club_elem:
        club_text = club_elem.find_next(string=True)
        if club_text:
            profile['club'] = club_text.strip()

    # Parse resultater - finn alle tabeller med resultater
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 4:
                result = parse_result_row(cols)
                if result:
                    profile['results'].append(result)

    return profile


def parse_result_row(cols):
    """Parse en resultatrad fra tabellen."""
    try:
        # Typisk struktur: Øvelse | Resultat | Vind | Stevne | Dato | Sted
        # Dette må tilpasses basert på faktisk HTML-struktur
        result = {
            'event': cols[0].get_text(strip=True) if len(cols) > 0 else '',
            'performance': cols[1].get_text(strip=True) if len(cols) > 1 else '',
            'wind': None,
            'meet_name': '',
            'date': None,
            'place': None
        }

        # Ekstraher vind fra resultat (f.eks. "10.45 (+1.2)")
        perf_text = result['performance']
        wind_match = re.search(r'\(([\+\-]?\d+[\.,]\d+)\)', perf_text)
        if wind_match:
            result['wind'] = float(wind_match.group(1).replace(',', '.'))
            result['performance'] = re.sub(r'\s*\([^\)]+\)', '', perf_text).strip()

        # Konverter komma til punktum i resultat
        result['performance'] = result['performance'].replace(',', '.')

        return result if result['event'] and result['performance'] else None
    except Exception as e:
        logger.warning(f"Feil ved parsing av resultatrad: {e}")
        return None


def scrape_all_athletes():
    """Hent alle utøvere fra A-Å."""
    all_athletes = []
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ')

    for letter in tqdm(letters, desc="Henter utøvere"):
        athletes = scrape_athletes_by_letter(letter)
        all_athletes.extend(athletes)

    # Fjern duplikater basert på ID
    seen = set()
    unique_athletes = []
    for a in all_athletes:
        if a['external_id'] not in seen:
            seen.add(a['external_id'])
            unique_athletes.append(a)

    logger.info(f"Totalt {len(unique_athletes)} unike utøvere funnet")
    return unique_athletes


def scrape_athlete_profiles(athlete_ids, limit=None):
    """Hent profiler for alle utøvere."""
    profiles = []

    if limit:
        athlete_ids = athlete_ids[:limit]

    for athlete_id in tqdm(athlete_ids, desc="Henter profiler"):
        profile = scrape_athlete_profile(athlete_id)
        if profile:
            profiles.append(profile)

    return profiles


def save_to_json(data, filename):
    """Lagre data til JSON-fil."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Lagret {len(data)} elementer til {filepath}")


def save_to_csv(data, filename):
    """Lagre data til CSV-fil."""
    filepath = OUTPUT_DIR / filename
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding='utf-8')
    logger.info(f"Lagret {len(data)} rader til {filepath}")


# ============================================================
# KLASSE-KODER for minfriidrettsstatistikk.info
# ============================================================
CLASS_CODES = {
    # Senior
    11: {'name': 'Menn senior', 'gender': 'M', 'age_group': 'Senior'},
    12: {'name': 'Kvinner senior', 'gender': 'F', 'age_group': 'Senior'},
    # U23
    21: {'name': 'Menn U23', 'gender': 'M', 'age_group': 'U23'},
    22: {'name': 'Kvinner U23', 'gender': 'F', 'age_group': 'U23'},
    # U20
    31: {'name': 'Menn U20', 'gender': 'M', 'age_group': 'U20'},
    32: {'name': 'Kvinner U20', 'gender': 'F', 'age_group': 'U20'},
    # U18
    41: {'name': 'Gutter U18', 'gender': 'M', 'age_group': 'U18'},
    42: {'name': 'Jenter U18', 'gender': 'F', 'age_group': 'U18'},
    # Yngre
    51: {'name': 'Gutter 15', 'gender': 'M', 'age_group': 'G15'},
    52: {'name': 'Jenter 15', 'gender': 'F', 'age_group': 'J15'},
    61: {'name': 'Gutter 14', 'gender': 'M', 'age_group': 'G14'},
    62: {'name': 'Jenter 14', 'gender': 'F', 'age_group': 'J14'},
    71: {'name': 'Gutter 13', 'gender': 'M', 'age_group': 'G13'},
    72: {'name': 'Jenter 13', 'gender': 'F', 'age_group': 'J13'},
}

# ============================================================
# ØVELSE-KODER (må mappes til våre event-koder)
# ============================================================
EVENT_CODES = {
    1: '60m',
    2: '100m',
    3: '200m',
    4: '400m',
    5: '800m',
    6: '1500m',
    7: '3000m',
    8: '5000m',
    9: '10000m',
    10: '60mh',
    11: '100mh',
    12: '110mh',
    13: '400mh',
    14: '3000mhinder',
    15: 'hoyde',
    16: 'stav',
    17: 'lengde',
    18: 'tresteg',
    19: 'kule',
    20: 'diskos',
    21: 'slegge',
    22: 'spyd',
    23: '5kamp',
    24: '7kamp',
    25: '10kamp',
    # ... flere øvelser må mappes
}


def main():
    """Hovedfunksjon for scraping."""
    logger.info("Starter scraping av minfriidrettsstatistikk.info")

    # Steg 1: Hent alle utøver-IDer
    logger.info("Steg 1: Henter utøverliste...")
    athletes = scrape_all_athletes()
    save_to_json(athletes, 'athletes_list.json')

    # Steg 2: Hent profiler for alle utøvere (kan ta lang tid!)
    logger.info("Steg 2: Henter utøverprofiler...")
    athlete_ids = [a['external_id'] for a in athletes]

    # For testing: Begrens til første 100
    # profiles = scrape_athlete_profiles(athlete_ids, limit=100)
    profiles = scrape_athlete_profiles(athlete_ids)
    save_to_json(profiles, 'athlete_profiles.json')

    # Steg 3: Ekstraher unik data
    logger.info("Steg 3: Prosesserer data...")

    # Ekstraher klubber
    clubs = set()
    for p in profiles:
        if p.get('club'):
            clubs.add(p['club'])
    clubs_list = [{'name': c} for c in sorted(clubs)]
    save_to_json(clubs_list, 'clubs.json')

    # Ekstraher stevner
    meets = set()
    for p in profiles:
        for r in p.get('results', []):
            if r.get('meet_name'):
                meets.add(r['meet_name'])
    meets_list = [{'name': m} for m in sorted(meets)]
    save_to_json(meets_list, 'meets.json')

    # Flatten resultater
    all_results = []
    for p in profiles:
        for r in p.get('results', []):
            result = {
                'athlete_external_id': p['external_id'],
                'athlete_name': f"{p.get('first_name', '')} {p.get('last_name', '')}".strip(),
                **r
            }
            all_results.append(result)
    save_to_json(all_results, 'results.json')
    save_to_csv(all_results, 'results.csv')

    logger.info(f"""
    Scraping fullført!
    - Utøvere: {len(profiles)}
    - Klubber: {len(clubs_list)}
    - Stevner: {len(meets_list)}
    - Resultater: {len(all_results)}

    Filer lagret i: {OUTPUT_DIR}
    """)


if __name__ == '__main__':
    main()
