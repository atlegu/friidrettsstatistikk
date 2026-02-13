"""
Import historical all-time statistics from friidrett.no into Supabase.

Parses the Word-converted HTML pages from:
  https://www.friidrett.no/siteassets/aktivitet/statistikk/alle-tiders/

Features:
  - 3-level deduplication (application check, meet matching, DB constraint)
  - Fuzzy athlete matching with performance-based confirmation
  - Source and import batch tracking
  - Separate parsers for senior and youth (13-18) pages

Usage:
    python import_historical.py --gender F --event 100 --dry-run
    python import_historical.py --gender M --event 100
    python import_historical.py --gender F --all
    python import_historical.py --gender M --event 100 --youth
"""

import argparse
import os
import re
import time
import logging
from datetime import datetime, timedelta
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
BASE_URL = "https://www.friidrett.no/siteassets/aktivitet/statistikk/alle-tiders"
REQUEST_DELAY = 0.5

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FriidrettStats/1.0'
})

# ============================================================
# Event mapping: friidrett.no filename -> (event_code_M, event_code_F)
#
# URL pattern: .../mennute/www.friidrett.no-m{key}.htm
#              .../kvinnerute/www.friidrett.no-k{key}.htm
#
# Running events use numeric names (100, 200, etc.)
# Field/hurdle events use abbreviated codes (hj, lj, sp, etc.)
# ============================================================
SENIOR_EVENTS = {
    # Running events (9 cells with wind for sprint, 8 cells for 400m+)
    '100':      ('100m', '100m'),
    '200':      ('200m', '200m'),
    '400':      ('400m', '400m'),
    '800':      ('800m', '800m'),
    '1500':     ('1500m', '1500m'),
    '3000':     ('3000m', '3000m'),
    '5000':     ('5000m', '5000m'),
    '10000':    ('10000m', '10000m'),
    # Hurdles (9 cells with wind for sprint hurdles, 8 cells for 400mh)
    '110h':     ('110mh', None),
    '100h':     (None, '100mh'),
    '400h':     ('400mh', '400mh'),
    '3000h':    ('3000mhinder', '3000mhinder'),
    # Jumps (9 cells with wind for lj/tj, 8 cells for hj/pv)
    'hj':       ('hoyde', 'hoyde'),
    'pv':       ('stav', 'stav'),
    'lj':       ('lengde', 'lengde'),
    'tj':       ('tresteg', 'tresteg'),
    # Throws (8 cells, no wind)
    'sp':       ('kule_7_26kg', 'kule_4kg'),
    'dt':       ('diskos_2kg', 'diskos_1kg'),
    'ht':       ('slegge_726kg/1215cm', 'slegge_40kg/1195cm'),
    'jt':       ('spyd_800g', 'spyd_600g'),
}

# NOTE: As of 2026-02, ALL youth pages return pages without parseable tables.
YOUTH_EVENTS = {
    '100':      ('100m', '100m'),
    '200':      ('200m', '200m'),
    '400':      ('400m', '400m'),
    '800':      ('800m', '800m'),
    '1500':     ('1500m', '1500m'),
    '3000':     ('3000m', '3000m'),
    'hoyde':    ('hoyde', 'hoyde'),
    'stav':     ('stav', 'stav'),
    'lengde':   ('lengde', 'lengde'),
    'tresteg':  ('tresteg', 'tresteg'),
    'kule':     ('kule_5kg', 'kule_3kg'),
    'diskos':   ('diskos_1_5kg', 'diskos_1kg'),
    'spyd':     ('spyd_800g', 'spyd_600g'),
}

# Sections to skip on senior pages
SKIP_SECTION_KEYWORDS = [
    'medvind', 'assisting wind', 'wind-assisted',
    'feil', 'incorrect', 'wrong',
    'ubekreftet', 'not confirmed', 'unconfirmed',
    'kort distanse', 'short distance', 'short track',
    'flaggstart', 'no gun', 'false start',
    'ekstra', 'extra race', 'extra trial', 'ekstra forsok',
    'autorisert', 'not authorised', 'unsanctioned',
    'tvilsomt', 'doubtful', 'rolling start',
    'statsborger', 'citizen',
    'voksne', 'adult',
    'retning', 'direction',
    'ikke godkjente', 'unapproved',
    'suspendert', 'suspension',
    'defekt', 'defect',
    'hellende', 'sloping', 'banked',
    'annulert', 'nullified',
    'innendors', 'indoor',          # indoor results — separate category
    'oppvisning', 'exhibition',
    'manglende', 'missing',
    'uapprobert', 'unapproved meet',
    'ingen klubb', 'no club',
    'utenfor bane', 'outside stadium',
    'lave hekker', 'low hurdles',
    'kort strekning', 'short race',
    'usikker hekke', 'hurdle height not confirmed',
    'lett kule', 'light implement', 'light shot',
    'lett diskos', 'light disc',
    'lett slegge', 'light hammer',
    'gammelt spyd', 'old javelin',
    'usikkert resultat', 'uncertain result',
    'uklare', 'unclear',
]


# ============================================================
# URL builders
# ============================================================

def build_senior_url(gender: str, event_key: str) -> str:
    if gender == 'M':
        return f"{BASE_URL}/mennute/www.friidrett.no-m{event_key}.htm"
    else:
        return f"{BASE_URL}/kvinnerute/www.friidrett.no-k{event_key}.htm"


def build_youth_url(gender: str, event_key: str) -> str:
    if gender == 'M':
        return f"{BASE_URL}/gutter/g{event_key}.htm"
    else:
        return f"{BASE_URL}/jenter/j{event_key}.htm"


# ============================================================
# Caches
# ============================================================
_event_cache: Dict[str, str] = {}
_club_cache: Dict[str, str] = {}
_athlete_cache: Dict[Tuple, str] = {}
_athlete_details: Dict[str, Dict] = {}
_meet_cache: Dict[Tuple, str] = {}
_season_cache: Dict[Tuple, str] = {}
_age_class_cache: Dict[str, str] = {}
_source_id: Optional[str] = None
_existing_results: Dict[Tuple, str] = {}


def load_events():
    global _event_cache
    response = supabase.table('events').select('id, code, name').execute()
    for e in response.data:
        _event_cache[e['code']] = e['id']
        if e.get('name'):
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
    offset, chunk_size, total = 0, 1000, 0
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
    global _athlete_cache, _athlete_details
    offset, chunk_size, total = 0, 1000, 0
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
            _athlete_details[a['id']] = {
                'first_name': a['first_name'],
                'last_name': a['last_name'],
                'birth_year': a.get('birth_year'),
                'gender': a.get('gender'),
            }
        total += len(response.data)
        offset += chunk_size
        if len(response.data) < chunk_size:
            break
        if total % 10000 == 0:
            logger.info(f"  ...loaded {total} athletes so far")
    logger.info(f"Loaded {total} athletes into cache")


def load_age_classes():
    global _age_class_cache
    response = supabase.table('age_classes').select('id, code, name, gender').execute()
    for ac in response.data:
        _age_class_cache[ac['code']] = ac['id']
        if ac.get('name'):
            _age_class_cache[ac['name']] = ac['id']
    logger.info(f"Loaded {len(response.data)} age classes")


def load_existing_results_for_event(event_id: str):
    """Load existing results for dedup. Keyed by (athlete_id, event_id, date, performance)."""
    global _existing_results
    _existing_results = {}
    offset, chunk_size, total = 0, 1000, 0
    while True:
        response = supabase.table('results').select(
            'id, athlete_id, event_id, date, performance'
        ).eq('event_id', event_id).range(offset, offset + chunk_size - 1).execute()
        if not response.data:
            break
        for r in response.data:
            key = (r['athlete_id'], r['event_id'], r['date'], r['performance'])
            _existing_results[key] = r['id']
        total += len(response.data)
        offset += chunk_size
        if len(response.data) < chunk_size:
            break
    logger.info(f"Loaded {total} existing results for event dedup")


# ============================================================
# Source and import batch tracking
# ============================================================

def get_or_create_source() -> str:
    global _source_id
    if _source_id:
        return _source_id

    name = "friidrett.no alle tiders statistikk"
    response = supabase.table('sources').select('id').eq('name', name).execute()
    if response.data:
        _source_id = response.data[0]['id']
        logger.info(f"Using existing source: {_source_id}")
        return _source_id

    response = supabase.table('sources').insert({
        'name': name,
        'source_type': 'other',
        'original_url': 'https://www.friidrett.no/siteassets/aktivitet/statistikk/alle-tiders/',
    }).execute()
    if response.data:
        _source_id = response.data[0]['id']
        logger.info(f"Created source: {_source_id}")
        return _source_id
    raise RuntimeError("Failed to create source record")


def create_import_batch(name: str) -> str:
    response = supabase.table('import_batches').insert({
        'name': name,
        'source_type': 'other',
        'status': 'processing',
    }).execute()
    if response.data:
        return response.data[0]['id']
    raise RuntimeError("Failed to create import batch")


def update_import_batch(batch_id: str, row_count: int, status: str = "imported",
                        matched: int = 0, unmatched: int = 0):
    supabase.table('import_batches').update({
        'row_count': row_count,
        'status': status,
        'matched_athletes': matched,
        'unmatched_athletes': unmatched,
        'imported_at': datetime.now().isoformat(),
    }).eq('id', batch_id).execute()


# ============================================================
# HTML fetching
# ============================================================

def fetch_page(url: str) -> Optional[str]:
    time.sleep(REQUEST_DELAY)
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        if response.apparent_encoding:
            response.encoding = response.apparent_encoding
        else:
            response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


# ============================================================
# Parsing helpers
# ============================================================

def clean_text(text: str) -> str:
    if not text:
        return ''
    text = text.replace('\xa0', ' ').replace('\u00a0', ' ')
    text = text.replace('\r\n', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_date_dmy(date_str: str) -> Optional[datetime]:
    """Parse date from D.M.YY or D.M.YYYY format.
    For 2-digit years: if result > current year, subtract 100.
    """
    if not date_str:
        return None
    date_str = clean_text(date_str)
    current_year = datetime.now().year
    try:
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 100:
                year = 2000 + year if year < 30 else 1900 + year
                if year > current_year:
                    year -= 100
            if 1 <= month <= 12 and 1 <= day <= 31:
                return datetime(year, month, day)
        elif len(parts) == 2:
            # M.YY — use 1st of month
            month, year = int(parts[0]), int(parts[1])
            if year < 100:
                year = 2000 + year if year < 30 else 1900 + year
                if year > current_year:
                    year -= 100
            if 1 <= month <= 12:
                return datetime(year, month, 1)
    except (ValueError, IndexError):
        pass
    return None


def _resolve_two_digit_year(yy: int, context_year: Optional[int] = None) -> int:
    """Resolve 2-digit year to 4-digit, using competition context if available.
    For birth years: if 2000+yy would make the person < 10 at context_year, use 1900+yy.
    Default cutoff: 30 (so 29->2029 without context, but see below).
    """
    if yy >= 100:
        return yy
    candidate_2000 = 2000 + yy
    candidate_1900 = 1900 + yy
    if context_year:
        age_if_2000 = context_year - candidate_2000
        if age_if_2000 < 10:
            return candidate_1900
        return candidate_2000
    # No context: use 30 as cutoff but cap at current year
    if candidate_2000 > datetime.now().year:
        return candidate_1900
    return candidate_2000 if yy < 30 else candidate_1900


def parse_birth_date_to_year(date_str: str, comp_year: Optional[int] = None) -> Optional[int]:
    """Parse birth date to year. Handles D.M.YY and bare year like '68'.
    Uses competition year as context to resolve 2-digit years correctly.
    """
    if not date_str:
        return None
    date_str = clean_text(date_str)
    if re.match(r'^\d{2,4}$', date_str):
        year = int(date_str)
        if year < 100:
            year = _resolve_two_digit_year(year, comp_year)
        return year
    # Try D.M.YY format
    parts = date_str.split('.')
    if len(parts) == 3:
        try:
            year = int(parts[2])
            if year < 100:
                year = _resolve_two_digit_year(year, comp_year)
            return year
        except ValueError:
            pass
    return None


def parse_youth_birth_date(date_str: str) -> Optional[int]:
    """Parse youth birth date: 'DD.MM YYYY' or 'DD.MM.YYYY' -> year."""
    if not date_str:
        return None
    date_str = clean_text(date_str)
    m = re.match(r'^\d{1,2}\.\d{1,2}\s+(\d{4})$', date_str)
    if m:
        return int(m.group(1))
    m = re.match(r'^\d{1,2}\.\d{1,2}\.(\d{4})$', date_str)
    if m:
        return int(m.group(1))
    m = re.match(r'^(\d{4})$', date_str)
    if m:
        return int(m.group(1))
    m = re.match(r'^(\d{2})$', date_str)
    if m:
        yr = int(m.group(1))
        return 2000 + yr if yr < 30 else 1900 + yr
    return None


def parse_youth_comp_date(date_str: str) -> Optional[datetime]:
    """Parse youth competition date: 'DD.MM.YYYY' or 'DD.MM YYYY'."""
    if not date_str:
        return None
    date_str = clean_text(date_str)
    # DD.MM.YYYY
    m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', date_str)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    # DD.MM YYYY
    m = re.match(r'^(\d{1,2})\.(\d{1,2})\s+(\d{4})$', date_str)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def fix_performance_format(result_str: str) -> str:
    """Convert '3.34.02' -> '3:34.02'."""
    if not result_str:
        return result_str
    match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{1,2})$', result_str)
    if match:
        minutes, seconds, hundredths = match.groups()
        return f"{minutes}:{seconds}.{hundredths}"
    return result_str


def parse_wind_value(wind_str: str) -> Optional[float]:
    if not wind_str:
        return None
    wind_str = clean_text(wind_str)
    # Normalize minus chars
    wind_str = wind_str.replace('\u2212', '-').replace('\u2013', '-').replace('\u2014', '-')
    wind_str = wind_str.replace(',', '.')
    # Strip non-numeric prefix
    wind_str = re.sub(r'^[^0-9+\-]+', '', wind_str)
    if not wind_str:
        return None
    try:
        return float(wind_str)
    except ValueError:
        return None


def performance_to_value(perf: str) -> Optional[float]:
    """Convert performance string to seconds or meters for sorting."""
    if not perf:
        return None
    try:
        if ':' in perf:
            parts = perf.split(':')
            if len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return float(perf)
    except ValueError:
        return None


# ============================================================
# Senior page parser
# ============================================================

def parse_senior_page(html: str, gender: str, event_code: str) -> List[Dict]:
    """Parse a senior all-time page.

    HTML structure: <div class=WordSection1> containing alternating
    <p> headers and <table class=MsoNormalTable> with result rows.
    Each table row has 9 cells:
      performance, wind, (lane), first_name, last_name, club, birth_date, location, comp_date
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    section = soup.find('div', class_='WordSection1')
    if not section:
        section = soup.find('body')
    if not section:
        logger.error("Could not find content in HTML")
        return results

    current_section = ''
    is_manual_section = False
    is_indoor_section = False
    table_index = 0

    # Track last bold athlete for immediate continuations
    last_athlete = {'first_name': '', 'last_name': '', 'club': '',
                    'birth_year': None, 'birth_date_str': ''}
    # Track ALL bold entries by last_name for reference-back in interleaved rows.
    # Results are sorted by performance, so athlete A's non-bold rows can appear
    # after athlete B's bold entry. We need to look up by last_name.
    bold_athletes = {}  # last_name.lower() -> {first_name, club, birth_year, birth_date_str}

    for child in section.children:
        if not hasattr(child, 'name') or child.name is None:
            continue

        # Section headers can appear in <p> or <div> tags (Word HTML uses both)
        if child.name in ('p', 'div'):
            text = clean_text(child.get_text())
            if text and len(text) > 2 and child.find('b'):
                current_section = text
                section_lower = current_section.lower()
                is_manual_section = ('anuelt' in section_lower or 'hand-timed' in section_lower)
                is_indoor_section = ('innend' in section_lower or 'indoor' in section_lower)

        elif child.name == 'table':
            # Check if we should import this section
            should_skip = False
            if table_index > 0:
                if is_manual_section:
                    should_skip = False  # Import manual supplement
                elif is_indoor_section:
                    should_skip = False  # Import indoor section
                elif current_section:
                    section_lower = current_section.lower()
                    should_skip = any(kw in section_lower for kw in SKIP_SECTION_KEYWORDS)
                    if not should_skip and not is_manual_section and not is_indoor_section:
                        # Unknown section — skip to be safe
                        should_skip = True

            if should_skip:
                table_index += 1
                last_athlete = {'first_name': '', 'last_name': '', 'club': '',
                                'birth_year': None, 'birth_date_str': ''}
                continue

            rows = child.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                ncells = len(cells)
                if ncells < 8:
                    continue

                cell_texts = [clean_text(c.get_text()) for c in cells]
                cell_bolds = [c.find('b') is not None for c in cells]

                # Two formats:
                # 9 cells (sprint/field): perf, wind, lane, first_name, last_name, club, birth_date, location, comp_date
                # 8 cells (400m+): perf, lane, first_name, last_name, club, birth_date, location, comp_date
                if ncells >= 9:
                    perf_raw = cell_texts[0]
                    wind_raw = cell_texts[1]
                    lane_raw = cell_texts[2]
                    first_name = cell_texts[3]
                    last_name = cell_texts[4]
                    club = cell_texts[5]
                    birth_date_str = cell_texts[6]
                    location = cell_texts[7]
                    comp_date_str = cell_texts[8]
                else:
                    perf_raw = cell_texts[0]
                    wind_raw = ''
                    lane_raw = cell_texts[1]
                    first_name = cell_texts[2]
                    last_name = cell_texts[3]
                    club = cell_texts[4]
                    birth_date_str = cell_texts[5]
                    location = cell_texts[6]
                    comp_date_str = cell_texts[7]

                if not perf_raw:
                    continue

                # Parse performance
                perf_clean = perf_raw.replace(',', '.')
                perf_formatted = fix_performance_format(perf_clean)

                # Parse wind
                wind = parse_wind_value(wind_raw) if wind_raw else None

                # Parse lane
                lane = None
                lane_match = re.match(r'\((\d+)\)', lane_raw)
                if lane_match:
                    lane = int(lane_match.group(1))

                # Handle athlete identification:
                # New entry = bold performance AND non-empty first_name
                # Some rows have bold perf + bold last_name but empty first_name —
                # these are "notable repeats" for an already-introduced athlete, not new entries.
                is_new_entry = cell_bolds[0] and first_name
                if is_new_entry and last_name:
                    # Fresh bold athlete entry — register in tracking dicts
                    cd = parse_date_dmy(comp_date_str)
                    by = parse_birth_date_to_year(
                        birth_date_str, cd.year if cd else None
                    ) if birth_date_str else None
                    last_athlete = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'club': club,
                        'birth_year': by,
                        'birth_date_str': birth_date_str,
                    }
                    bold_athletes[last_name.lower()] = last_athlete.copy()
                else:
                    # Non-bold row: determine which bold athlete this belongs to
                    if not last_name:
                        # Truly empty last_name — continuation of last_athlete
                        ref = last_athlete
                    elif last_name.lower() == last_athlete['last_name'].lower():
                        # Same last_name as last bold entry — continuation
                        ref = last_athlete
                    elif last_name.lower() in bold_athletes:
                        # Different last_name — look up in bold_athletes registry
                        ref = bold_athletes[last_name.lower()]
                    else:
                        # Unknown athlete (not seen in bold) — use what we have
                        ref = None

                    if ref:
                        if not first_name:
                            first_name = ref['first_name']
                        if not club:
                            club = ref['club']
                        if not birth_date_str:
                            birth_date_str = ref.get('birth_date_str')
                    else:
                        if not birth_date_str:
                            birth_date_str = None

                if not last_name:
                    continue

                comp_date = parse_date_dmy(comp_date_str)
                if not comp_date:
                    continue

                full_name = f"{first_name} {last_name}".strip() if first_name else last_name
                # Get birth_year: parse from birth_date_str if present, else from ref
                if birth_date_str:
                    birth_year = parse_birth_date_to_year(birth_date_str, comp_date.year)
                elif is_new_entry:
                    birth_year = last_athlete.get('birth_year')
                else:
                    ref = bold_athletes.get(last_name.lower()) if last_name else None
                    if not ref and last_name and last_name.lower() == last_athlete['last_name'].lower():
                        ref = last_athlete
                    birth_year = ref['birth_year'] if ref else None

                is_indoor = is_indoor_section

                results.append({
                    'performance': perf_formatted,
                    'wind': wind,
                    'lane': lane,
                    'athlete_name': full_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'club': club,
                    'birth_year': birth_year,
                    'gender': gender,
                    'location': clean_text(location),
                    'date': comp_date,
                    'date_str': comp_date.strftime('%Y-%m-%d'),
                    'is_manual_time': is_manual_section,
                    'is_indoor': is_indoor,
                    'event_code': event_code,
                    'age_class': None,
                })

            table_index += 1
            last_athlete = {'first_name': '', 'last_name': '', 'club': '',
                            'birth_year': None, 'birth_date_str': ''}

    logger.info(f"Parsed {len(results)} results from senior page "
                f"(section: main + {'manual' if any(r['is_manual_time'] for r in results) else 'no manual'})")
    return results


# ============================================================
# Youth page parser
# ============================================================

def parse_youth_page(html: str, gender: str, event_code: str) -> List[Dict]:
    """Parse a youth all-time page.

    Single table with age group headers as rows.
    Data columns: empty, perf(+wind), place/heat, name, club, birth_date, city, comp_date
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    tables = soup.find_all('table')
    if not tables:
        logger.error("No tables found in youth HTML")
        return results

    current_age = None
    current_age_class = None
    is_manual_section = False
    gender_prefix = 'G' if gender == 'M' else 'J'

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if not cells:
                continue

            cell_texts = [clean_text(c.get_text()) for c in cells]
            combined = ' '.join(t for t in cell_texts if t).upper()

            # Check for age group header row
            # Pattern: "100 METER JENTER 13 ÅR" or "100 METER GUTTER 14 ÅR — MANUELT SUPPLEMENT"
            age_match = re.search(r'(\d{2})\s*[ÅåA]\s*[Rr]', combined.replace('\ufffd', 'Å'))
            if age_match and ('JENTER' in combined or 'GUTTER' in combined or 'METER' in combined):
                current_age = int(age_match.group(1))
                current_age_class = f"{gender_prefix}{current_age}"
                is_manual_section = 'MANUELT' in combined or 'SUPPLEMENT' in combined
                continue

            # Skip rank marker rows (just a number like "10" or "20")
            non_empty = [t for t in cell_texts if t]
            if len(non_empty) == 1 and non_empty[0].isdigit():
                continue

            if not current_age:
                continue

            # Need at least 7 cells for data
            if len(cells) < 7:
                continue

            # Columns: [empty], perf+wind, place/heat, name, club, birth_date, city, comp_date
            perf_raw = cell_texts[1] if len(cell_texts) > 1 else ''
            name_raw = cell_texts[3] if len(cell_texts) > 3 else ''
            club_raw = cell_texts[4] if len(cell_texts) > 4 else ''
            birth_raw = cell_texts[5] if len(cell_texts) > 5 else ''
            city_raw = cell_texts[6] if len(cell_texts) > 6 else ''
            date_raw = cell_texts[7] if len(cell_texts) > 7 else ''

            if not perf_raw or not name_raw:
                continue

            # Parse performance and wind (combined: "12.54 -0.6" or "12,43")
            perf_parts = perf_raw.split()
            perf_str = perf_parts[0] if perf_parts else ''
            wind_str = perf_parts[1] if len(perf_parts) > 1 else None

            # Detect indoor 'i' suffix
            is_indoor = False
            if perf_str.endswith('i'):
                is_indoor = True
                perf_str = perf_str[:-1]

            perf_clean = perf_str.replace(',', '.')
            perf_formatted = fix_performance_format(perf_clean)

            wind = parse_wind_value(wind_str) if wind_str else None

            # Skip if not starting with digit
            if not perf_formatted or not re.match(r'^\d', perf_formatted):
                continue

            # Parse name (single cell: "Fornavn Etternavn")
            name_parts = name_raw.split()
            if len(name_parts) >= 2:
                first_name = ' '.join(name_parts[:-1])
                last_name = name_parts[-1]
            elif name_parts:
                first_name = ''
                last_name = name_parts[0]
            else:
                continue

            birth_year = parse_youth_birth_date(birth_raw)

            comp_date = parse_youth_comp_date(date_raw)
            if not comp_date:
                continue

            results.append({
                'performance': perf_formatted,
                'wind': wind,
                'lane': None,
                'athlete_name': name_raw,
                'first_name': first_name,
                'last_name': last_name,
                'club': club_raw,
                'birth_year': birth_year,
                'gender': gender,
                'location': city_raw,
                'date': comp_date,
                'date_str': comp_date.strftime('%Y-%m-%d'),
                'is_manual_time': is_manual_section,
                'is_indoor': is_indoor,
                'event_code': event_code,
                'age_class': current_age_class,
            })

    logger.info(f"Parsed {len(results)} results from youth page")
    return results


# ============================================================
# Athlete matching
# ============================================================

def _levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(curr[-1] + 1, prev[j + 1] + 1, prev[j] + (0 if c1 == c2 else 1)))
        prev = curr
    return prev[-1]


def fuzzy_match_athlete(name: str, birth_year: Optional[int], gender: str) -> Optional[str]:
    """Fuzzy match: Levenshtein ≤ 2, last name match + first name substring, reversed name."""
    if not birth_year:
        return None

    name_lower = name.lower()
    name_parts = name_lower.split()
    if not name_parts:
        return None

    first_lower = name_parts[0]
    last_lower = name_parts[-1] if len(name_parts) > 1 else ''

    best_match = None
    best_distance = 3

    for (cached_name, cached_by, cached_gender), athlete_id in _athlete_cache.items():
        if cached_by != birth_year:
            continue
        if cached_gender and gender and cached_gender != gender:
            continue

        dist = _levenshtein(name_lower, cached_name)
        if dist < best_distance:
            best_distance = dist
            best_match = athlete_id
            if dist == 0:
                break

        # Last name match + first name substring
        if last_lower:
            cached_parts = cached_name.split()
            cached_last = cached_parts[-1] if len(cached_parts) > 1 else ''
            cached_first = cached_parts[0] if cached_parts else ''
            if cached_last == last_lower and (first_lower in cached_first or cached_first in first_lower):
                if best_distance > 1:
                    best_distance = 1
                    best_match = athlete_id

        # Reversed name order
        if last_lower:
            reversed_name = f"{last_lower} {first_lower}"
            if _levenshtein(reversed_name, cached_name) <= 1:
                if best_distance > 1:
                    best_distance = 1
                    best_match = athlete_id

    if best_match and best_distance <= 2:
        return best_match
    return None


def match_athlete(name: str, birth_year: Optional[int], gender: str) -> Optional[str]:
    """Match athlete: exact, then without gender, then fuzzy."""
    if not name:
        return None
    key = (name.lower(), birth_year, gender)
    athlete_id = _athlete_cache.get(key)
    if athlete_id:
        return athlete_id
    # Try without gender
    for ck, cid in _athlete_cache.items():
        if ck[0] == name.lower() and ck[1] == birth_year:
            return cid
    return fuzzy_match_athlete(name, birth_year, gender)


def create_athlete(name: str, birth_year: Optional[int], gender: str,
                   club_name: str) -> Optional[str]:
    name_parts = name.split() if name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    club_id = get_or_create_club(club_name) if club_name else None

    try:
        response = supabase.table('athletes').insert({
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'birth_year': birth_year,
            'current_club_id': club_id,
        }).execute()
        if response.data:
            aid = response.data[0]['id']
            _athlete_cache[(name.lower(), birth_year, gender)] = aid
            _athlete_details[aid] = {
                'first_name': first_name, 'last_name': last_name,
                'birth_year': birth_year, 'gender': gender,
            }
            return aid
    except Exception as e:
        logger.debug(f"Failed to create athlete '{name}': {e}")
    return None


# ============================================================
# Club and meet helpers
# ============================================================

def get_or_create_club(name: str) -> Optional[str]:
    if not name or not name.strip():
        return None
    name = name.strip()
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


def find_existing_meet(city: str, date_str: str) -> Optional[str]:
    """Find existing meet by city + date (±1 day). Level 2 dedup."""
    if not city:
        return None
    city_clean = city.split(',')[0].strip()
    if not city_clean or len(city_clean) < 2:
        return None

    # Check cache
    for (cached_name, cached_date), cached_id in _meet_cache.items():
        if city_clean.lower() in cached_name.lower() and cached_date == date_str:
            return cached_id

    # Query DB
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_before = (date_obj - timedelta(days=1)).strftime('%Y-%m-%d')
        date_after = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')

        response = supabase.table('meets').select('id, name, city, start_date').ilike(
            'city', f'%{city_clean}%'
        ).gte('start_date', date_before).lte('start_date', date_after).execute()

        if response.data:
            meet = response.data[0]
            _meet_cache[(meet['name'], meet['start_date'])] = meet['id']
            return meet['id']
    except Exception as e:
        logger.debug(f"Error finding meet {city} {date_str}: {e}")
    return None


def get_or_create_meet_historical(city: str, date_str: str, indoor: bool) -> Optional[str]:
    """Get or create meet for historical data."""
    meet_id = find_existing_meet(city, date_str)
    if meet_id:
        return meet_id

    cache_key = (city, date_str)
    if cache_key in _meet_cache:
        return _meet_cache[cache_key]

    # Determine season
    year = int(date_str[:4])
    month = int(date_str[5:7])
    season_year = year + 1 if indoor and month >= 10 else year
    season_id = _season_cache.get((season_year, indoor))

    # Parse country from location
    city_name = city.split(',')[0].strip() if city else ''
    country = 'NOR'
    if ',' in city:
        country_part = city.split(',')[-1].strip()
        if len(country_part) == 3 and country_part.isupper():
            country = country_part

    meet_data = {
        'name': city_name or city or 'Ukjent',
        'start_date': date_str,
        'city': city_name or city or 'Ukjent',
        'country': country,
        'indoor': indoor,
    }
    if season_id:
        meet_data['season_id'] = season_id

    try:
        response = supabase.table('meets').insert(meet_data).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            return _meet_cache[cache_key]
    except Exception as e:
        logger.debug(f"Failed to create meet '{city}' {date_str}: {e}")
        # Try to find it (may have been created by concurrent insert)
        try:
            response = supabase.table('meets').select('id').eq(
                'city', city_name or city
            ).eq('start_date', date_str).execute()
            if response.data:
                _meet_cache[cache_key] = response.data[0]['id']
                return _meet_cache[cache_key]
        except Exception:
            pass
    return None


# ============================================================
# Dedup helpers
# ============================================================

def result_already_exists(athlete_id: str, event_id: str, date_str: str,
                          performance: str) -> bool:
    """Level 1 dedup: check if result already in DB."""
    return (athlete_id, event_id, date_str, performance) in _existing_results


def get_season_id(date_str: str, indoor: bool) -> Optional[str]:
    year = int(date_str[:4])
    if indoor and int(date_str[5:7]) >= 10:
        year += 1
    return _season_cache.get((year, indoor))


# ============================================================
# Import engine
# ============================================================

def import_results(parsed_results: List[Dict], event_id: str, source_id: Optional[str],
                   batch_id: Optional[str], dry_run: bool = False) -> Dict:
    stats = {
        'total_parsed': len(parsed_results),
        'imported': 0,
        'skipped_duplicate': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'skipped_no_season': 0,
        'matched_existing_athlete': 0,
        'created_new_athlete': 0,
        'errors': 0,
        'new_athletes': [],
    }

    result_batch = []

    for i, row in enumerate(parsed_results):
        if i > 0 and i % 500 == 0:
            logger.info(f"  Processing row {i}/{len(parsed_results)}...")

        # Match athlete
        athlete_id = match_athlete(row['athlete_name'], row['birth_year'], row['gender'])

        if athlete_id:
            stats['matched_existing_athlete'] += 1
        else:
            if dry_run:
                stats['created_new_athlete'] += 1
                stats['new_athletes'].append({
                    'name': row['athlete_name'],
                    'birth_year': row['birth_year'],
                    'gender': row['gender'],
                    'club': row['club'],
                })
                athlete_id = 'DRY_RUN'
            else:
                athlete_id = create_athlete(
                    row['athlete_name'], row['birth_year'],
                    row['gender'], row['club']
                )
                if athlete_id:
                    stats['created_new_athlete'] += 1
                    stats['new_athletes'].append({
                        'name': row['athlete_name'],
                        'birth_year': row['birth_year'],
                        'gender': row['gender'],
                        'club': row['club'],
                    })
                else:
                    stats['skipped_no_athlete'] += 1
                    continue

        # Level 1 dedup
        if not dry_run and athlete_id != 'DRY_RUN':
            if result_already_exists(athlete_id, event_id, row['date_str'], row['performance']):
                stats['skipped_duplicate'] += 1
                continue

        # Meet
        if dry_run:
            meet_id = 'DRY_RUN_MEET'
        else:
            meet_id = get_or_create_meet_historical(
                row['location'], row['date_str'], row['is_indoor']
            )
            if not meet_id:
                stats['skipped_no_meet'] += 1
                continue

        # Season
        season_id = get_season_id(row['date_str'], row['is_indoor'])
        if not season_id and not dry_run:
            stats['skipped_no_season'] += 1
            continue

        if dry_run:
            stats['imported'] += 1
            continue

        # Build result
        result_data = {
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': row['performance'],
            'date': row['date_str'],
            'status': 'OK',
            'verified': True,
            'source_id': source_id,
            'import_batch_id': batch_id,
            'is_manual_time': row.get('is_manual_time', False) or None,
        }

        # Optional fields
        if row['wind'] is not None:
            result_data['wind'] = row['wind']
            if row['wind'] > 2.0:
                result_data['is_wind_legal'] = False

        if row.get('lane'):
            result_data['lane'] = row['lane']

        club_id = get_or_create_club(row['club'])
        if club_id:
            result_data['club_id'] = club_id

        # performance_value is calculated automatically by DB trigger
        # (calculate_performance_value_trigger) - do NOT send it

        if row.get('age_class'):
            ac_id = _age_class_cache.get(row['age_class'])
            if ac_id:
                result_data['competition_age_class_id'] = ac_id

        # Don't store False for is_manual_time, use None
        if not result_data.get('is_manual_time'):
            result_data.pop('is_manual_time', None)

        result_batch.append(result_data)

        # Track in cache to prevent intra-batch duplicates
        _existing_results[(athlete_id, event_id, row['date_str'], row['performance'])] = 'pending'

    # Insert
    if result_batch and not dry_run:
        logger.info(f"  Inserting {len(result_batch)} results...")
        inserted = 0
        for i in range(0, len(result_batch), 50):
            chunk = result_batch[i:i + 50]
            try:
                supabase.table('results').insert(chunk).execute()
                inserted += len(chunk)
            except Exception as e:
                logger.warning(f"  Batch failed at offset {i}, trying one-by-one: {e}")
                for rd in chunk:
                    try:
                        supabase.table('results').insert(rd).execute()
                        inserted += 1
                    except Exception as e2:
                        err_str = str(e2).lower()
                        if 'duplicate' in err_str or 'unique' in err_str:
                            stats['skipped_duplicate'] += 1
                        else:
                            logger.debug(f"    Insert failed: {rd['performance']} - {e2}")
                            stats['errors'] += 1
        stats['imported'] = inserted

    return stats


# ============================================================
# New athlete report
# ============================================================

def write_new_athlete_report(new_athletes: List[Dict], filename: str):
    report_dir = os.path.join(os.path.dirname(__file__), 'new_meets_data')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, filename)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"New Athletes Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {len(new_athletes)} new athletes\n")
        f.write("=" * 60 + "\n\n")
        for a in new_athletes:
            f.write(f"  {a['name']} ({a['gender']}, {a.get('birth_year', '?')}) - {a.get('club', 'no club')}\n")
    logger.info(f"New athlete report: {report_path}")


# ============================================================
# CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Import historical all-time statistics from friidrett.no'
    )
    parser.add_argument('--gender', required=True, choices=['M', 'F'])
    parser.add_argument('--event', help='Event key (e.g. 100, 200, hoyde, kule)')
    parser.add_argument('--all', action='store_true', help='Import all events')
    parser.add_argument('--youth', action='store_true', help='Import youth (13-18)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    parser.add_argument('--list-events', action='store_true', help='List available events')
    return parser.parse_args()


def process_event(gender: str, event_key: str, youth: bool, dry_run: bool,
                  source_id: Optional[str]) -> Dict:
    events = YOUTH_EVENTS if youth else SENIOR_EVENTS
    if event_key not in events:
        logger.error(f"Unknown event: {event_key}")
        return {'total_parsed': 0, 'imported': 0, 'errors': 1}

    codes = events[event_key]
    event_code = codes[0] if gender == 'M' else codes[1]
    if not event_code:
        logger.warning(f"Event {event_key} not available for gender {gender}")
        return {'total_parsed': 0, 'imported': 0}

    event_id = _event_cache.get(event_code)
    if not event_id:
        logger.error(f"Event code '{event_code}' not found in database")
        return {'total_parsed': 0, 'imported': 0, 'errors': 1}

    url = build_youth_url(gender, event_key) if youth else build_senior_url(gender, event_key)
    logger.info(f"Fetching: {url}")

    html = fetch_page(url)
    if not html:
        return {'total_parsed': 0, 'imported': 0, 'errors': 1}

    parsed = parse_youth_page(html, gender, event_code) if youth else parse_senior_page(html, gender, event_code)
    if not parsed:
        logger.warning("No results parsed")
        return {'total_parsed': 0, 'imported': 0}

    # Load existing results for dedup
    if not dry_run:
        load_existing_results_for_event(event_id)

    # Create import batch
    batch_id = None
    if not dry_run:
        category = "youth" if youth else "senior"
        batch_id = create_import_batch(f"historical_{category}_{gender}_{event_key}")

    stats = import_results(parsed, event_id, source_id, batch_id, dry_run=dry_run)

    if batch_id:
        update_import_batch(
            batch_id,
            row_count=stats['imported'],
            status='imported' if stats['errors'] == 0 else 'needs_review',
            matched=stats['matched_existing_athlete'],
            unmatched=stats['created_new_athlete'],
        )

    return stats


def main():
    args = parse_args()
    events = YOUTH_EVENTS if args.youth else SENIOR_EVENTS

    if args.list_events:
        category = "Youth" if args.youth else "Senior"
        print(f"\nAvailable {category} events for {'Men' if args.gender == 'M' else 'Women'}:")
        for key, (m_code, f_code) in sorted(events.items()):
            code = m_code if args.gender == 'M' else f_code
            if code:
                print(f"  {key:20s} -> {code}")
        return

    if not args.event and not args.all:
        print("Error: specify --event or --all")
        return

    event_keys = []
    if args.all:
        for key, (m_code, f_code) in events.items():
            code = m_code if args.gender == 'M' else f_code
            if code:
                event_keys.append(key)
    else:
        event_keys = [args.event]

    category = "youth" if args.youth else "senior"
    gender_label = "Men" if args.gender == 'M' else "Women"

    logger.info("=" * 60)
    logger.info(f"IMPORT HISTORICAL - {gender_label} {category}")
    logger.info(f"Events: {', '.join(event_keys)}")
    if args.dry_run:
        logger.info("*** DRY RUN - no changes ***")
    logger.info("=" * 60)

    # Load reference data
    logger.info("\nLoading reference data...")
    load_events()
    load_seasons()
    load_clubs()
    load_athletes()
    if args.youth:
        load_age_classes()

    source_id = None
    if not args.dry_run:
        source_id = get_or_create_source()

    # Process
    totals = {k: 0 for k in [
        'total_parsed', 'imported', 'skipped_duplicate', 'skipped_no_athlete',
        'skipped_no_meet', 'skipped_no_season', 'matched_existing_athlete',
        'created_new_athlete', 'errors', 'events_processed',
    ]}
    all_new_athletes = []

    for event_key in event_keys:
        logger.info(f"\n{'=' * 40}")
        logger.info(f"Processing: {event_key} ({gender_label} {category})")
        logger.info(f"{'=' * 40}")

        stats = process_event(args.gender, event_key, args.youth, args.dry_run, source_id)

        totals['events_processed'] += 1
        for k in ['total_parsed', 'imported', 'skipped_duplicate', 'skipped_no_athlete',
                   'skipped_no_meet', 'skipped_no_season', 'matched_existing_athlete',
                   'created_new_athlete', 'errors']:
            totals[k] += stats.get(k, 0)

        if stats.get('new_athletes'):
            all_new_athletes.extend(stats['new_athletes'])

        logger.info(f"  Parsed: {stats.get('total_parsed', 0)}")
        logger.info(f"  Imported: {stats.get('imported', 0)}")
        logger.info(f"  Duplicates skipped: {stats.get('skipped_duplicate', 0)}")
        logger.info(f"  Athletes matched: {stats.get('matched_existing_athlete', 0)}")
        logger.info(f"  Athletes created: {stats.get('created_new_athlete', 0)}")

    # Write new athlete report
    if all_new_athletes:
        report_name = f"new_athletes_{category}_{args.gender}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        write_new_athlete_report(all_new_athletes, report_name)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("IMPORT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Category: {gender_label} {category}")
    logger.info(f"Events processed: {totals['events_processed']}")
    logger.info(f"Total parsed: {totals['total_parsed']}")
    logger.info(f"Imported: {totals['imported']}")
    logger.info(f"Duplicates skipped: {totals['skipped_duplicate']}")
    logger.info(f"  Athletes matched: {totals['matched_existing_athlete']}")
    logger.info(f"  Athletes created: {totals['created_new_athlete']}")
    logger.info(f"  Skipped (no athlete): {totals['skipped_no_athlete']}")
    logger.info(f"  Skipped (no meet): {totals['skipped_no_meet']}")
    logger.info(f"  Skipped (no season): {totals['skipped_no_season']}")
    logger.info(f"  Errors: {totals['errors']}")
    if all_new_athletes:
        logger.info(f"  New athletes: {len(all_new_athletes)} (see report)")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
