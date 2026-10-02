#!/usr/bin/env python3
"""
Import youth statistics (10-12 year olds) from minfriidrettsstatistikk.info.

Scrapes the password-protected LandsStatistikkAdv.php pages for age classes
Gutter 10, 11, 12 and Jenter 10, 11, 12.

Usage:
    python import_youth_stats.py --dry-run
    python import_youth_stats.py --age 11 --gender M --outdoor
    python import_youth_stats.py --season 2024 --dry-run
    python import_youth_stats.py --all
"""

import argparse
import logging
import os
import re
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, f'import_youth_stats_{timestamp}.log')),
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# Configuration
# ============================================================

BASE_URL = 'https://www.minfriidrettsstatistikk.info/php'
LOGIN_URL = f'{BASE_URL}/sjekkinnloggingstatistikk.php'
STATS_URL = f'{BASE_URL}/LandsStatistikkAdv.php'
REQUEST_DELAY = 0.3

USERNAME = 'atle'
PASSWORD = 'atleFriidrett16'

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettLive/1.0'
})

# showclass values for each age group
AGE_CLASS_MAP = {
    ('M', 10): 1,   # Gutter 10
    ('M', 11): 2,   # Gutter 11
    ('M', 12): 3,   # Gutter 12
    ('F', 10): 12,  # Jenter 10
    ('F', 11): 13,  # Jenter 11
    ('F', 12): 14,  # Jenter 12
}

# ============================================================
# Event mapping: scraped name -> event code in DB
# Extends the base mapping with youth-specific events
# ============================================================

EVENT_NAME_TO_CODE = {
    # Sprint
    '30 meter': '30m',
    '40 meter': '40m',
    '50 meter': '50m',
    '55 meter': '55m',
    '60 meter': '60m',
    '80 meter': '80m',
    '100 meter': '100m',
    '150 meter': '150m',
    '200 meter': '200m',
    '300 meter': '300m',
    '400 meter': '400m',
    '600 meter': '600m',
    '800 meter': '800m',
    '1000 meter': '1000m',
    '1500 meter': '1500m',
    '1 mile': '1mile',
    '2000 meter': '2000m',
    '3000 meter': '3000m',
    '5000 meter': '5000m',
    '10000 meter': '10000m',

    # Hurdles
    '60 meter hekk (60cm)': '60mh_60cm',
    '60 meter hekk (68,0cm)': '60mh_68cm',
    '60 meter hekk (76,2cm)': '60mh_76_2cm',
    '200 meter hekk (68,0cm)': '200mh_68cm',
    '200 meter hekk (76,2cm)': '200mh_76_2cm',
    '300 meter hekk (68,0cm)': '300mh_68cm',
    '300 meter hekk (76,2cm)': '300mh_76_2cm',

    # Jumps
    'Høyde': 'hoyde',
    'Stav': 'stav',
    'Lengde': 'lengde',
    'Lengde (Sone 0,5m)': 'lengde',
    'Tresteg': 'tresteg',
    'Tresteg (Sone 0,5m)': 'tresteg',

    # Throws - kule
    'Kule 2,0kg': 'kule_2kg',
    'Kule 3,0kg': 'kule_3kg',
    'Kule 4,0kg': 'kule_4kg',
    'Kule 5,0kg': 'kule_5kg',

    # Throws - diskos (DB codes)
    'Diskos 600gram': 'diskos_600g',
    'Diskos 750gram': 'diskos_750g',
    'Diskos 1,0kg': 'diskos_1kg',

    # Throws - slegge (exact DB codes with wire length variants)
    'Slegge 2,0kg/110cm': 'slegge_2kg',
    'Slegge 3,0kg/110cm': 'slegge_30kg/110cm',
    'Slegge 3,0Kg (119,5cm)': 'slegge_30kg_1195cm',
    'Slegge 4,0kg/119,5cm': 'slegge_40kg/1195cm',

    # Throws - spyd
    'Spyd': 'spyd',
    'Spyd 400gram': 'spyd_400g',
    'Spyd 600gram': 'spyd_600g',
    'Spyd 700gram': 'spyd_700g',

    # Throws - ball (DB codes use underscore naming)
    'Liten Ball 80gram': 'liten_ball_80gram',
    'Liten Ball 150gram': 'liten_ball_150gram',
    'Liten Ball 180gram': 'liten_ball_180gram',
    'Liten Ball 300gram': 'liten_ball_300gram',
    'Slengball 750gr': 'slengball_750gr',
    'Slengball 1,0Kg': 'slengball_10kg',

    # Throws - vektkast (DB codes)
    'VektKast': 'vektkast',
    'VektKast4,0kg': 'vektkast40kg',
    'VektKast 5,45Kg': 'vektkast_545kg',

    # Race walking (DB uses kappgang_ prefix)
    'Kappgang 400 meter': 'kappgang_400_m',
    'Kappgang 600 meter': 'kappgang_600_m',
    'Kappgang 1000 meter': 'kappgang_1000_m',
    'Kappgang 1500 meter': 'kappgang_1500_m',
    'Kappgang 2000 meter': 'kappgang_2000_m',
    'Kappgang 3000 meter': 'kappgang_3000_m',
    'Kappgang 1 km': 'kappgang_1_km',
    'Kappgang 1,5 km': 'kappgang_1500_m',
    'Kappgang 3 km': 'kappgang_3_km',

    # Combined events - specific DB name matches
    # These use the full event name including discipline list.
    # load_events() caches by name too, so exact name match works.
    'Kast 5 Kamp (Slegge-Kule-Diskos-Spyd-Vektkast) Ungdom':
        'kast_5_k_slegge-kule-diskos-spyd-vektkast_ungdom',
}

SKIP_EVENTS = {
    '60 meter Racerunning',
    '60 meter Rullestol',
    '200 meter Rullestol',
}

# Sections to skip (under h5/h6) — these are not official results
SKIP_SECTIONS = {
    'Ikke godkjente resultater',
    'For mye vind/Assisting wind',
    'Manglende informasjon om vind',
    'Feilplassert målkamera',
    'Bane med for stor omkrets/Oversized track',
}

# ============================================================
# Caches
# ============================================================
_event_cache = {}
_club_cache = {}
_athlete_cache = {}
_meet_cache = {}
_season_cache = {}

# ============================================================
# Login
# ============================================================

def login() -> bool:
    """Log in to minfriidrettsstatistikk.info and store session cookies."""
    logger.info("Logging in to minfriidrettsstatistikk.info...")
    try:
        response = session.post(LOGIN_URL, data={
            'mittbrukernavn': USERNAME,
            'mittpassord': PASSWORD,
            'Submit': 'Logg inn',
        }, timeout=30)
        if 'Landsoversikt' in response.text or '<h4' in response.text:
            logger.info("Login successful")
            return True
        else:
            logger.error("Login failed — check credentials")
            return False
    except requests.RequestException as e:
        logger.error(f"Login error: {e}")
        return False


# ============================================================
# Fetch and parse
# ============================================================

def fetch_stats_page(showclass: int, outdoor: str = 'Y', season: int = 0) -> Optional[str]:
    """Fetch a statistics page. Returns HTML or None."""
    time.sleep(REQUEST_DELAY)
    params = {
        'showclass': showclass,
        'showevent': 0,  # all events
        'showseason': season,
        'outdoor': outdoor,
    }
    try:
        response = session.get(STATS_URL, params=params, timeout=60)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch stats page (class={showclass}): {e}")
        return None


def parse_result_wind(text: str) -> Tuple[Optional[str], Optional[float]]:
    """Parse result string like '8,20(+1,0)' into (result, wind).
    Handles unusual wind formats: (+0), (-1), (+.05), (:+0.8), (+04).
    """
    if not text:
        return None, None

    text = text.strip()

    # Skip non-results
    if text.upper() in ('DNS', 'DNF', 'DQ', 'NM', '-', ''):
        return None, None

    wind = None
    # Match wind in parens: optional leading colon, optional sign, optional digits, optional decimal, digits
    # Examples: (+1.2), (-0.3), (+0), (-1), (+.05), (:+0.8), (+04)
    wind_match = re.search(r'\(:?\s*([+-]?\d*[.,]?\d+)\s*\)', text)
    if wind_match:
        wind_str = wind_match.group(1).replace(',', '.')
        # Handle leading-decimal cases like '.05'
        if wind_str.startswith('.') or wind_str.startswith('+.') or wind_str.startswith('-.'):
            wind_str = wind_str.replace('+.', '+0.').replace('-.', '-0.')
            if wind_str.startswith('.'):
                wind_str = '0' + wind_str
        try:
            wind = float(wind_str)
        except ValueError:
            pass
        text = text[:wind_match.start()].strip()

    # Handle (ok) wind marker
    ok_match = re.search(r'\(ok\)', text, re.IGNORECASE)
    if ok_match:
        text = text[:ok_match.start()].strip()

    # Replace comma decimal separator with period
    result = text.replace(',', '.')

    if not result:
        return None, None

    # Sanity check: result should be a number, possibly with colon for minutes
    # Valid patterns: '10.45', '3:34.02', '12.3', '1.85', etc.
    # Invalid: '6.6Magnus Seljeset...' (malformed concatenated row)
    if not re.match(r'^\d+([.:]\d+)*$', result):
        return None, None

    return result, wind


def fix_performance_format(result_str: str) -> str:
    """Convert '3.34.02' -> '3:34.02' for times with period separators."""
    if not result_str:
        return result_str
    match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{1,2})$', result_str)
    if match:
        minutes, seconds, hundredths = match.groups()
        return f"{minutes}:{seconds}.{hundredths}"
    return result_str


def parse_birth_date(date_str: str) -> Tuple[Optional[str], Optional[int]]:
    """Parse birth date string. Returns (iso_date_or_none, birth_year).
    Handles: '17.06.12', '25.09.00', '12' (just year), '04', etc.
    """
    if not date_str:
        return None, None

    date_str = date_str.strip()

    # Full date: DD.MM.YY or DD.MM.YYYY
    parts = date_str.split('.')
    if len(parts) == 3:
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            iso = f"{year:04d}-{month:02d}-{day:02d}"
            return iso, year
        except (ValueError, IndexError):
            pass

    # Just a 2-digit year: '12', '04', '99'
    if re.match(r'^\d{1,2}$', date_str):
        try:
            y = int(date_str)
            year = 2000 + y if y < 50 else 1900 + y
            return None, year
        except ValueError:
            pass

    return None, None


def parse_meet_location(sted: str) -> Tuple[str, str, str]:
    """Parse 'City, Meet Name' or 'City/Country, Meet Name'.
    Returns (city, meet_name, country_code).
    """
    if not sted:
        return '', '', 'NOR'

    # Split on first comma
    parts = sted.split(',', 1)
    if len(parts) == 2:
        city_part = parts[0].strip()
        meet_name = parts[1].strip()
    else:
        city_part = ''
        meet_name = sted.strip()

    # Check for country code in city (e.g., "Västerås/SWE")
    country = 'NOR'
    if '/' in city_part:
        city_sub = city_part.split('/')
        city_part = city_sub[0].strip()
        code = city_sub[-1].strip()
        if len(code) == 3 and code.isalpha():
            country = code.upper()

    return city_part, meet_name, country


def parse_comp_date(date_str: str) -> Optional[str]:
    """Parse competition date DD.MM.YY -> YYYY-MM-DD."""
    if not date_str:
        return None
    date_str = date_str.strip()
    parts = date_str.split('.')
    if len(parts) == 3:
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            pass
    return None


def parse_stats_page(html: str, gender: str, age: int, outdoor: bool) -> List[Dict]:
    """Parse a LandsStatistikkAdv HTML page into result dicts."""
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    current_event = None
    in_skip_section = False
    is_manual_section = False
    is_foreign_section = False

    elements = soup.find_all(['h4', 'h5', 'h6', 'table'])

    for el in elements:
        if el.name == 'h4':
            current_event = el.get_text(strip=True)
            in_skip_section = False
            is_manual_section = False
            is_foreign_section = False

        elif el.name == 'h5':
            text = el.get_text(strip=True)
            if text in SKIP_SECTIONS or text == 'Ikke godkjente resultater':
                in_skip_section = True
                is_manual_section = False
            elif text == 'Manuelt Supplement':
                is_manual_section = True
                in_skip_section = False
            else:
                in_skip_section = False
                is_manual_section = False

        elif el.name == 'h6':
            text = el.get_text(strip=True)
            if text in SKIP_SECTIONS or text == 'Ikke medlem av NFIF':
                in_skip_section = True
            elif text == 'Utenlandske statsborgere for norske klubber':
                is_foreign_section = True
                in_skip_section = False
            else:
                in_skip_section = in_skip_section

        elif el.name == 'table' and current_event and not in_skip_section:
            rows = el.find_all('tr')
            for row in rows:
                # Skip header row
                if row.find('th'):
                    continue
                header_cells = row.find_all('td')
                if header_cells and header_cells[0].get_text(strip=True) == 'Resultat':
                    continue

                cells = row.find_all('td')
                if len(cells) < 6:
                    continue

                try:
                    result_text = cells[0].get_text(strip=True)
                    name_club_text = cells[1].get_text(strip=True)
                    birth_text = cells[2].get_text(strip=True)
                    place_text = cells[3].get_text(strip=True)
                    location_text = cells[4].get_text(strip=True)
                    comp_date_text = cells[5].get_text(strip=True)

                    # Get athlete external_id from link
                    athlete_ext_id = None
                    link = cells[1].find('a')
                    if link and link.get('href'):
                        m = re.search(r'showathl=(\d+)', link.get('href'))
                        if m:
                            athlete_ext_id = int(m.group(1))

                    # Parse result + wind
                    result, wind = parse_result_wind(result_text)
                    if not result:
                        continue

                    # Parse name and club.
                    #
                    # Cellen har formen "Navn, Klubb". For mangekamp limes
                    # delresultatene på i samme celle, med komma som desimaltegn:
                    #   "Maiken Rose Bjerknesli, IL i BUL14,23-7,40-16,56-14,43-4,61"
                    # Derfor MÅ vi splitte på FØRSTE komma. rsplit(',', 1) tok
                    # siste komma og ga klubbnavnet "61" — det skapte 660 falske
                    # utøvere og 133 falske klubber i mai 2026. Se OPERATIONS_LOG.md.
                    name_club_parts = name_club_text.split(',', 1)
                    if len(name_club_parts) == 2:
                        athlete_name = name_club_parts[0].strip()
                        club = strip_combined_event_results(name_club_parts[1])
                    else:
                        athlete_name = name_club_text.strip()
                        club = ''

                    # Remove nationality marker like "(EST)" from name
                    nat_match = re.search(r'\s*\([A-Z]{2,3}\)\s*$', athlete_name)
                    if nat_match:
                        athlete_name = athlete_name[:nat_match.start()].strip()

                    if not athlete_name:
                        continue

                    # Parse dates
                    birth_date_iso, birth_year = parse_birth_date(birth_text)
                    comp_date = parse_comp_date(comp_date_text)
                    if not comp_date:
                        continue

                    # Parse placement
                    place = None
                    place_match = re.match(r'^(\d+)', place_text)
                    if place_match:
                        place = int(place_match.group(1))

                    # Parse meet location
                    city, meet_name, country = parse_meet_location(location_text)

                    # Detect manual timing from result precision
                    is_manual = is_manual_section
                    if not is_manual and _is_running_event(current_event):
                        # Tideler (e.g., 8.4) = manual; hundredeler (e.g., 8.42) = electronic
                        decimal_match = re.search(r'\.(\d+)$', result)
                        if decimal_match and len(decimal_match.group(1)) == 1:
                            is_manual = True

                    results.append({
                        'event_name': current_event,
                        'athlete_name': athlete_name,
                        'athlete_ext_id': athlete_ext_id,
                        'birth_date': birth_date_iso,
                        'birth_year': birth_year,
                        'club': club,
                        'result': result,
                        'wind': wind,
                        'place': place,
                        'city': city,
                        'meet_name': meet_name,
                        'country': country,
                        'comp_date': comp_date,
                        'gender': gender,
                        'age_class': age,
                        'is_indoor': not outdoor,
                        'is_manual': is_manual,
                        'is_foreign': is_foreign_section,
                    })
                except Exception as e:
                    logger.debug(f"Error parsing row in {current_event}: {e}")
                    continue

    return results


def _is_running_event(event_name: str) -> bool:
    """Check if an event is a running event (where manual timing applies)."""
    if not event_name:
        return False
    name = event_name.lower()
    # Running events: anything with 'meter' but not 'hekk' over 400m
    if 'meter' in name and 'kappgang' not in name:
        # Extract distance
        dist_match = re.match(r'(\d+)\s*meter', name)
        if dist_match:
            dist = int(dist_match.group(1))
            return dist < 800
    return False


# ============================================================
# Database helpers (reused from update_results.py patterns)
# ============================================================

def load_events():
    global _event_cache
    response = supabase.table('events').select('id, code, name').execute()
    for e in response.data:
        _event_cache[e['code']] = e['id']
        if e['name']:
            _event_cache[e['name']] = e['id']
    logger.info(f"Loaded {len(response.data)} events")


def load_seasons():
    global _season_cache
    response = supabase.table('seasons').select('id, year, indoor').execute()
    for s in response.data:
        _season_cache[(s['year'], s['indoor'])] = s['id']
    logger.info(f"Loaded {len(response.data)} seasons")


def load_clubs():
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
            logger.info(f"  ...loaded {total} athletes")
    logger.info(f"Loaded {total} athletes")


def load_meets():
    """Load existing meets for dedup."""
    global _meet_cache
    offset = 0
    chunk_size = 1000
    total = 0
    while True:
        response = supabase.table('meets').select(
            'id, name, start_date'
        ).range(offset, offset + chunk_size - 1).execute()
        if not response.data:
            break
        for m in response.data:
            key = (m['name'], m['start_date'])
            _meet_cache[key] = m['id']
        total += len(response.data)
        offset += chunk_size
        if len(response.data) < chunk_size:
            break
    logger.info(f"Loaded {total} meets")


def get_event_id(event_name: str) -> Optional[str]:
    """Get event ID from event name.
    Priority: 1) explicit mapping, 2) direct name match in cache, 3) skip.
    Combined events (3/4/5/6 Kamp) are in DB by their full name,
    so direct name lookup via _event_cache handles them.
    """
    if event_name in SKIP_EVENTS:
        return None

    # 1. Explicit code mapping
    code = EVENT_NAME_TO_CODE.get(event_name)
    if code:
        return _event_cache.get(code)

    # 2. Direct name match (load_events caches by name too)
    if event_name in _event_cache:
        return _event_cache[event_name]

    return None


def get_season_id(date_str: str, indoor: bool) -> Optional[str]:
    year = int(date_str[:4])
    if indoor and int(date_str[5:7]) >= 10:
        year += 1
    return _season_cache.get((year, indoor))


# Delresultater fra mangekamp som er limt på klubbnavnet. Kutt fra første
# desimaltall ("14,23") eller statuskode ("DNF-"). Merk at rene sifre uten
# desimaltegn IKKE trigger — ekte klubber som "3T" skal overleve.
_CE_RESULTS = re.compile(r'(?:\d+[,.]\d+|(?:DNF|DNS|DQ|NM)(?=[-\s]|$)).*$')
_CLUB_TAIL = re.compile(r'[\s\-,.()]+$')


def strip_combined_event_results(text: str) -> str:
    """Fjern påhengte mangekamp-delresultater fra et klubbnavn."""
    return _CLUB_TAIL.sub('', _CE_RESULTS.sub('', text.strip())).strip()


def is_valid_club_name(name: str) -> bool:
    """Sperre mot at parsefeil skaper søppelklubber.

    Et klubbnavn må inneholde minst én bokstav og kan ikke være et rent tall
    eller en statuskode. Fanger "01", "61", "04-DNS", "0(558)".
    """
    n = (name or '').strip()
    if len(n) < 2:
        return False
    if not re.search(r'[A-Za-zÆØÅæøå]', n):
        return False
    # Kun sifre, skilletegn og statuskoder — f.eks. "04-DNS", "6)-DNS-DNS".
    if re.fullmatch(r'[\d\s\-–,.()]*(?:(?:DNS|DNF|DQ|NM)[\d\s\-–,.()]*)+', n, re.IGNORECASE):
        return False
    return True


def get_or_create_club(name: str) -> Optional[str]:
    if not name or name.strip() == '' or name == 'ukjent':
        return None
    name = name.strip()
    if not is_valid_club_name(name):
        logger.warning("Avviser ugyldig klubbnavn fra parsing: %r", name)
        return None
    if name in _club_cache:
        return _club_cache[name]
    try:
        response = supabase.table('clubs').insert({'name': name}).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
    except Exception:
        response = supabase.table('clubs').select('id').eq('name', name).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
    return None


def get_or_create_meet(name: str, date: str, city: str, country: str, indoor: bool) -> Optional[str]:
    cache_key = (name, date)
    if cache_key in _meet_cache:
        return _meet_cache[cache_key]

    # Also try "City, Meet" format
    full_name = f"{city}, {name}" if city else name
    full_key = (full_name, date)
    if full_key in _meet_cache:
        return _meet_cache[full_key]

    season_id = get_season_id(date, indoor)
    meet_data = {
        'name': full_name if city else name,
        'start_date': date,
        'city': city,
        'country': country,
        'indoor': indoor,
        'season_id': season_id,
    }
    try:
        response = supabase.table('meets').insert(meet_data).execute()
        if response.data:
            meet_id = response.data[0]['id']
            _meet_cache[cache_key] = meet_id
            _meet_cache[full_key] = meet_id
            logger.info(f"  Created meet: {full_name} ({date})")
            return meet_id
    except Exception as e:
        # Try to find it again (race condition)
        response = supabase.table('meets').select('id').eq('name', full_name).eq('start_date', date).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            return response.data[0]['id']
        logger.debug(f"Failed to create meet '{full_name}': {e}")
    return None


def match_athlete(name: str, birth_year: Optional[int], gender: str) -> Optional[str]:
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


def create_athlete(name: str, birth_year: Optional[int], gender: str,
                   club_name: str, birth_date: Optional[str] = None) -> Optional[str]:
    parts = name.split() if name else []
    first_name = parts[0] if parts else ''
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
    club_id = get_or_create_club(club_name) if club_name else None
    athlete_data = {
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'birth_year': birth_year,
        'current_club_id': club_id,
    }
    if birth_date:
        athlete_data['birth_date'] = birth_date
    try:
        response = supabase.table('athletes').insert(athlete_data).execute()
        if response.data:
            athlete_id = response.data[0]['id']
            _athlete_cache[(name.lower(), birth_year, gender)] = athlete_id
            return athlete_id
    except Exception as e:
        logger.debug(f"Failed to create athlete '{name}': {e}")
    return None


# ============================================================
# Dedup: per-athlete batch lookup
# ============================================================

_existing_results = set()
_athlete_results_loaded = set()


def _load_athlete_results(athlete_id: str):
    """Load all results for one athlete into the dedup cache (one DB call)."""
    if athlete_id in _athlete_results_loaded:
        return
    _athlete_results_loaded.add(athlete_id)
    try:
        offset = 0
        while True:
            response = supabase.table('results').select(
                'event_id, date, performance'
            ).eq('athlete_id', athlete_id).range(offset, offset + 999).execute()
            if not response.data:
                break
            for r in response.data:
                _existing_results.add((athlete_id, r['event_id'], r['date'], r['performance']))
            if len(response.data) < 1000:
                break
            offset += 1000
    except Exception:
        pass


def is_duplicate(athlete_id: str, event_id: str, comp_date: str, performance: str) -> bool:
    """Check dedup via in-memory cache (pre-loaded per athlete)."""
    _load_athlete_results(athlete_id)
    return (athlete_id, event_id, comp_date, performance) in _existing_results


# ============================================================
# Import
# ============================================================

def import_results(all_results: List[Dict], dry_run: bool = False) -> Dict:
    """Import parsed results into the database.
    Uses batch inserts (50 at a time) and skips dedup for newly created athletes.
    """
    stats = {
        'total_parsed': len(all_results),
        'imported': 0,
        'duplicates': 0,
        'matched_athlete': 0,
        'created_athlete': 0,
        'skipped_no_event': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'errors': 0,
    }
    unmapped_events = defaultdict(int)
    newly_created_athletes = set()
    result_batch = []
    BATCH_SIZE = 50

    def flush_batch():
        if not result_batch:
            return
        try:
            for i in range(0, len(result_batch), BATCH_SIZE):
                chunk = result_batch[i:i + BATCH_SIZE]
                supabase.table('results').insert(chunk).execute()
                stats['imported'] += len(chunk)
                for r in chunk:
                    _existing_results.add((r['athlete_id'], r['event_id'], r['date'], r['performance']))
        except Exception as e:
            logger.warning(f"  Batch insert failed, trying one-by-one: {e}")
            for r in result_batch:
                try:
                    supabase.table('results').insert(r).execute()
                    stats['imported'] += 1
                    _existing_results.add((r['athlete_id'], r['event_id'], r['date'], r['performance']))
                except Exception as e2:
                    logger.debug(f"    Single insert error: {e2}")
                    stats['errors'] += 1
        result_batch.clear()

    for i, row in enumerate(all_results):
        if i > 0 and i % 5000 == 0:
            logger.info(f"  Progress: {i}/{len(all_results)} "
                       f"(imported={stats['imported']}, dupes={stats['duplicates']}, "
                       f"new_athletes={stats['created_athlete']})")

        event_name = row['event_name']
        event_id = get_event_id(event_name)
        if not event_id:
            if event_name not in SKIP_EVENTS:
                unmapped_events[event_name] += 1
            stats['skipped_no_event'] += 1
            continue

        gender = row['gender']
        birth_year = row.get('birth_year')
        athlete_name = row['athlete_name']

        athlete_id = match_athlete(athlete_name, birth_year, gender)
        is_new_athlete = False

        if athlete_id:
            stats['matched_athlete'] += 1
        else:
            if dry_run:
                stats['created_athlete'] += 1
                stats['imported'] += 1
                continue
            athlete_id = create_athlete(
                athlete_name, birth_year, gender,
                row.get('club'), row.get('birth_date')
            )
            if athlete_id:
                stats['created_athlete'] += 1
                is_new_athlete = True
                newly_created_athletes.add(athlete_id)
            else:
                stats['skipped_no_athlete'] += 1
                continue

        club_id = get_or_create_club(row.get('club')) if not dry_run else None

        result_str = fix_performance_format(row['result'])
        comp_date = row['comp_date']

        # Skip dedup for newly created athletes — they have no existing results
        if not dry_run and athlete_id not in newly_created_athletes:
            if is_duplicate(athlete_id, event_id, comp_date, result_str):
                stats['duplicates'] += 1
                continue

        meet_id = None
        if not dry_run:
            meet_id = get_or_create_meet(
                row['meet_name'], comp_date, row['city'],
                row['country'], row['is_indoor']
            )
            if not meet_id:
                stats['skipped_no_meet'] += 1
                continue

        season_id = get_season_id(comp_date, row['is_indoor']) if not dry_run else None

        wind = None
        if row.get('wind') is not None:
            wind = row['wind']

        result_data = {
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': result_str,
            'date': comp_date,
            'wind': wind,
            'place': row.get('place'),
            'club_id': club_id,
            'status': 'OK',
            'verified': True,
        }

        if row.get('is_manual'):
            result_data['is_manual_time'] = True

        if wind is not None and wind > 2.0:
            result_data['is_wind_legal'] = False

        if dry_run:
            stats['imported'] += 1
            continue

        result_batch.append(result_data)
        if len(result_batch) >= BATCH_SIZE:
            flush_batch()

    # Flush remaining
    if not dry_run:
        flush_batch()

    if unmapped_events:
        logger.warning("\nUnmapped events:")
        for event, count in sorted(unmapped_events.items(), key=lambda x: -x[1]):
            logger.warning(f"  {event}: {count} results")

    return stats


# ============================================================
# Main
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Import youth (10-12) statistics from minfriidrettsstatistikk.info'
    )
    parser.add_argument('--age', type=int, choices=[10, 11, 12],
                        help='Specific age class (default: all three)')
    parser.add_argument('--gender', choices=['M', 'F'],
                        help='Specific gender (default: both)')
    parser.add_argument('--outdoor', action='store_true',
                        help='Only outdoor')
    parser.add_argument('--indoor', action='store_true',
                        help='Only indoor')
    parser.add_argument('--season', type=int, default=0,
                        help='Specific season year (default: all seasons)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Parse and count without importing')
    parser.add_argument('--all', action='store_true',
                        help='Import all age classes, both genders, both venues')
    return parser.parse_args()


def main():
    args = parse_args()

    logger.info("=" * 60)
    logger.info("IMPORT YOUTH STATISTICS (10-12)")
    if args.dry_run:
        logger.info("*** DRY RUN — no changes will be made ***")
    logger.info("=" * 60)

    # Login
    if not login():
        return

    # Determine what to scrape
    ages = [args.age] if args.age else [10, 11, 12]
    genders = [args.gender] if args.gender else ['M', 'F']
    venues = []
    if args.outdoor or args.all or (not args.indoor):
        venues.append(('Y', True))   # outdoor=Y, outdoor_flag=True
    if args.indoor or args.all or (not args.outdoor):
        venues.append(('N', False))  # outdoor=N, outdoor_flag=False

    # Load reference data
    logger.info("\nLoading reference data...")
    load_events()
    load_seasons()
    load_clubs()
    load_athletes()
    load_meets()

    grand_total = defaultdict(int)

    for gender in genders:
        for age in ages:
            showclass = AGE_CLASS_MAP.get((gender, age))
            if not showclass:
                continue

            gender_label = 'Gutter' if gender == 'M' else 'Jenter'

            for outdoor_param, is_outdoor in venues:
                venue_label = 'ute' if is_outdoor else 'inne'
                label = f"{gender_label} {age} ({venue_label})"
                logger.info(f"\n{'='*40}")
                logger.info(f"Scraping: {label} (showclass={showclass}, season={args.season or 'all'})")
                logger.info(f"{'='*40}")

                html = fetch_stats_page(showclass, outdoor_param, args.season)
                if not html:
                    logger.error(f"  Failed to fetch page for {label}")
                    continue

                # Check we didn't get a login page back
                if 'mittbrukernavn' in html:
                    logger.error(f"  Session expired — got login page. Re-logging in...")
                    if not login():
                        return
                    html = fetch_stats_page(showclass, outdoor_param, args.season)
                    if not html or 'mittbrukernavn' in html:
                        logger.error(f"  Still getting login page. Aborting.")
                        return

                results = parse_stats_page(html, gender, age, is_outdoor)
                logger.info(f"  Parsed {len(results)} results")

                if results:
                    stats = import_results(results, dry_run=args.dry_run)

                    for k, v in stats.items():
                        grand_total[k] += v

                    logger.info(f"  Results: imported={stats['imported']}, "
                               f"dupes={stats['duplicates']}, "
                               f"matched={stats['matched_athlete']}, "
                               f"created={stats['created_athlete']}, "
                               f"no_event={stats['skipped_no_event']}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("GRAND TOTAL")
    logger.info("=" * 60)
    for k, v in sorted(grand_total.items()):
        logger.info(f"  {k}: {v}")


if __name__ == '__main__':
    main()
