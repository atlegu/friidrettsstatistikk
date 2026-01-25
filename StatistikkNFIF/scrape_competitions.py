"""
Competition-based scraper for Norwegian Athletics Statistics.

This scraper:
1. Discovers competition IDs from LandsStatistikk.php rankings
2. Scrapes full competition results from StevneResultater.php
3. Stores properly linked data with real competition IDs

Usage:
    python scrape_competitions.py discover          # Find all competition IDs
    python scrape_competitions.py scrape            # Scrape all discovered competitions
    python scrape_competitions.py scrape 10006050   # Scrape specific competition
    python scrape_competitions.py status            # Show progress
"""

import requests
import sqlite3
import re
import sys
import time
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, List, Set, Tuple
import logging

# Configuration
DB_PATH = "athletics_stats.db"
DELAY_BETWEEN_REQUESTS = 0.3
MAX_RETRIES = 3

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('competition_scrape.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =====================================================
# DATABASE SETUP
# =====================================================

def init_database():
    """Initialize database with competition-focused schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        -- Competitions table with source system IDs
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY,          -- Original competition ID from source
            name TEXT NOT NULL,
            venue TEXT,
            organizer TEXT,
            start_date TEXT,                 -- YYYY-MM-DD
            end_date TEXT,                   -- YYYY-MM-DD
            year INTEGER,
            is_outdoor INTEGER DEFAULT 1,
            scraped_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Athletes table
        CREATE TABLE IF NOT EXISTS athletes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,               -- ID from source if known
            name TEXT NOT NULL,
            birth_year INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(name, birth_year)
        );

        -- Clubs table
        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Events table
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Age classes table
        CREATE TABLE IF NOT EXISTS age_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Results table
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id INTEGER NOT NULL REFERENCES competitions(id),
            athlete_id INTEGER NOT NULL REFERENCES athletes(id),
            event_id INTEGER NOT NULL REFERENCES events(id),
            club_id INTEGER REFERENCES clubs(id),
            age_class_id INTEGER REFERENCES age_classes(id),
            result TEXT NOT NULL,
            result_numeric REAL,
            wind TEXT,
            placement TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(competition_id, athlete_id, event_id, result)
        );

        -- Competition discovery tracking
        CREATE TABLE IF NOT EXISTS discovered_competitions (
            competition_id INTEGER PRIMARY KEY,
            discovered_at TEXT DEFAULT (datetime('now')),
            scraped INTEGER DEFAULT 0,
            scraped_at TEXT
        );

        -- Discovery progress tracking
        CREATE TABLE IF NOT EXISTS discovery_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            showclass INTEGER,
            showevent INTEGER,
            showseason INTEGER,
            outdoor TEXT,
            competitions_found INTEGER DEFAULT 0,
            discovered_at TEXT DEFAULT (datetime('now'))
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_results_competition ON results(competition_id);
        CREATE INDEX IF NOT EXISTS idx_results_athlete ON results(athlete_id);
        CREATE INDEX IF NOT EXISTS idx_results_event ON results(event_id);
        CREATE INDEX IF NOT EXISTS idx_competitions_year ON competitions(year);
        CREATE INDEX IF NOT EXISTS idx_athletes_name ON athletes(name);
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized")


# =====================================================
# COMPETITION ID DISCOVERY
# =====================================================

def fetch_rankings_page(showclass: int, showevent: int, showseason: int, outdoor: str) -> str:
    """Fetch a rankings page from LandsStatistikk.php"""
    url = "https://www.minfriidrettsstatistikk.info/php/LandsStatistikk.php"
    params = {
        'showclass': showclass,
        'showevent': showevent,
        'showseason': showseason,
        'outdoor': outdoor,
        'showclub': 0
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
            else:
                raise
    return ""


def extract_competition_ids(html: str) -> Set[int]:
    """Extract competition IDs from rankings page HTML"""
    # Find all posttoresultlist(XXXXXX) calls
    pattern = r'posttoresultlist\((\d+)\)'
    matches = re.findall(pattern, html)
    return set(int(m) for m in matches)


def get_event_class_ranges():
    """
    Return ranges for events and classes to iterate through.
    These were discovered from the website's dropdown menus.
    """
    # Event IDs (discovered from the website)
    # This is a subset - expand as needed
    events = [
        2,   # 60m
        4,   # 100m
        6,   # 200m
        8,   # 400m
        10,  # 800m
        12,  # 1500m
        14,  # 3000m
        16,  # 5000m
        18,  # 10000m
        68,  # Høyde (High jump)
        70,  # Stav (Pole vault)
        72,  # Lengde (Long jump)
        74,  # Tresteg (Triple jump)
        76,  # Kule (Shot put)
        78,  # Diskos (Discus)
        80,  # Slegge (Hammer)
        82,  # Spyd (Javelin)
    ]

    # Class IDs (age/gender categories)
    # 1-10: Youth boys, 11: Men Senior, 12-21: Youth girls, 22: Women Senior, etc.
    classes = list(range(1, 50))  # Cover main classes

    # Years to scrape
    current_year = datetime.now().year
    years = list(range(1960, current_year + 1))

    return events, classes, years


def discover_all_competition_ids():
    """
    Iterate through all event/class/year combinations to discover competition IDs.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    events, classes, years = get_event_class_ranges()

    total_combinations = len(events) * len(classes) * len(years) * 2  # *2 for outdoor/indoor
    logger.info(f"Scanning {total_combinations:,} combinations for competition IDs...")

    all_competition_ids = set()
    processed = 0

    for outdoor in ['Y', 'N']:
        for year in reversed(years):  # Start with recent years
            for event in events:
                for cls in classes:
                    # Check if already processed
                    cursor.execute("""
                        SELECT 1 FROM discovery_progress
                        WHERE showclass=? AND showevent=? AND showseason=? AND outdoor=?
                    """, (cls, event, year, outdoor))

                    if cursor.fetchone():
                        processed += 1
                        continue

                    try:
                        html = fetch_rankings_page(cls, event, year, outdoor)
                        comp_ids = extract_competition_ids(html)

                        # Store discovered IDs
                        for comp_id in comp_ids:
                            cursor.execute("""
                                INSERT OR IGNORE INTO discovered_competitions (competition_id)
                                VALUES (?)
                            """, (comp_id,))
                            all_competition_ids.add(comp_id)

                        # Mark as processed
                        cursor.execute("""
                            INSERT INTO discovery_progress (showclass, showevent, showseason, outdoor, competitions_found)
                            VALUES (?, ?, ?, ?, ?)
                        """, (cls, event, year, outdoor, len(comp_ids)))

                        conn.commit()
                        processed += 1

                        if processed % 100 == 0:
                            logger.info(f"Progress: {processed}/{total_combinations} - Found {len(all_competition_ids)} unique competitions")

                        time.sleep(DELAY_BETWEEN_REQUESTS)

                    except Exception as e:
                        logger.error(f"Error fetching class={cls} event={event} year={year}: {e}")
                        continue

    conn.close()
    logger.info(f"Discovery complete. Found {len(all_competition_ids)} unique competition IDs")
    return all_competition_ids


def quick_discover(years: List[int] = None, events: List[int] = None):
    """Quick discovery for specific years/events only"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if years is None:
        years = list(range(2020, datetime.now().year + 1))

    if events is None:
        # Main events only
        events = [4, 6, 8, 10, 12, 68, 70, 72, 76, 82]  # 100m, 200m, 400m, 800m, 1500m, HJ, PV, LJ, SP, JT

    classes = [11, 22]  # Senior men and women only for quick scan

    all_comp_ids = set()

    for outdoor in ['Y', 'N']:
        for year in years:
            for event in events:
                for cls in classes:
                    try:
                        html = fetch_rankings_page(cls, event, year, outdoor)
                        comp_ids = extract_competition_ids(html)

                        for comp_id in comp_ids:
                            cursor.execute("""
                                INSERT OR IGNORE INTO discovered_competitions (competition_id)
                                VALUES (?)
                            """, (comp_id,))
                            all_comp_ids.add(comp_id)

                        time.sleep(DELAY_BETWEEN_REQUESTS)

                    except Exception as e:
                        logger.error(f"Error: {e}")

    conn.commit()
    conn.close()

    logger.info(f"Quick discovery found {len(all_comp_ids)} competitions")
    return all_comp_ids


# =====================================================
# COMPETITION SCRAPING
# =====================================================

def fetch_competition_results(competition_id: int) -> str:
    """Fetch full results for a competition"""
    url = "https://www.minfriidrettsstatistikk.info/php/StevneResultater.php"

    data = {"competition": competition_id}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, data=data, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
            else:
                raise
    return ""


def parse_date_range(date_str: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse date range like '27.06.2025 til 29.06.2025' or single date '27.06.2025'"""
    if not date_str:
        return None, None

    # Check for range
    if ' til ' in date_str:
        parts = date_str.split(' til ')
        start = parse_single_date(parts[0].strip())
        end = parse_single_date(parts[1].strip())
        return start, end
    else:
        d = parse_single_date(date_str.strip())
        return d, d


def parse_single_date(date_str: str) -> Optional[str]:
    """Parse DD.MM.YYYY to YYYY-MM-DD"""
    try:
        parts = date_str.split('.')
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str]]:
    """Parse result and wind from '14,12(+2,0)'"""
    if not result_str:
        return '', None

    result_str = result_str.strip()
    match = re.match(r'(.+?)\(([+-]?\d+[,.]?\d*)\)\s*$', result_str)
    if match:
        return match.group(1).strip(), match.group(2)

    return result_str, None


def parse_athlete_name_year(name_str: str) -> Tuple[str, Optional[int]]:
    """Parse 'Athlete Name(1990)' format"""
    if not name_str:
        return '', None

    match = re.match(r'(.+?)\((\d{4})\)$', name_str.strip())
    if match:
        return match.group(1).strip(), int(match.group(2))

    # Handle (0000) for unknown birth year
    match = re.match(r'(.+?)\(0+\)$', name_str.strip())
    if match:
        return match.group(1).strip(), None

    return name_str.strip(), None


def parse_competition_page(html: str, competition_id: int) -> Dict:
    """Parse competition results page"""
    soup = BeautifulSoup(html, 'html.parser')

    data = {
        'competition_id': competition_id,
        'name': None,
        'venue': None,
        'organizer': None,
        'start_date': None,
        'end_date': None,
        'results': []
    }

    # Extract header info
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
                        data['name'] = value
                    elif 'DATO' in label:
                        data['start_date'], data['end_date'] = parse_date_range(value)
                    elif 'STED' in label:
                        data['venue'] = value
                    elif 'ARRANGØR' in label:
                        data['organizer'] = value

    if not data['name']:
        return data

    # Extract year
    if data['start_date']:
        data['year'] = int(data['start_date'][:4])

    # Parse results
    current_class = None
    current_event = None

    for element in soup.find_all(['div', 'table']):
        # Age class header
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                current_class = h2.get_text(strip=True)

        # Event header
        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)

        # Results table
        elif element.name == 'table' and current_event:
            rows = element.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if not cells or len(cells) < 4:
                    continue

                placement = cells[0].get_text(strip=True)
                result_raw = cells[1].get_text(strip=True)
                result, wind = parse_result_wind(result_raw)

                name_raw = cells[2].get_text(strip=True)
                athlete_name, birth_year = parse_athlete_name_year(name_raw)

                club = cells[3].get_text(strip=True) if len(cells) > 3 else None

                if athlete_name and result:
                    data['results'].append({
                        'age_class': current_class,
                        'event': current_event,
                        'placement': placement,
                        'result': result,
                        'wind': wind,
                        'athlete_name': athlete_name,
                        'birth_year': birth_year,
                        'club': club
                    })

    return data


def get_or_create_id(cursor, table: str, name_col: str, name: str, extra_cols: Dict = None) -> int:
    """Get or create a record and return its ID"""
    if not name:
        return None

    cursor.execute(f"SELECT id FROM {table} WHERE {name_col} = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]

    if extra_cols:
        cols = [name_col] + list(extra_cols.keys())
        vals = [name] + list(extra_cols.values())
        placeholders = ','.join(['?' for _ in vals])
        cursor.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})", vals)
    else:
        cursor.execute(f"INSERT INTO {table} ({name_col}) VALUES (?)", (name,))

    return cursor.lastrowid


def scrape_competition(competition_id: int):
    """Scrape and store a single competition"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if already scraped
    cursor.execute("SELECT scraped FROM discovered_competitions WHERE competition_id = ?", (competition_id,))
    row = cursor.fetchone()
    if row and row['scraped']:
        logger.info(f"Competition {competition_id} already scraped, skipping")
        conn.close()
        return

    try:
        html = fetch_competition_results(competition_id)
        data = parse_competition_page(html, competition_id)

        if not data['name']:
            logger.warning(f"Competition {competition_id}: No data found")
            conn.close()
            return

        # Insert competition
        cursor.execute("""
            INSERT OR REPLACE INTO competitions
            (id, name, venue, organizer, start_date, end_date, year, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            competition_id,
            data['name'],
            data['venue'],
            data['organizer'],
            data['start_date'],
            data['end_date'],
            data.get('year')
        ))

        # Insert results
        results_added = 0
        for r in data['results']:
            # Get/create athlete
            cursor.execute(
                "SELECT id FROM athletes WHERE name = ? AND (birth_year = ? OR (birth_year IS NULL AND ? IS NULL))",
                (r['athlete_name'], r['birth_year'], r['birth_year'])
            )
            athlete_row = cursor.fetchone()
            if athlete_row:
                athlete_id = athlete_row[0]
            else:
                cursor.execute(
                    "INSERT INTO athletes (name, birth_year) VALUES (?, ?)",
                    (r['athlete_name'], r['birth_year'])
                )
                athlete_id = cursor.lastrowid

            event_id = get_or_create_id(cursor, 'events', 'name', r['event'])
            club_id = get_or_create_id(cursor, 'clubs', 'name', r['club'])
            class_id = get_or_create_id(cursor, 'age_classes', 'name', r['age_class'])

            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO results
                    (competition_id, athlete_id, event_id, club_id, age_class_id, result, wind, placement)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    competition_id, athlete_id, event_id, club_id, class_id,
                    r['result'], r['wind'], r['placement']
                ))
                results_added += 1
            except sqlite3.IntegrityError:
                pass

        # Mark as scraped
        cursor.execute("""
            UPDATE discovered_competitions
            SET scraped = 1, scraped_at = datetime('now')
            WHERE competition_id = ?
        """, (competition_id,))

        conn.commit()
        logger.info(f"Competition {competition_id}: {data['name']} - {results_added} results")

    except Exception as e:
        logger.error(f"Error scraping competition {competition_id}: {e}")

    conn.close()


def scrape_all_competitions():
    """Scrape all discovered competitions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT competition_id FROM discovered_competitions
        WHERE scraped = 0
        ORDER BY competition_id DESC
    """)

    comp_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    logger.info(f"Scraping {len(comp_ids)} competitions...")

    for i, comp_id in enumerate(comp_ids):
        scrape_competition(comp_id)

        if (i + 1) % 50 == 0:
            logger.info(f"Progress: {i + 1}/{len(comp_ids)}")

        time.sleep(DELAY_BETWEEN_REQUESTS)


def show_status():
    """Show scraping status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("COMPETITION SCRAPING STATUS")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM discovered_competitions")
    discovered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM discovered_competitions WHERE scraped = 1")
    scraped = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM competitions")
    competitions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results")
    results = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM athletes")
    athletes = cursor.fetchone()[0]

    print(f"\nDiscovered competitions: {discovered:,}")
    print(f"Scraped competitions: {scraped:,}")
    print(f"Stored competitions: {competitions:,}")
    print(f"Total results: {results:,}")
    print(f"Total athletes: {athletes:,}")

    if discovered > 0:
        print(f"\nProgress: {100*scraped/discovered:.1f}%")

    # Recent competitions
    print("\n" + "-" * 60)
    print("RECENT COMPETITIONS:")
    cursor.execute("""
        SELECT id, name, start_date, venue,
               (SELECT COUNT(*) FROM results WHERE competition_id = c.id) as result_count
        FROM competitions c
        ORDER BY start_date DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[2]} | {row[1][:40]:<40} | {row[4]} results")

    conn.close()
    print("=" * 60)


# =====================================================
# MAIN
# =====================================================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scrape_competitions.py init              # Initialize database")
        print("  python scrape_competitions.py discover          # Discover all competition IDs")
        print("  python scrape_competitions.py quick-discover    # Quick discover (recent years)")
        print("  python scrape_competitions.py scrape            # Scrape all competitions")
        print("  python scrape_competitions.py scrape <ID>       # Scrape specific competition")
        print("  python scrape_competitions.py status            # Show status")
        return

    command = sys.argv[1].lower()

    if command == 'init':
        init_database()

    elif command == 'discover':
        init_database()
        discover_all_competition_ids()

    elif command == 'quick-discover':
        init_database()
        quick_discover()

    elif command == 'scrape':
        if len(sys.argv) > 2:
            scrape_competition(int(sys.argv[2]))
        else:
            scrape_all_competitions()

    elif command == 'status':
        show_status()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
