"""
Unified Athletics Statistics Scraper

Combines competition-based scraping (2011+) with athlete-based scraping (all years)
to build the most complete and accurate dataset.

STRATEGY:
=========
1. PHASE 1: Scrape all competitions (2011+)
   - Gets real competition IDs, venues, organizers, date ranges
   - Results linked by competition_id
   - Athletes identified by name + birth_year

2. PHASE 2: Scrape all athletes
   - Gets athlete source IDs, full names, birth dates
   - Gets ALL historical results (including pre-2011)
   - Pre-2011 results get "derived" competition records

3. PHASE 3: Link & merge
   - Match competition-scraped athletes to athlete-scraped records
   - Enrich results with proper athlete_ids
   - Deduplicate where both sources have same result

Usage:
    python unified_scraper.py init
    python unified_scraper.py phase1              # Scrape competitions (2011+)
    python unified_scraper.py phase2              # Scrape athletes (all years)
    python unified_scraper.py phase3              # Link and merge
    python unified_scraper.py status
    python unified_scraper.py export              # Export to CSV for Supabase
"""

import requests
import sqlite3
import re
import sys
import time
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, List, Set, Tuple
import logging
import os

# Configuration
DB_PATH = "athletics_unified.db"
SEARCH_HTML_DIR = "athlete_search_html"
DELAY_BETWEEN_REQUESTS = 0.25
MAX_RETRIES = 3
COMPETITION_LINK_CUTOFF_YEAR = 2011  # Competition links exist from this year

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_scrape.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =====================================================
# DATABASE SCHEMA
# =====================================================

SCHEMA = """
-- =====================================================
-- COMPETITIONS TABLE
-- Stores both real (2011+) and derived (pre-2011) competitions
-- =====================================================
CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER UNIQUE,            -- Original ID from StevneResultater (NULL for derived)
    name TEXT NOT NULL,
    venue TEXT,
    organizer TEXT,
    start_date TEXT,                     -- YYYY-MM-DD
    end_date TEXT,
    year INTEGER,
    is_outdoor INTEGER DEFAULT 1,
    is_derived INTEGER DEFAULT 0,        -- 1 if created from athlete scrape, 0 if from competition scrape
    derived_hash TEXT UNIQUE,            -- Hash for derived competitions (date|venue|name)
    source TEXT,                         -- 'competition_scrape' or 'athlete_scrape'
    scraped_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- ATHLETES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER UNIQUE,            -- Original athlete ID from source system
    name TEXT NOT NULL,
    birth_date TEXT,                     -- YYYY-MM-DD (full date from athlete scrape)
    birth_year INTEGER,                  -- Just year (from competition scrape or derived)
    source TEXT,                         -- 'athlete_scrape' or 'competition_scrape'
    scraped_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Index for matching athletes by name + birth year
CREATE INDEX IF NOT EXISTS idx_athletes_name_year ON athletes(name, birth_year);

-- =====================================================
-- CLUBS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- EVENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    is_timed INTEGER DEFAULT 1,
    higher_is_better INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- AGE CLASSES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS age_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- RESULTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER REFERENCES competitions(id),
    athlete_id INTEGER REFERENCES athletes(id),
    event_id INTEGER NOT NULL REFERENCES events(id),
    club_id INTEGER REFERENCES clubs(id),
    age_class_id INTEGER REFERENCES age_classes(id),

    result TEXT NOT NULL,
    result_numeric REAL,
    wind TEXT,
    placement TEXT,

    year INTEGER,
    age INTEGER,                         -- Athlete's age at competition
    date TEXT,                           -- YYYY-MM-DD
    is_outdoor INTEGER DEFAULT 1,
    is_approved INTEGER DEFAULT 1,
    rejection_reason TEXT,

    source TEXT,                         -- 'competition_scrape' or 'athlete_scrape'
    source_athlete_id INTEGER,           -- For linking back
    source_competition_id INTEGER,       -- For linking back

    created_at TEXT DEFAULT (datetime('now')),

    -- Unique constraint to prevent duplicates
    UNIQUE(athlete_id, event_id, date, result, placement, is_outdoor)
);

-- =====================================================
-- SCRAPE TRACKING TABLES
-- =====================================================

-- Track discovered competition IDs
CREATE TABLE IF NOT EXISTS competition_discovery (
    source_id INTEGER PRIMARY KEY,
    discovered_at TEXT DEFAULT (datetime('now')),
    scraped INTEGER DEFAULT 0,
    scraped_at TEXT,
    result_count INTEGER
);

-- Track athlete scraping progress
CREATE TABLE IF NOT EXISTS athlete_scrape_progress (
    letter TEXT PRIMARY KEY,
    total_athletes INTEGER,
    processed_count INTEGER DEFAULT 0,
    last_index INTEGER DEFAULT 0,
    started_at TEXT,
    completed_at TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- =====================================================
-- INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_results_competition ON results(competition_id);
CREATE INDEX IF NOT EXISTS idx_results_athlete ON results(athlete_id);
CREATE INDEX IF NOT EXISTS idx_results_event ON results(event_id);
CREATE INDEX IF NOT EXISTS idx_results_date ON results(date);
CREATE INDEX IF NOT EXISTS idx_results_year ON results(year);
CREATE INDEX IF NOT EXISTS idx_competitions_year ON competitions(year);
CREATE INDEX IF NOT EXISTS idx_competitions_source_id ON competitions(source_id);
CREATE INDEX IF NOT EXISTS idx_competitions_derived_hash ON competitions(derived_hash);
CREATE INDEX IF NOT EXISTS idx_athletes_source_id ON athletes(source_id);

-- =====================================================
-- VIEWS
-- =====================================================
CREATE VIEW IF NOT EXISTS results_full AS
SELECT
    r.id,
    r.date,
    r.year,
    r.age,
    r.result,
    r.result_numeric,
    r.wind,
    r.placement,
    r.is_outdoor,
    r.is_approved,
    r.rejection_reason,
    r.source as result_source,
    a.id as athlete_id,
    a.source_id as athlete_source_id,
    a.name as athlete_name,
    a.birth_date,
    a.birth_year,
    e.id as event_id,
    e.name as event_name,
    e.category as event_category,
    cl.id as club_id,
    cl.name as club_name,
    c.id as competition_id,
    c.source_id as competition_source_id,
    c.name as competition_name,
    c.venue,
    c.organizer,
    c.is_derived as competition_is_derived,
    ac.name as age_class
FROM results r
LEFT JOIN athletes a ON r.athlete_id = a.id
LEFT JOIN events e ON r.event_id = e.id
LEFT JOIN clubs cl ON r.club_id = cl.id
LEFT JOIN competitions c ON r.competition_id = c.id
LEFT JOIN age_classes ac ON r.age_class_id = ac.id;
"""


def init_database():
    """Initialize the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    logger.info(f"Database initialized: {DB_PATH}")


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def make_request(url, method='GET', data=None, params=None):
    """Make HTTP request with retry logic"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    for attempt in range(MAX_RETRIES):
        try:
            if method == 'POST':
                response = requests.post(url, data=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, params=params, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
            else:
                raise
    return ""


def get_or_create(conn, table, name_col, value, extra_cols=None):
    """Get or create a record, return its ID"""
    if not value or (isinstance(value, str) and not value.strip()):
        return None

    if isinstance(value, str):
        value = value.strip()

    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE {name_col} = ?", (value,))
    row = cursor.fetchone()
    if row:
        return row[0]

    if extra_cols:
        cols = [name_col] + list(extra_cols.keys())
        vals = [value] + list(extra_cols.values())
        placeholders = ','.join(['?' for _ in vals])
        cursor.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})", vals)
    else:
        cursor.execute(f"INSERT INTO {table} ({name_col}) VALUES (?)", (value,))

    return cursor.lastrowid


def parse_date(date_str: str, format='short') -> Optional[str]:
    """Parse date to YYYY-MM-DD"""
    if not date_str:
        return None
    try:
        date_str = date_str.strip()
        if format == 'short':  # DD.MM.YY
            parts = date_str.split('.')
            if len(parts) == 3:
                day, month, year = parts
                year = int(year)
                year = 1900 + year if year > 50 else 2000 + year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:  # DD.MM.YYYY
            parts = date_str.split('.')
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None


def parse_date_range(date_str: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse '27.06.2025 til 29.06.2025' or single date"""
    if not date_str:
        return None, None

    if ' til ' in date_str:
        parts = date_str.split(' til ')
        start = parse_date(parts[0].strip(), 'long')
        end = parse_date(parts[1].strip(), 'long')
        return start, end
    else:
        d = parse_date(date_str.strip(), 'long')
        return d, d


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str]]:
    """Parse '9,17(+0,9)' into result and wind"""
    if not result_str:
        return '', None

    result_str = result_str.strip()
    match = re.match(r'(.+?)\(([+-]?\d+[,.]?\d*)\)\s*$', result_str)
    if match:
        return match.group(1).strip(), match.group(2)

    return result_str, None


def parse_athlete_name_year(name_str: str) -> Tuple[str, Optional[int]]:
    """Parse 'Athlete Name(1990)' -> (name, birth_year)"""
    if not name_str:
        return '', None

    match = re.match(r'(.+?)\((\d{4})\)$', name_str.strip())
    if match:
        return match.group(1).strip(), int(match.group(2))

    match = re.match(r'(.+?)\(0+\)$', name_str.strip())
    if match:
        return match.group(1).strip(), None

    return name_str.strip(), None


def parse_year_age(year_age_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse '2015 (14)' -> (year, age)"""
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


def derive_competition_hash(date: str, venue: str, name: str) -> str:
    """Create a stable hash for derived competitions"""
    # Normalize name - remove location prefix
    if name:
        name = re.sub(r'^[^,]+,\s*', '', name).strip().lower()
    key = f"{date or ''}|{venue or ''}|{name or ''}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def categorize_event(event_name: str) -> Tuple[str, bool, bool]:
    """Return (category, is_timed, higher_is_better)"""
    name_lower = event_name.lower()

    if any(x in name_lower for x in ['tikamp', 'sjukamp', 'femkamp', 'mangekamp']):
        return 'combined', False, True
    if any(x in name_lower for x in ['stafett', 'relay', '4x']):
        return 'relay', True, False
    if any(x in name_lower for x in ['hekk', 'hinder']):
        return 'hurdles', True, False
    if any(x in name_lower for x in ['kule', 'diskos', 'spyd', 'slegge', 'vektkast']):
        return 'throws', False, True
    if any(x in name_lower for x in ['høyde', 'stav', 'lengde', 'tresteg']):
        return 'jumps', False, True
    if any(x in name_lower for x in ['kappgang', 'gang']):
        return 'walk', True, False

    # Distance-based
    match = re.search(r'(\d+)\s*m', name_lower)
    if match:
        meters = int(match.group(1))
        if meters <= 400:
            return 'sprint', True, False
        elif meters <= 1500:
            return 'middle_distance', True, False
        else:
            return 'long_distance', True, False

    if 'km' in name_lower or 'maraton' in name_lower:
        return 'long_distance', True, False

    return 'other', True, False


# =====================================================
# PHASE 1: COMPETITION SCRAPING (2011+)
# =====================================================

def discover_competition_ids(years: List[int] = None):
    """Discover competition IDs from LandsStatistikk rankings"""
    conn = get_connection()
    cursor = conn.cursor()

    if years is None:
        current_year = datetime.now().year
        years = list(range(COMPETITION_LINK_CUTOFF_YEAR, current_year + 1))

    # Event and class IDs to scan
    events = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24,  # Running
              68, 70, 72, 74, 76, 78, 80, 82,  # Field
              84, 86, 88, 90]  # Combined/other
    classes = list(range(1, 50))

    all_ids = set()
    total = len(events) * len(classes) * len(years) * 2
    processed = 0

    logger.info(f"Discovering competitions from {min(years)} to {max(years)}...")

    for outdoor in ['Y', 'N']:
        for year in years:
            for event in events:
                for cls in classes:
                    try:
                        url = "https://www.minfriidrettsstatistikk.info/php/LandsStatistikk.php"
                        params = {
                            'showclass': cls,
                            'showevent': event,
                            'showseason': year,
                            'outdoor': outdoor,
                            'showclub': 0
                        }

                        html = make_request(url, params=params)

                        # Extract competition IDs
                        pattern = r'posttoresultlist\((\d+)\)'
                        matches = re.findall(pattern, html)

                        for comp_id in matches:
                            comp_id = int(comp_id)
                            cursor.execute("""
                                INSERT OR IGNORE INTO competition_discovery (source_id)
                                VALUES (?)
                            """, (comp_id,))
                            all_ids.add(comp_id)

                        processed += 1
                        if processed % 500 == 0:
                            conn.commit()
                            logger.info(f"Discovery progress: {processed}/{total} - Found {len(all_ids)} competitions")

                        time.sleep(DELAY_BETWEEN_REQUESTS)

                    except Exception as e:
                        logger.error(f"Error discovering: {e}")

    conn.commit()
    conn.close()

    logger.info(f"Discovery complete. Found {len(all_ids)} unique competition IDs")
    return all_ids


def scrape_competition(conn, source_id: int) -> int:
    """Scrape a single competition, return result count"""
    cursor = conn.cursor()

    url = "https://www.minfriidrettsstatistikk.info/php/StevneResultater.php"
    html = make_request(url, method='POST', data={'competition': source_id})

    soup = BeautifulSoup(html, 'html.parser')

    # Parse header
    comp_data = {
        'source_id': source_id,
        'name': None,
        'venue': None,
        'organizer': None,
        'start_date': None,
        'end_date': None
    }

    header = soup.find('div', id='header')
    if header:
        table = header.find('table')
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).upper()
                    value = cells[1].get_text(strip=True)

                    if 'STEVNE' in label:
                        comp_data['name'] = value
                    elif 'DATO' in label:
                        comp_data['start_date'], comp_data['end_date'] = parse_date_range(value)
                    elif 'STED' in label:
                        comp_data['venue'] = value
                    elif 'ARRANGØR' in label:
                        comp_data['organizer'] = value

    if not comp_data['name']:
        return 0

    # Extract year
    year = None
    if comp_data['start_date']:
        year = int(comp_data['start_date'][:4])

    # Insert competition
    cursor.execute("""
        INSERT OR REPLACE INTO competitions
        (source_id, name, venue, organizer, start_date, end_date, year, is_derived, source, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'competition_scrape', datetime('now'))
    """, (
        source_id, comp_data['name'], comp_data['venue'], comp_data['organizer'],
        comp_data['start_date'], comp_data['end_date'], year
    ))

    competition_id = cursor.lastrowid
    # Get the actual ID if it was a replace
    cursor.execute("SELECT id FROM competitions WHERE source_id = ?", (source_id,))
    competition_id = cursor.fetchone()[0]

    # Parse results
    current_class = None
    current_event = None
    result_count = 0

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
            for row in element.find_all('tr'):
                cells = row.find_all('td')
                if not cells or len(cells) < 4:
                    continue

                placement = cells[0].get_text(strip=True)
                result_raw = cells[1].get_text(strip=True)
                result, wind = parse_result_wind(result_raw)

                name_raw = cells[2].get_text(strip=True)
                athlete_name, birth_year = parse_athlete_name_year(name_raw)

                club = cells[3].get_text(strip=True) if len(cells) > 3 else None

                if not athlete_name or not result:
                    continue

                # Get or create athlete (by name + birth_year for competition scrape)
                cursor.execute("""
                    SELECT id FROM athletes
                    WHERE name = ? AND (birth_year = ? OR (birth_year IS NULL AND ? IS NULL))
                """, (athlete_name, birth_year, birth_year))
                athlete_row = cursor.fetchone()

                if athlete_row:
                    athlete_id = athlete_row[0]
                else:
                    cursor.execute("""
                        INSERT INTO athletes (name, birth_year, source)
                        VALUES (?, ?, 'competition_scrape')
                    """, (athlete_name, birth_year))
                    athlete_id = cursor.lastrowid

                # Get or create other entities
                event_id = get_or_create(conn, 'events', 'name', current_event)
                club_id = get_or_create(conn, 'clubs', 'name', club)
                class_id = get_or_create(conn, 'age_classes', 'name', current_class)

                # Insert result
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO results
                        (competition_id, athlete_id, event_id, club_id, age_class_id,
                         result, wind, placement, date, year, is_outdoor,
                         source, source_competition_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'competition_scrape', ?)
                    """, (
                        competition_id, athlete_id, event_id, club_id, class_id,
                        result, wind, placement, comp_data['start_date'], year, source_id
                    ))
                    result_count += 1
                except sqlite3.IntegrityError:
                    pass

    # Update discovery record
    cursor.execute("""
        UPDATE competition_discovery
        SET scraped = 1, scraped_at = datetime('now'), result_count = ?
        WHERE source_id = ?
    """, (result_count, source_id))

    return result_count


def run_phase1():
    """Run Phase 1: Scrape all competitions (2011+)"""
    logger.info("=" * 60)
    logger.info("PHASE 1: Competition Scraping (2011+)")
    logger.info("=" * 60)

    conn = get_connection()
    cursor = conn.cursor()

    # First, discover competition IDs
    cursor.execute("SELECT COUNT(*) FROM competition_discovery")
    discovered = cursor.fetchone()[0]

    if discovered == 0:
        logger.info("No competitions discovered yet. Running discovery...")
        conn.close()
        discover_competition_ids()
        conn = get_connection()
        cursor = conn.cursor()

    # Get unscraped competitions
    cursor.execute("""
        SELECT source_id FROM competition_discovery
        WHERE scraped = 0
        ORDER BY source_id DESC
    """)
    to_scrape = [row[0] for row in cursor.fetchall()]

    logger.info(f"Scraping {len(to_scrape)} competitions...")

    total_results = 0
    for i, source_id in enumerate(to_scrape):
        try:
            count = scrape_competition(conn, source_id)
            total_results += count

            if (i + 1) % 10 == 0:
                conn.commit()

            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i + 1}/{len(to_scrape)} competitions, {total_results} results")

            time.sleep(DELAY_BETWEEN_REQUESTS)

        except Exception as e:
            logger.error(f"Error scraping competition {source_id}: {e}")

    conn.commit()
    conn.close()

    logger.info(f"Phase 1 complete. Scraped {len(to_scrape)} competitions, {total_results} results")


# =====================================================
# PHASE 2: ATHLETE SCRAPING (All years)
# =====================================================

def get_athletes_for_letter(letter: str) -> List[Tuple[int, str]]:
    """Get athlete IDs and names for a letter from search HTML"""
    search_file = os.path.join(SEARCH_HTML_DIR, f"search_{letter}.html")

    if not os.path.exists(search_file):
        raise FileNotFoundError(f"Search file not found: {search_file}")

    with open(search_file, 'r', encoding='utf-8') as f:
        html = f.read()

    pattern = r'showathl=(\d+)[^>]*>([^<]+)'
    matches = re.findall(pattern, html)

    return [(int(aid), name.strip()) for aid, name in matches]


def scrape_athlete(conn, source_id: int) -> Tuple[int, int]:
    """Scrape a single athlete, return (new_results, total_results)"""
    cursor = conn.cursor()

    url = "https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php"
    html = make_request(url, method='POST', data={'athlete': source_id, 'type': 'RES'})

    soup = BeautifulSoup(html, 'html.parser')

    # Parse athlete info
    athlete_name = None
    birth_date = None

    athlete_div = soup.find('div', id='athlete')
    if athlete_div:
        name_tag = athlete_div.find('h2')
        if name_tag:
            athlete_name = name_tag.get_text(strip=True)

        birth_tag = athlete_div.find('h3')
        if birth_tag:
            birth_text = birth_tag.get_text(strip=True)
            match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', birth_text)
            if match:
                day, month, year = match.groups()
                birth_date = f"{year}-{month}-{day}"

    if not athlete_name:
        return 0, 0

    # Get birth year from date
    birth_year = int(birth_date[:4]) if birth_date else None

    # Find or create athlete
    # First check if we have this athlete from competition scrape
    cursor.execute("""
        SELECT id FROM athletes
        WHERE name = ? AND (birth_year = ? OR (birth_year IS NULL AND ? IS NULL))
    """, (athlete_name, birth_year, birth_year))
    athlete_row = cursor.fetchone()

    if athlete_row:
        athlete_id = athlete_row[0]
        # Update with source_id and birth_date if we have them
        cursor.execute("""
            UPDATE athletes
            SET source_id = ?, birth_date = COALESCE(birth_date, ?),
                source = 'athlete_scrape', scraped_at = datetime('now')
            WHERE id = ?
        """, (source_id, birth_date, athlete_id))
    else:
        cursor.execute("""
            INSERT INTO athletes (source_id, name, birth_date, birth_year, source, scraped_at)
            VALUES (?, ?, ?, ?, 'athlete_scrape', datetime('now'))
        """, (source_id, athlete_name, birth_date, birth_year))
        athlete_id = cursor.lastrowid

    # Parse results
    current_section = None
    current_event = None
    is_approved_section = True

    new_results = 0
    total_results = 0

    for element in soup.find_all(['div', 'table', 'h4']):
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                text = h2.get_text(strip=True)
                current_section = 'outdoor' if 'UTENDØRS' in text else 'indoor'

        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)
                is_approved_section = True

        elif element.name == 'h4':
            if 'Ikke godkjente' in element.get_text(strip=True):
                is_approved_section = False

        elif element.name == 'table' and current_event and current_section:
            for row in element.find_all('tr'):
                cells = row.find_all('td')
                if not cells or len(cells) < 6:
                    continue

                year, age = parse_year_age(cells[0].get_text())
                result_raw = cells[1].get_text(strip=True)
                result, wind = parse_result_wind(result_raw)
                placement = cells[2].get_text(strip=True)
                club = cells[3].get_text(strip=True)
                date_str = cells[4].get_text(strip=True)
                date = parse_date(date_str, 'short')

                location_cell = cells[5]
                venue = location_cell.get('title', '').strip()
                competition_name = location_cell.get_text(strip=True)

                rejection_reason = None
                if len(cells) >= 7 and not is_approved_section:
                    rejection_reason = cells[6].get_text(strip=True)

                if not result:
                    continue

                total_results += 1
                is_outdoor = 1 if current_section == 'outdoor' else 0

                # Find or create competition
                competition_id = None

                if year and year >= COMPETITION_LINK_CUTOFF_YEAR:
                    # Try to find existing competition by matching criteria
                    # This is approximate - competition scrape is the authority
                    cursor.execute("""
                        SELECT id FROM competitions
                        WHERE is_derived = 0
                        AND year = ?
                        AND (venue = ? OR ? IS NULL OR venue IS NULL)
                        AND name LIKE ?
                        LIMIT 1
                    """, (year, venue, venue, f"%{competition_name.split(',')[-1].strip() if competition_name else ''}%"))
                    comp_row = cursor.fetchone()
                    if comp_row:
                        competition_id = comp_row[0]

                if not competition_id:
                    # Create derived competition
                    derived_hash = derive_competition_hash(date, venue, competition_name)

                    cursor.execute("SELECT id FROM competitions WHERE derived_hash = ?", (derived_hash,))
                    comp_row = cursor.fetchone()

                    if comp_row:
                        competition_id = comp_row[0]
                    else:
                        cursor.execute("""
                            INSERT INTO competitions
                            (name, venue, start_date, end_date, year, is_outdoor, is_derived, derived_hash, source)
                            VALUES (?, ?, ?, ?, ?, ?, 1, ?, 'athlete_scrape')
                        """, (competition_name, venue, date, date, year, is_outdoor, derived_hash))
                        competition_id = cursor.lastrowid

                # Get or create other entities
                event_id = get_or_create(conn, 'events', 'name', current_event)
                club_id = get_or_create(conn, 'clubs', 'name', club)

                # Insert result
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO results
                        (competition_id, athlete_id, event_id, club_id,
                         result, wind, placement, date, year, age, is_outdoor,
                         is_approved, rejection_reason, source, source_athlete_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'athlete_scrape', ?)
                    """, (
                        competition_id, athlete_id, event_id, club_id,
                        result, wind, placement, date, year, age, is_outdoor,
                        1 if is_approved_section else 0, rejection_reason, source_id
                    ))
                    if cursor.rowcount > 0:
                        new_results += 1
                except sqlite3.IntegrityError:
                    pass

    return new_results, total_results


def run_phase2(letters: List[str] = None):
    """Run Phase 2: Scrape all athletes"""
    logger.info("=" * 60)
    logger.info("PHASE 2: Athlete Scraping (All years)")
    logger.info("=" * 60)

    if letters is None:
        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ")

    conn = get_connection()
    cursor = conn.cursor()

    for letter in letters:
        try:
            athletes = get_athletes_for_letter(letter)
        except FileNotFoundError:
            logger.warning(f"No search file for letter {letter}, skipping")
            continue

        total = len(athletes)

        # Check progress
        cursor.execute("SELECT last_index FROM athlete_scrape_progress WHERE letter = ?", (letter,))
        row = cursor.fetchone()
        start_idx = row[0] if row else 0

        if start_idx >= total:
            logger.info(f"Letter {letter} already complete, skipping")
            continue

        logger.info(f"Scraping letter {letter}: {total} athletes (starting at {start_idx})")

        # Initialize progress record
        cursor.execute("""
            INSERT OR REPLACE INTO athlete_scrape_progress
            (letter, total_athletes, processed_count, last_index, started_at, updated_at)
            VALUES (?, ?, ?, ?, COALESCE((SELECT started_at FROM athlete_scrape_progress WHERE letter = ?), datetime('now')), datetime('now'))
        """, (letter, total, start_idx, start_idx, letter))
        conn.commit()

        total_new = 0
        total_all = 0

        for i in range(start_idx, total):
            source_id, name = athletes[i]

            try:
                new, all_results = scrape_athlete(conn, source_id)
                total_new += new
                total_all += all_results

                if (i + 1) % 50 == 0:
                    cursor.execute("""
                        UPDATE athlete_scrape_progress
                        SET processed_count = ?, last_index = ?, updated_at = datetime('now')
                        WHERE letter = ?
                    """, (i + 1, i + 1, letter))
                    conn.commit()
                    logger.info(f"Letter {letter}: {i + 1}/{total} - {total_new} new results")

                time.sleep(DELAY_BETWEEN_REQUESTS)

            except Exception as e:
                logger.error(f"Error scraping athlete {source_id} ({name}): {e}")

        # Mark letter complete
        cursor.execute("""
            UPDATE athlete_scrape_progress
            SET processed_count = ?, last_index = ?, completed_at = datetime('now')
            WHERE letter = ?
        """, (total, total, letter))
        conn.commit()

        logger.info(f"Letter {letter} complete: {total_new} new results, {total_all} total")

    conn.close()
    logger.info("Phase 2 complete")


# =====================================================
# PHASE 3: LINKING & CLEANUP
# =====================================================

def run_phase3():
    """Run Phase 3: Link and clean up data"""
    logger.info("=" * 60)
    logger.info("PHASE 3: Linking & Cleanup")
    logger.info("=" * 60)

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Link athletes from competition scrape to athlete scrape by name + birth_year
    logger.info("Linking athletes...")
    cursor.execute("""
        UPDATE athletes AS a1
        SET source_id = (
            SELECT a2.source_id FROM athletes a2
            WHERE a2.source_id IS NOT NULL
            AND a2.name = a1.name
            AND (a2.birth_year = a1.birth_year OR a2.birth_year IS NULL OR a1.birth_year IS NULL)
            LIMIT 1
        )
        WHERE a1.source_id IS NULL
    """)
    logger.info(f"  Updated {cursor.rowcount} athlete records with source IDs")

    # 2. Update birth_date where we have it
    cursor.execute("""
        UPDATE athletes AS a1
        SET birth_date = (
            SELECT a2.birth_date FROM athletes a2
            WHERE a2.birth_date IS NOT NULL
            AND a2.name = a1.name
            AND (a2.birth_year = a1.birth_year OR a2.birth_year IS NULL OR a1.birth_year IS NULL)
            LIMIT 1
        )
        WHERE a1.birth_date IS NULL
    """)
    logger.info(f"  Updated {cursor.rowcount} athlete records with birth dates")

    # 3. Categorize events
    logger.info("Categorizing events...")
    cursor.execute("SELECT id, name FROM events WHERE category IS NULL")
    events = cursor.fetchall()

    for event in events:
        category, is_timed, higher_is_better = categorize_event(event['name'])
        cursor.execute("""
            UPDATE events SET category = ?, is_timed = ?, higher_is_better = ?
            WHERE id = ?
        """, (category, is_timed, higher_is_better, event['id']))

    logger.info(f"  Categorized {len(events)} events")

    conn.commit()
    conn.close()

    logger.info("Phase 3 complete")


# =====================================================
# STATUS & EXPORT
# =====================================================

def show_status():
    """Show scraping status"""
    conn = get_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("UNIFIED SCRAPER STATUS")
    print("=" * 70)

    # Overall stats
    stats = {}
    for table in ['athletes', 'competitions', 'results', 'events', 'clubs']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]

    print(f"\nAthletes:     {stats['athletes']:>10,}")
    print(f"Competitions: {stats['competitions']:>10,}")
    print(f"Results:      {stats['results']:>10,}")
    print(f"Events:       {stats['events']:>10,}")
    print(f"Clubs:        {stats['clubs']:>10,}")

    # Competition discovery
    print("\n" + "-" * 70)
    print("PHASE 1: Competition Scraping (2011+)")

    cursor.execute("SELECT COUNT(*) FROM competition_discovery")
    discovered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM competition_discovery WHERE scraped = 1")
    scraped = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM competitions WHERE is_derived = 0")
    real_comps = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results WHERE source = 'competition_scrape'")
    comp_results = cursor.fetchone()[0]

    print(f"  Discovered competitions: {discovered:,}")
    print(f"  Scraped competitions:    {scraped:,}")
    print(f"  Real competitions:       {real_comps:,}")
    print(f"  Results from comps:      {comp_results:,}")

    # Athlete scraping
    print("\n" + "-" * 70)
    print("PHASE 2: Athlete Scraping (All years)")

    cursor.execute("""
        SELECT letter, total_athletes, processed_count, completed_at
        FROM athlete_scrape_progress
        ORDER BY letter
    """)
    progress = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM competitions WHERE is_derived = 1")
    derived_comps = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results WHERE source = 'athlete_scrape'")
    athlete_results = cursor.fetchone()[0]

    total_athletes = sum(p['total_athletes'] for p in progress)
    total_processed = sum(p['processed_count'] for p in progress)
    completed_letters = sum(1 for p in progress if p['completed_at'])

    print(f"  Letters completed: {completed_letters}/29")
    print(f"  Athletes scraped:  {total_processed:,}/{total_athletes:,}")
    print(f"  Derived competitions: {derived_comps:,}")
    print(f"  Results from athletes: {athlete_results:,}")

    # Data quality
    print("\n" + "-" * 70)
    print("DATA QUALITY")

    cursor.execute("SELECT COUNT(*) FROM athletes WHERE source_id IS NOT NULL")
    athletes_with_id = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM athletes WHERE birth_date IS NOT NULL")
    athletes_with_dob = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results WHERE competition_id IS NOT NULL")
    results_with_comp = cursor.fetchone()[0]

    print(f"  Athletes with source ID: {athletes_with_id:,}/{stats['athletes']:,}")
    print(f"  Athletes with birth date: {athletes_with_dob:,}/{stats['athletes']:,}")
    print(f"  Results with competition: {results_with_comp:,}/{stats['results']:,}")

    # Year distribution
    print("\n" + "-" * 70)
    print("RESULTS BY DECADE")

    cursor.execute("""
        SELECT (year/10)*10 as decade, COUNT(*) as count
        FROM results
        WHERE year IS NOT NULL
        GROUP BY decade
        ORDER BY decade
    """)

    for row in cursor.fetchall():
        bar = "#" * (row['count'] // 50000)
        print(f"  {row['decade']}s: {row['count']:>10,} {bar}")

    conn.close()
    print("=" * 70)


def export_to_csv():
    """Export data to CSV files for Supabase import"""
    import csv

    os.makedirs('export', exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    tables = [
        ('athletes', ['id', 'source_id', 'name', 'birth_date', 'birth_year']),
        ('clubs', ['id', 'name']),
        ('events', ['id', 'name', 'category', 'is_timed', 'higher_is_better']),
        ('age_classes', ['id', 'name']),
        ('competitions', ['id', 'source_id', 'name', 'venue', 'organizer', 'start_date', 'end_date', 'year', 'is_outdoor', 'is_derived']),
        ('results', ['id', 'competition_id', 'athlete_id', 'event_id', 'club_id', 'age_class_id', 'result', 'result_numeric', 'wind', 'placement', 'year', 'age', 'date', 'is_outdoor', 'is_approved', 'rejection_reason']),
    ]

    for table_name, columns in tables:
        filename = f"export/{table_name}.csv"
        cursor.execute(f"SELECT {','.join(columns)} FROM {table_name}")

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(cursor.fetchall())

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Exported {table_name}: {count:,} rows")

    conn.close()
    print(f"\nFiles exported to: export/")


# =====================================================
# MAIN
# =====================================================

def main():
    if len(sys.argv) < 2:
        print("Unified Athletics Statistics Scraper")
        print("=" * 50)
        print("\nUsage:")
        print("  python unified_scraper.py init              # Initialize database")
        print("  python unified_scraper.py phase1            # Scrape competitions (2011+)")
        print("  python unified_scraper.py phase2            # Scrape athletes (all years)")
        print("  python unified_scraper.py phase2 A B C      # Scrape specific letters")
        print("  python unified_scraper.py phase3            # Link & cleanup")
        print("  python unified_scraper.py status            # Show status")
        print("  python unified_scraper.py export            # Export to CSV")
        print("  python unified_scraper.py all               # Run all phases")
        return

    command = sys.argv[1].lower()

    if command == 'init':
        init_database()

    elif command == 'phase1':
        init_database()
        run_phase1()

    elif command == 'phase2':
        init_database()
        letters = [l.upper() for l in sys.argv[2:]] if len(sys.argv) > 2 else None
        run_phase2(letters)

    elif command == 'phase3':
        run_phase3()

    elif command == 'status':
        show_status()

    elif command == 'export':
        export_to_csv()

    elif command == 'all':
        init_database()
        run_phase1()
        run_phase2()
        run_phase3()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
