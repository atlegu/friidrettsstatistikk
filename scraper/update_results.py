"""
Unified update script: scrapes new meets and imports results directly to Supabase.
Combines scrape_new_meets.py + import_new_meets.py into one command with no CSV intermediate.

Usage:
    python update_results.py              # Auto-detect season, update everything
    python update_results.py --indoor     # Force indoor season
    python update_results.py --outdoor    # Force outdoor season
    python update_results.py --from-date 2025-12-01
    python update_results.py --dry-run    # Show what would be imported without importing
"""

import argparse
import os
import re
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
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

# ============================================================
# Configuration
# ============================================================
BASE_URL = "https://www.minfriidrettsstatistikk.info/php"
REQUEST_DELAY = 0.3  # seconds between requests
MIN_RESULTS_THRESHOLD = 10  # Meets with fewer results are considered incomplete

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# HTTP session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettLive/1.0'
})

# ============================================================
# EVENT NAME MAPPING (scraped name -> event code in DB)
# ============================================================
EVENT_NAME_TO_CODE = {
    # Sprint
    '60 meter': '60m',
    '100 meter': '100m',
    '150 meter': '150m',
    '200 meter': '200m',
    '300 meter': '300m',
    '400 meter': '400m',
    '600 meter': '600m',
    '800 meter': '800m',
    '1000 meter': '1000m',
    '1500 meter': '1500m',
    '2000 meter': '2000m',
    '3000 meter': '3000m',
    '5000 meter': '5000m',
    '10000 meter': '10000m',
    '1 mile': '1mile',

    # Hurdles
    '60 meter hekk (68,0cm)': '60mh_68cm',
    '60 meter hekk (76,2cm)': '60mh_76_2cm',
    '60 meter hekk (84,0cm)': '60mh_84cm',
    '60 meter hekk (91,4cm)': '60mh_91_4cm',
    '60 meter hekk (100cm)': '60mh_100cm',
    '60 meter hekk (106,7 cm)': '60mh_106_7cm',
    '60 meter hekk (106,7cm)': '60mh_106_7cm',

    # Jumps
    'Høyde': 'hoyde',
    'Stav': 'stav',
    'Lengde': 'lengde',
    'Tresteg': 'tresteg',

    # Standing jumps
    'Lengde uten tilløp': 'lengde_ut',
    'Høyde uten tilløp': 'hoyde_ut',
    'Tresteg uten tilløp': 'tresteg_ut',

    # Throws
    'Kule 7,26kg': 'kule_7_26kg',
    'Kule 6,0kg': 'kule_6kg',
    'Kule 5,0kg': 'kule_5kg',
    'Kule 4,0kg': 'kule_4kg',
    'Kule 3,0kg': 'kule_3kg',
    'Kule 2,0kg': 'kule_2kg',

    # Race walking
    'Kappgang 1000 meter': '1000mg',
    'Kappgang 1500 meter': '1500mg',
    'Kappgang 2000 meter': '2000mg',
    'Kappgang 3000 meter': '3000mg',

    # Zone jumps (map to base event)
    'Lengde (Sone 0,5m)': 'lengde',
    'Tresteg (Sone 0,5m)': 'tresteg',
}

SKIP_EVENTS = {
    '60 meter Racerunning',
    '60 meter Rullestol',
    '200 meter Rullestol',
    '400 meter Rullestol',
    '800 meter Rullestol',
    'VektKast 7,26Kg',
    'VektKast 9,08Kg',
    'VektKast 15,88Kg',
}

COMBINED_EVENT_PATTERNS = {
    r'4 Kamp': '4kamp',
    r'5 Kamp': '5kamp',
    r'7 Kamp': '7kamp',
}

# ============================================================
# Caches (loaded once at startup)
# ============================================================
_event_cache = {}      # event_code -> event_id
_club_cache = {}       # club_name -> club_id
_athlete_cache = {}    # (name, birth_year, gender) -> athlete_id
_meet_cache = {}       # (name, date) -> meet_id
_season_cache = {}     # (year, indoor) -> season_id


# ============================================================
# Season detection
# ============================================================

def auto_detect_season() -> Tuple[int, bool]:
    """Determine season year and indoor/outdoor from today's date.
    Dec-Mar: indoor season (next year if Dec)
    Apr-Nov: outdoor season (current year)
    Returns (year, indoor).
    """
    today = datetime.now()
    month = today.month

    if month <= 3 or month == 12:
        # Indoor season
        year = today.year if month <= 3 else today.year + 1
        return year, True
    else:
        # Outdoor season
        return today.year, False


def get_latest_meet_date() -> Optional[datetime]:
    """Get the most recent meet date from the database."""
    try:
        result = supabase.table('meets').select(
            'start_date'
        ).order('start_date', desc=True).limit(1).execute()

        if result.data:
            return datetime.strptime(result.data[0]['start_date'], '%Y-%m-%d')
    except Exception as e:
        logger.warning(f"Could not fetch latest meet date: {e}")
    return None


def determine_min_date(from_date: Optional[str], season_year: int, indoor: bool) -> datetime:
    """Determine the minimum date for scraping.
    Priority: 1) explicit --from-date, 2) latest meet in DB - 7 days, 3) season start.
    """
    if from_date:
        return datetime.strptime(from_date, '%Y-%m-%d')

    latest = get_latest_meet_date()
    if latest:
        min_date = latest - timedelta(days=7)
        logger.info(f"Latest meet in DB: {latest.strftime('%Y-%m-%d')}, using min_date: {min_date.strftime('%Y-%m-%d')}")
        return min_date

    # Fallback: season start
    if indoor:
        return datetime(season_year - 1, 12, 1)
    else:
        return datetime(season_year, 4, 1)


# ============================================================
# Scraping functions (from scrape_new_meets.py)
# ============================================================

def fetch_page(url: str, method: str = 'GET', data: dict = None) -> Optional[str]:
    """Fetch a page with rate limiting."""
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
    """Parse date from DD.MM.YYYY or DD.MM.YY format."""
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
    except Exception:
        pass
    return None


def format_date(dt: datetime) -> str:
    """Format date as YYYY-MM-DD."""
    return dt.strftime('%Y-%m-%d')


def fetch_meets_from_source(season: int, outdoor: str, min_date: datetime) -> List[Dict]:
    """Fetch all meets from minfriidrettsstatistikk.info for a season."""
    logger.info(f"Fetching meet list for season {season}, outdoor={outdoor}...")

    url = f"{BASE_URL}/Stevner.php"
    params = {'outdoor': outdoor, 'showseason': season}

    html = fetch_page(url, data=params)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    meets = []

    for link in soup.find_all('a', href=re.compile(r'posttoresultlist')):
        href = link.get('href', '')
        match = re.search(r'posttoresultlist\((\d+)\)', href)
        if not match:
            continue

        meet_id = int(match.group(1))
        meet_name = link.get_text(strip=True)

        parent_row = link.find_parent('tr')
        if not parent_row:
            continue

        cells = parent_row.find_all('td')
        if len(cells) < 4:
            continue

        date_str = cells[0].get_text(strip=True)
        arena = cells[2].get_text(strip=True) if len(cells) > 2 else ''
        location = cells[3].get_text(strip=True) if len(cells) > 3 else ''

        meet_date = parse_date(date_str)
        if not meet_date:
            continue

        if meet_date < min_date:
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

    logger.info(f"Found {len(meets)} meets from {min_date.strftime('%Y-%m-%d')} onwards")
    return meets


def get_existing_meets_from_db(min_date: datetime) -> List[Dict]:
    """Get existing meets from database with result counts."""
    try:
        result = supabase.table('meets').select(
            'id, name, city, start_date'
        ).gte('start_date', min_date.strftime('%Y-%m-%d')).execute()

        meets = []
        for m in result.data:
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
    """Normalize meet name for comparison."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name


def find_missing_meets(source_meets: List[Dict], db_meets: List[Dict]) -> List[Dict]:
    """Find meets that are missing or have too few results in database."""
    db_lookup = {}
    for m in db_meets:
        key = (normalize_meet_name(m['name']), m['date'])
        db_lookup[key] = m.get('result_count', 0)

        if ',' in m['name']:
            short_name = m['name'].split(',', 1)[1].strip()
            db_lookup[(normalize_meet_name(short_name), m['date'])] = m.get('result_count', 0)

    missing = []
    incomplete = []

    for m in source_meets:
        key = (normalize_meet_name(m['name']), m['date'])
        full_key = (normalize_meet_name(f"{m['location']}, {m['name']}"), m['date'])

        result_count = db_lookup.get(key) or db_lookup.get(full_key)

        if result_count is None:
            missing.append(m)
        elif result_count < MIN_RESULTS_THRESHOLD:
            incomplete.append(m)
            logger.info(f"  Incomplete meet: {m['name']} ({m['date']}) - only {result_count} results")

    logger.info(f"Found {len(missing)} missing meets and {len(incomplete)} incomplete meets")
    return missing + incomplete


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str]]:
    """Parse result and wind from formats like '9,17(+0,9)'."""
    if not result_str:
        return '', None

    result_str = result_str.strip()

    match = re.match(r'(.+?)\(([+-]?\d+[,.]?\d*)\)$', result_str)
    if match:
        return match.group(1).strip(), match.group(2).replace(',', '.')

    return result_str, None


def fetch_and_parse_meet_results(meet: Dict) -> List[Dict]:
    """Fetch and parse results for a single meet. Returns list of result dicts."""
    url = f"{BASE_URL}/StevneResultater.php"
    data = {'competition': meet['external_id']}
    html = fetch_page(url, method='POST', data=data)

    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    results = []

    current_event = None
    current_class = None

    for element in soup.find_all(['div', 'table']):
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                current_class = h2.get_text(strip=True)

        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)

        elif element.name == 'table' and current_event:
            rows = element.find_all('tr')

            for row in rows:
                if row.find('th'):
                    continue

                cells = row.find_all('td')
                if len(cells) < 4:
                    continue

                try:
                    place_text = cells[0].get_text(strip=True)
                    result_raw = cells[1].get_text(strip=True)
                    name_text = cells[2].get_text(strip=True)
                    club = cells[3].get_text(strip=True)

                    place = None
                    place_match = re.match(r'^(\d+)', place_text)
                    if place_match:
                        place = int(place_match.group(1))

                    result, wind = parse_result_wind(result_raw)

                    name = name_text
                    birth_year = None
                    year_match = re.search(r'\((\d{4})\)$', name_text)
                    if year_match:
                        birth_year = int(year_match.group(1))
                        name = name_text[:year_match.start()].strip()

                    if not name or not result:
                        continue

                    if result.upper() in ['DNS', 'DNF', 'DQ', 'NM', '-']:
                        continue

                    results.append({
                        'meet_external_id': meet['external_id'],
                        'meet_name': meet['name'],
                        'meet_date': meet['date'],
                        'location': meet.get('location', ''),
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


# ============================================================
# Import functions (from import_new_meets.py)
# ============================================================

def load_events():
    """Load all events from database into cache."""
    global _event_cache
    response = supabase.table('events').select('id, code, name').execute()
    for e in response.data:
        _event_cache[e['code']] = e['id']
        _event_cache[e['name']] = e['id']
    logger.info(f"Loaded {len(response.data)} events")


def load_seasons():
    """Load all seasons from database into cache."""
    global _season_cache
    response = supabase.table('seasons').select('id, year, indoor').execute()
    for s in response.data:
        key = (s['year'], s['indoor'])
        _season_cache[key] = s['id']
    logger.info(f"Loaded {len(response.data)} seasons")


def load_clubs():
    """Load all clubs from database into cache."""
    global _club_cache
    offset = 0
    chunk_size = 1000
    total = 0
    while True:
        response = supabase.table('clubs').select('id, name').range(offset, offset + chunk_size - 1).execute()
        if not response.data:
            break
        for c in response.data:
            _club_cache[c['name']] = c['id']
        total += len(response.data)
        offset += chunk_size
        if len(response.data) < chunk_size:
            break
    logger.info(f"Loaded {total} clubs")


def load_athletes():
    """Load athletes for fast matching (paginated)."""
    global _athlete_cache
    offset = 0
    chunk_size = 1000
    total = 0

    while True:
        response = supabase.table('athletes').select(
            'id, first_name, last_name, birth_year, gender'
        ).range(offset, offset + chunk_size - 1).execute()

        if not response.data:
            break

        for a in response.data:
            full_name = f"{a['first_name']} {a['last_name']}"
            key = (full_name.lower(), a.get('birth_year'), a.get('gender'))
            _athlete_cache[key] = a['id']

        total += len(response.data)
        offset += chunk_size

        if len(response.data) < chunk_size:
            break

        if total % 10000 == 0:
            logger.info(f"  ...loaded {total} athletes so far")

    logger.info(f"Loaded {total} athletes into cache")


def fix_performance_format(result_str):
    """Convert European period-separated time format to colon-separated.
    E.g., '3.34.02' -> '3:34.02', '16.08.70' -> '16:08.70'
    """
    if not result_str:
        return result_str

    match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{1,2})$', result_str)
    if match:
        minutes, seconds, hundredths = match.groups()
        return f"{minutes}:{seconds}.{hundredths}"

    return result_str


def get_event_id(event_name):
    """Get event ID from scraped event name."""
    if event_name in SKIP_EVENTS:
        return None

    for pattern, code in COMBINED_EVENT_PATTERNS.items():
        if event_name.startswith(pattern):
            return _event_cache.get(code)

    code = EVENT_NAME_TO_CODE.get(event_name)
    if code:
        return _event_cache.get(code)

    return _event_cache.get(event_name)


def get_gender(event_class):
    """Extract gender from event class string."""
    if not event_class:
        return None
    ec = event_class.lower()
    if ec.startswith(('menn', 'gutter', 'ms ', 'g-')):
        return 'M'
    if ec.startswith(('kvinner', 'jenter', 'ks ', 'k-')):
        return 'F'
    return None


def get_season_id(date_str, indoor):
    """Get season ID from date and indoor flag."""
    year = int(date_str[:4])
    if indoor and int(date_str[5:7]) >= 10:
        year += 1
    key = (year, indoor)
    return _season_cache.get(key)


def get_or_create_club(name):
    """Get or create a club, return its ID."""
    if not name or name.strip() == '':
        return None

    name = name.strip()
    if name in _club_cache:
        return _club_cache[name]

    try:
        response = supabase.table('clubs').insert({'name': name}).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
    except Exception as e:
        response = supabase.table('clubs').select('id').eq('name', name).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
        logger.warning(f"Failed to create club '{name}': {e}")

    return None


def get_or_create_meet(name, date, location, indoor):
    """Get or create a meet, return its ID."""
    cache_key = (name, date)
    if cache_key in _meet_cache:
        return _meet_cache[cache_key]

    response = supabase.table('meets').select('id').eq(
        'name', name
    ).eq('start_date', date).execute()

    if response.data:
        _meet_cache[cache_key] = response.data[0]['id']
        return _meet_cache[cache_key]

    if location:
        city_name = f"{location}, {name}"
        response = supabase.table('meets').select('id').eq(
            'name', city_name
        ).eq('start_date', date).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            return _meet_cache[cache_key]

    year = int(date[:4])
    if indoor and int(date[5:7]) >= 10:
        year += 1
    season_id = _season_cache.get((year, indoor))

    city = location.split('/')[0] if location else ''

    country = 'NOR'
    if location and '/' in location:
        country_code = location.split('/')[-1].strip()
        country_map = {
            'FRA': 'FRA', 'GER': 'GER', 'SUI': 'SUI', 'SWE': 'SWE',
            'DEN': 'DEN', 'FIN': 'FIN', 'USA': 'USA', 'GBR': 'GBR',
            'NOR': 'NOR', 'EST': 'EST', 'NED': 'NED', 'BEL': 'BEL',
            'POL': 'POL', 'CZE': 'CZE', 'AUT': 'AUT', 'ITA': 'ITA',
            'ESP': 'ESP', 'POR': 'POR', 'HUN': 'HUN', 'SVK': 'SVK',
        }
        country = country_map.get(country_code, country_code)

    meet_data = {
        'name': name,
        'start_date': date,
        'city': city,
        'country': country,
        'indoor': indoor,
        'season_id': season_id,
    }

    try:
        response = supabase.table('meets').insert(meet_data).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            logger.info(f"  Created meet: {name} ({date}) in {city}")
            return _meet_cache[cache_key]
    except Exception as e:
        logger.warning(f"Failed to create meet '{name}': {e}")

    return None


def match_athlete(name, birth_year, gender):
    """Match an athlete by name, birth_year, and gender."""
    if not name:
        return None

    key = (name.lower(), birth_year, gender)
    athlete_id = _athlete_cache.get(key)
    if athlete_id:
        return athlete_id

    # Try without gender
    for cached_key, cached_id in _athlete_cache.items():
        if cached_key[0] == name.lower() and cached_key[1] == birth_year:
            return cached_id

    return None


def create_athlete(name, birth_year, gender, club_name):
    """Create a new athlete in the database."""
    name_parts = name.split() if name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    club_id = get_or_create_club(club_name) if club_name else None

    athlete_data = {
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'birth_year': birth_year,
        'current_club_id': club_id,
    }

    try:
        response = supabase.table('athletes').insert(athlete_data).execute()
        if response.data:
            athlete_id = response.data[0]['id']
            key = (name.lower(), birth_year, gender)
            _athlete_cache[key] = athlete_id
            return athlete_id
    except Exception as e:
        logger.debug(f"Failed to create athlete '{name}': {e}")

    return None


_athlete_club_updated = set()  # Track already-updated athletes this run


def _update_athlete_club(athlete_id, club_id):
    """Update athlete's current_club_id if changed. Only updates once per run."""
    if athlete_id in _athlete_club_updated:
        return
    _athlete_club_updated.add(athlete_id)
    try:
        supabase.table('athletes').update(
            {'current_club_id': club_id}
        ).eq('id', athlete_id).neq('current_club_id', club_id).execute()
    except Exception:
        pass  # Non-critical, don't fail the import


# ============================================================
# Import a single meet's results directly to DB
# ============================================================

def import_meet_results(meet_results: List[Dict], dry_run: bool = False) -> Dict:
    """Import scraped results for one meet directly to the database.
    Returns stats dict for this meet.
    """
    stats = {
        'imported': 0,
        'matched_existing_athlete': 0,
        'created_new_athlete': 0,
        'skipped_no_event': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'errors': 0,
        'new_meets': 0,
    }
    unmapped_events = defaultdict(int)

    if not meet_results:
        return stats

    # All results are for the same meet
    first = meet_results[0]
    meet_name = first['meet_name']
    meet_date = first['meet_date']
    location = first.get('location', '')
    is_indoor = first['is_indoor']

    if dry_run:
        logger.info(f"  [DRY RUN] Would import {len(meet_results)} results for {meet_name} ({meet_date})")
        stats['imported'] = len(meet_results)
        return stats

    # Get or create meet
    meet_id = get_or_create_meet(meet_name, meet_date, location, is_indoor)
    if not meet_id:
        stats['skipped_no_meet'] = len(meet_results)
        return stats

    # Check if this meet was newly created (not in cache before this call)
    # We track this via _meet_cache side effects in get_or_create_meet

    season_id = get_season_id(meet_date, is_indoor)

    result_batch = []

    for row in meet_results:
        event_name = row['event']
        event_class = row['event_class']

        event_id = get_event_id(event_name)
        if not event_id:
            if event_name not in SKIP_EVENTS:
                unmapped_events[event_name] += 1
            stats['skipped_no_event'] += 1
            continue

        gender = get_gender(event_class)
        birth_year = row.get('birth_year')

        athlete_name = row['athlete_name']
        athlete_id = match_athlete(athlete_name, birth_year, gender)

        club_id = get_or_create_club(row.get('club'))

        if athlete_id:
            stats['matched_existing_athlete'] += 1
            # Update current_club_id to this meet's club (latest data)
            if club_id:
                _update_athlete_club(athlete_id, club_id)
        else:
            athlete_id = create_athlete(athlete_name, birth_year, gender, row.get('club'))
            if athlete_id:
                stats['created_new_athlete'] += 1
            else:
                stats['skipped_no_athlete'] += 1
                continue

        result_str = fix_performance_format(row['result'])

        place = row.get('place')

        wind = None
        if row.get('wind'):
            try:
                wind = float(row['wind'])
            except ValueError:
                pass

        result_data = {
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': result_str,
            'date': meet_date,
            'wind': wind,
            'place': place,
            'club_id': club_id,
            'status': 'OK',
            'verified': True,
        }

        if wind is not None and wind > 2.0:
            result_data['is_wind_legal'] = False

        result_batch.append(result_data)

    # Insert batch
    if result_batch:
        try:
            for i in range(0, len(result_batch), 50):
                chunk = result_batch[i:i+50]
                supabase.table('results').insert(chunk).execute()
                stats['imported'] += len(chunk)
            logger.info(f"  Imported {len(result_batch)} results for {meet_name} ({meet_date})")
        except Exception as e:
            logger.warning(f"  Batch failed for {meet_name}, trying one-by-one: {e}")
            for result_data in result_batch:
                try:
                    supabase.table('results').insert(result_data).execute()
                    stats['imported'] += 1
                except Exception as e2:
                    logger.debug(f"    Failed single: {result_data['performance']} - {e2}")
                    stats['errors'] += 1

    if unmapped_events:
        for event, count in sorted(unmapped_events.items(), key=lambda x: -x[1]):
            logger.warning(f"  Unmapped event: {event} ({count} results)")

    return stats


# ============================================================
# Main orchestration
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Update friidrett results: scrape new meets and import to database.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--indoor', action='store_true', help='Force indoor season')
    group.add_argument('--outdoor', action='store_true', help='Force outdoor season')

    parser.add_argument('--season', type=int, help='Season year (e.g. 2026)')
    parser.add_argument('--from-date', type=str, help='Start date (YYYY-MM-DD), overrides auto-detection')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without importing')

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine season
    auto_year, auto_indoor = auto_detect_season()

    if args.indoor:
        indoor = True
    elif args.outdoor:
        indoor = False
    else:
        indoor = auto_indoor

    season_year = args.season or auto_year
    outdoor_flag = 'N' if indoor else 'Y'
    season_label = f"{season_year} {'indoor' if indoor else 'outdoor'}"

    logger.info("=" * 60)
    logger.info(f"UPDATE RESULTS — Season: {season_label}")
    if args.dry_run:
        logger.info("*** DRY RUN — no changes will be made ***")
    logger.info("=" * 60)

    # Determine min date
    min_date = determine_min_date(args.from_date, season_year, indoor)
    logger.info(f"Looking for meets from {min_date.strftime('%Y-%m-%d')} onwards")

    # Load reference data for import
    logger.info("\nLoading reference data...")
    load_events()
    load_seasons()
    load_clubs()
    load_athletes()

    # Step 1: Fetch source meets
    source_meets = fetch_meets_from_source(season_year, outdoor_flag, min_date)

    # Step 2: Get existing meets from DB
    db_meets = get_existing_meets_from_db(min_date)

    # Step 3: Find missing/incomplete meets
    missing_meets = find_missing_meets(source_meets, db_meets)

    if not missing_meets:
        logger.info("\nNo missing meets found — database is up to date!")
        logger.info("=" * 60)
        return

    # Step 4: Scrape + import each meet
    logger.info(f"\nProcessing {len(missing_meets)} missing/incomplete meets...")

    totals = {
        'imported': 0,
        'matched_existing_athlete': 0,
        'created_new_athlete': 0,
        'skipped_no_event': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'errors': 0,
        'new_meets': 0,
        'meets_processed': 0,
        'total_scraped': 0,
    }

    for i, meet in enumerate(missing_meets):
        logger.info(f"\n[{i+1}/{len(missing_meets)}] {meet['name']} ({meet['date']})")

        # Scrape results
        results = fetch_and_parse_meet_results(meet)
        totals['total_scraped'] += len(results)

        if not results:
            logger.warning(f"  No results found")
            continue

        logger.info(f"  Scraped {len(results)} results")

        # Import directly
        meet_stats = import_meet_results(results, dry_run=args.dry_run)
        totals['meets_processed'] += 1

        for key in ['imported', 'matched_existing_athlete', 'created_new_athlete',
                     'skipped_no_event', 'skipped_no_athlete', 'skipped_no_meet', 'errors']:
            totals[key] += meet_stats.get(key, 0)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("UPDATE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Season: {season_label}")
    logger.info(f"Source meets found: {len(source_meets)}")
    logger.info(f"Already in database: {len(db_meets)}")
    logger.info(f"Missing/incomplete: {len(missing_meets)}")
    logger.info(f"Meets processed: {totals['meets_processed']}")
    logger.info(f"Results scraped: {totals['total_scraped']}")
    logger.info(f"Results imported: {totals['imported']}")
    logger.info(f"  Matched athletes: {totals['matched_existing_athlete']}")
    logger.info(f"  New athletes created: {totals['created_new_athlete']}")
    logger.info(f"  Skipped (no event mapping): {totals['skipped_no_event']}")
    logger.info(f"  Skipped (no athlete): {totals['skipped_no_athlete']}")
    logger.info(f"  Errors: {totals['errors']}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
