"""
Comprehensive Athletics Statistics Scraper
Scrapes all athlete data and inserts directly into SQLite database.

Usage:
    python comprehensive_scraper.py init          # Initialize database
    python comprehensive_scraper.py scrape A      # Scrape letter A
    python comprehensive_scraper.py scrape A 0 100  # Scrape first 100 of A
    python comprehensive_scraper.py status        # Show progress
    python comprehensive_scraper.py verify        # Verify data integrity
"""

import requests
import json
import os
import re
import sys
import time
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Tuple, Any
import logging
from contextlib import contextmanager

# Configuration
DB_PATH = "athletics_stats.db"
SEARCH_HTML_DIR = "athlete_search_html"
DELAY_BETWEEN_REQUESTS = 0.2  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_scrape.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =====================================================
# DATABASE MANAGEMENT
# =====================================================

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize the database with schema"""
    with get_db_connection() as conn:
        with open('improved_schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
    logger.info(f"Database initialized: {DB_PATH}")


# =====================================================
# CACHING / LOOKUP HELPERS
# =====================================================

class LookupCache:
    """In-memory cache for normalized tables to avoid repeated queries"""

    def __init__(self, conn):
        self.conn = conn
        self.clubs = {}      # name -> id
        self.events = {}     # name -> id
        self.venues = {}     # name -> id
        self.competitions = {}  # (name, date, venue_id) -> id
        self._load_existing()

    def _load_existing(self):
        """Load existing data into cache"""
        cursor = self.conn.cursor()

        for row in cursor.execute("SELECT id, name FROM clubs"):
            self.clubs[row['name']] = row['id']

        for row in cursor.execute("SELECT id, name FROM events"):
            self.events[row['name']] = row['id']

        for row in cursor.execute("SELECT id, name FROM venues"):
            self.venues[row['name']] = row['id']

        for row in cursor.execute("SELECT id, name, date, venue_id FROM competitions"):
            key = (row['name'], row['date'], row['venue_id'])
            self.competitions[key] = row['id']

        logger.info(f"Loaded cache: {len(self.clubs)} clubs, {len(self.events)} events, "
                   f"{len(self.venues)} venues, {len(self.competitions)} competitions")

    def get_or_create_club(self, name: str) -> Optional[int]:
        """Get or create a club, return its ID"""
        if not name or name.strip() == '':
            return None
        name = name.strip()

        if name in self.clubs:
            return self.clubs[name]

        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO clubs (name) VALUES (?)", (name,))
        self.conn.commit()

        cursor.execute("SELECT id FROM clubs WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            self.clubs[name] = row['id']
            return row['id']
        return None

    def get_or_create_event(self, name: str) -> Optional[int]:
        """Get or create an event, return its ID"""
        if not name or name.strip() == '':
            return None
        name = name.strip()

        if name in self.events:
            return self.events[name]

        # Categorize the event
        category = categorize_event(name)
        is_timed = category in ('sprint', 'middle_distance', 'long_distance', 'hurdles', 'walk', 'relay')
        higher_is_better = not is_timed

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO events (name, category, is_timed, higher_is_better)
            VALUES (?, ?, ?, ?)
        """, (name, category, is_timed, higher_is_better))
        self.conn.commit()

        cursor.execute("SELECT id FROM events WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            self.events[name] = row['id']
            return row['id']
        return None

    def get_or_create_venue(self, name: str) -> Optional[int]:
        """Get or create a venue, return its ID"""
        if not name or name.strip() == '':
            return None
        name = name.strip()

        if name in self.venues:
            return self.venues[name]

        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO venues (name) VALUES (?)", (name,))
        self.conn.commit()

        cursor.execute("SELECT id FROM venues WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            self.venues[name] = row['id']
            return row['id']
        return None

    def get_or_create_competition(self, name: str, date: str, venue_id: Optional[int]) -> Optional[int]:
        """Get or create a competition, return its ID"""
        if not name or name.strip() == '':
            return None
        name = name.strip()

        key = (name, date, venue_id)
        if key in self.competitions:
            return self.competitions[key]

        # Extract year from date
        year = None
        if date:
            try:
                year = int(date.split('-')[0])
            except:
                pass

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO competitions (name, date, venue_id, year)
            VALUES (?, ?, ?, ?)
        """, (name, date, venue_id, year))
        self.conn.commit()

        cursor.execute("""
            SELECT id FROM competitions
            WHERE name = ? AND (date = ? OR (date IS NULL AND ? IS NULL))
            AND (venue_id = ? OR (venue_id IS NULL AND ? IS NULL))
        """, (name, date, date, venue_id, venue_id))
        row = cursor.fetchone()
        if row:
            self.competitions[key] = row['id']
            return row['id']
        return None


def categorize_event(event_name: str) -> str:
    """Categorize an event based on its name"""
    name_lower = event_name.lower()

    # Combined events
    if any(x in name_lower for x in ['tikamp', 'sjukamp', 'femkamp', 'mangekamp', 'decathlon', 'heptathlon']):
        return 'combined'

    # Relays
    if any(x in name_lower for x in ['stafett', 'relay', '4x', '4 x']):
        return 'relay'

    # Hurdles
    if any(x in name_lower for x in ['hekk', 'hinder', 'hurdle']):
        return 'hurdles'

    # Throws
    if any(x in name_lower for x in ['kule', 'diskos', 'spyd', 'slegge', 'shot', 'discus', 'javelin', 'hammer', 'vektkast']):
        return 'throws'

    # Jumps
    if any(x in name_lower for x in ['høyde', 'stav', 'lengde', 'tresteg', 'high', 'pole', 'long', 'triple']):
        return 'jumps'

    # Walk
    if any(x in name_lower for x in ['kappgang', 'gang', 'walk']):
        return 'walk'

    # Distance based categorization for running
    # Extract distance if possible
    meters = extract_meters(event_name)
    if meters:
        if meters <= 400:
            return 'sprint'
        elif meters <= 1500:
            return 'middle_distance'
        else:
            return 'long_distance'

    # Default categories based on common patterns
    if 'km' in name_lower or 'maraton' in name_lower or 'marathon' in name_lower:
        return 'long_distance'
    if 'mil' in name_lower:
        return 'long_distance'

    return 'other'


def extract_meters(event_name: str) -> Optional[int]:
    """Extract distance in meters from event name"""
    name = event_name.lower()

    # Handle "X meter" format
    match = re.search(r'(\d+)\s*meter', name)
    if match:
        return int(match.group(1))

    # Handle "X m" format
    match = re.search(r'(\d+)\s*m\b', name)
    if match:
        return int(match.group(1))

    # Handle km
    match = re.search(r'(\d+(?:,\d+)?)\s*km', name)
    if match:
        km = float(match.group(1).replace(',', '.'))
        return int(km * 1000)

    return None


# =====================================================
# RESULT PARSING
# =====================================================

def parse_result_to_numeric(result: str, event_name: str) -> Optional[float]:
    """
    Convert result string to numeric value for sorting.
    For timed events: returns seconds (lower is better)
    For field events: returns meters/points (higher is better)
    """
    if not result:
        return None

    result = result.strip()

    # Remove wind info if present (shouldn't be, but just in case)
    result = re.sub(r'\([^)]*\)$', '', result).strip()

    # Check if it's a combined event (points - just a number)
    if re.match(r'^\d{3,5}$', result):
        return float(result)

    # Check if it's a field event (single decimal number)
    if re.match(r'^\d+,\d{1,2}$', result):
        return float(result.replace(',', '.'))

    # Check if it's a time format: mm,ss,cc or m,ss,cc or ss,cc
    parts = result.split(',')

    if len(parts) == 3:
        # mm,ss,cc format (or m,ss,cc)
        try:
            minutes = int(parts[0])
            seconds = int(parts[1])
            hundredths = int(parts[2]) if len(parts[2]) == 2 else int(parts[2]) * 10
            return minutes * 60 + seconds + hundredths / 100
        except:
            pass

    elif len(parts) == 2:
        # Could be ss,cc (time) or m,cm (distance)
        # Guess based on event type
        category = categorize_event(event_name)
        if category in ('sprint', 'middle_distance', 'long_distance', 'hurdles', 'walk', 'relay'):
            # It's a time: ss,cc
            try:
                seconds = int(parts[0])
                hundredths = int(parts[1]) if len(parts[1]) == 2 else int(parts[1]) * 10
                return seconds + hundredths / 100
            except:
                pass
        else:
            # It's a distance: m,cm
            try:
                return float(result.replace(',', '.'))
            except:
                pass

    elif len(parts) == 1:
        # Single number - could be seconds or meters
        try:
            return float(result.replace(',', '.'))
        except:
            pass

    return None


def parse_date(date_str: str) -> Optional[str]:
    """Parse date from DD.MM.YY format to YYYY-MM-DD"""
    if not date_str:
        return None
    try:
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            day, month, year = parts
            year = int(year)
            if year > 50:
                year = 1900 + year
            else:
                year = 2000 + year
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None


def parse_birth_date(birth_str: str) -> Optional[str]:
    """Parse birth date from 'Født: DD.MM.YYYY' format"""
    if not birth_str:
        return None
    try:
        match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', birth_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"
    except:
        pass
    return None


def parse_year_age(year_age_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse year and age from '2015 (14)' format"""
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


def parse_result_wind(result_str: str) -> Tuple[str, Optional[str]]:
    """Parse result and wind from formats like '9,17(+0,9)'"""
    if not result_str:
        return '', None

    result_str = result_str.strip()
    # Match result followed by wind in parentheses
    match = re.match(r'(.+?)\(([+-]?\d+[,.]?\d*)\)$', result_str)
    if match:
        return match.group(1).strip(), match.group(2)

    return result_str, None


# =====================================================
# HTML FETCHING AND PARSING
# =====================================================

def fetch_athlete_results(athlete_id: int) -> str:
    """Fetch ALL results for an athlete with retry logic"""
    url = "https://www.minfriidrettsstatistikk.info/php/UtoverStatistikk.php"

    data = {
        "athlete": athlete_id,
        "type": "RES"
    }

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
                logger.warning(f"Retry {attempt + 1} for athlete {athlete_id}: {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise

    return ""


def parse_athlete_page(html: str, athlete_id: int) -> Dict:
    """Parse athlete page HTML and extract all data"""
    soup = BeautifulSoup(html, 'html.parser')

    data = {
        'athlete_id': athlete_id,
        'name': None,
        'birth_date': None,
        'results': []
    }

    # Extract athlete name
    athlete_div = soup.find('div', id='athlete')
    if athlete_div:
        name_tag = athlete_div.find('h2')
        if name_tag:
            data['name'] = name_tag.get_text(strip=True)

        birth_tag = athlete_div.find('h3')
        if birth_tag:
            data['birth_date'] = parse_birth_date(birth_tag.get_text())

    if not data['name']:
        return data

    # Track current context
    current_section = None  # 'outdoor' or 'indoor'
    current_event = None
    is_approved_section = True

    # Process all elements
    for element in soup.find_all(['div', 'table', 'h4']):
        if element.name == 'div' and element.get('id') == 'header2':
            h2 = element.find('h2')
            if h2:
                text = h2.get_text(strip=True)
                if 'UTENDØRS' in text:
                    current_section = 'outdoor'
                elif 'INNENDØRS' in text:
                    current_section = 'indoor'

        elif element.name == 'div' and element.get('id') == 'eventheader':
            h3 = element.find('h3')
            if h3:
                current_event = h3.get_text(strip=True)
                is_approved_section = True  # Reset for new event

        elif element.name == 'h4':
            text = element.get_text(strip=True)
            if 'Ikke godkjente' in text:
                is_approved_section = False

        elif element.name == 'table' and current_event and current_section:
            rows = element.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if not cells or len(cells) < 6:
                    continue

                year, age = parse_year_age(cells[0].get_text())
                result_raw = cells[1].get_text(strip=True)
                result, wind = parse_result_wind(result_raw)
                placement = cells[2].get_text(strip=True)
                club = cells[3].get_text(strip=True)
                date_str = cells[4].get_text(strip=True)
                date = parse_date(date_str)

                # Location cell has venue in title attribute, competition name in text
                location_cell = cells[5]
                venue = location_cell.get('title', '').strip()
                competition_name = location_cell.get_text(strip=True)

                # Handle rejection reason for non-approved results
                rejection_reason = None
                if len(cells) >= 7 and not is_approved_section:
                    rejection_reason = cells[6].get_text(strip=True)

                result_data = {
                    'event': current_event,
                    'is_outdoor': current_section == 'outdoor',
                    'year': year,
                    'age': age,
                    'result': result,
                    'wind': wind,
                    'placement': placement,
                    'club': club,
                    'date': date,
                    'venue': venue,
                    'competition': competition_name,
                    'is_approved': is_approved_section,
                    'rejection_reason': rejection_reason
                }

                data['results'].append(result_data)

    return data


# =====================================================
# ATHLETE LIST LOADING
# =====================================================

def get_athletes_for_letter(letter: str) -> List[Tuple[int, str]]:
    """Get all athlete IDs and names for a given letter from the search HTML"""
    search_file = os.path.join(SEARCH_HTML_DIR, f"search_{letter}.html")

    if not os.path.exists(search_file):
        raise FileNotFoundError(f"Search file not found: {search_file}")

    with open(search_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract athlete IDs and names
    pattern = r'showathl=(\d+)[^>]*>([^<]+)'
    matches = re.findall(pattern, html)

    return [(int(aid), name.strip()) for aid, name in matches]


# =====================================================
# MAIN SCRAPING LOGIC
# =====================================================

def scrape_athlete(conn, cache: LookupCache, athlete_id: int, athlete_name: str) -> Dict:
    """Scrape and store a single athlete's data"""
    result = {
        'status': 'unknown',
        'results_count': 0,
        'message': ''
    }

    try:
        html = fetch_athlete_results(athlete_id)
        data = parse_athlete_page(html, athlete_id)

        if not data['name']:
            result['status'] = 'empty'
            result['message'] = 'No athlete data found'
            return result

        cursor = conn.cursor()

        # Insert/update athlete
        cursor.execute("""
            INSERT OR REPLACE INTO athletes (id, name, birth_date, updated_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (athlete_id, data['name'], data['birth_date']))

        # Insert results
        for r in data['results']:
            event_id = cache.get_or_create_event(r['event'])
            club_id = cache.get_or_create_club(r['club'])
            venue_id = cache.get_or_create_venue(r['venue']) if r['venue'] else None
            competition_id = cache.get_or_create_competition(r['competition'], r['date'], venue_id)

            # Calculate numeric result for sorting
            result_numeric = parse_result_to_numeric(r['result'], r['event'])

            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO results (
                        athlete_id, event_id, club_id, competition_id,
                        result, result_numeric, wind,
                        year, age, date, placement,
                        is_outdoor, is_approved, rejection_reason,
                        source_athlete_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    athlete_id, event_id, club_id, competition_id,
                    r['result'], result_numeric, r['wind'],
                    r['year'], r['age'], r['date'], r['placement'],
                    1 if r['is_outdoor'] else 0,
                    1 if r['is_approved'] else 0,
                    r['rejection_reason'],
                    athlete_id
                ))
            except sqlite3.IntegrityError:
                # Duplicate result, skip
                pass

        conn.commit()

        result['status'] = 'success'
        result['results_count'] = len(data['results'])
        result['message'] = f"{data['name']} - {len(data['results'])} results"

    except Exception as e:
        result['status'] = 'error'
        result['message'] = str(e)
        logger.error(f"Error processing athlete {athlete_id}: {e}")

    return result


def scrape_letter(letter: str, start_idx: int = None, end_idx: int = None):
    """Scrape all athletes for a given letter"""
    logger.info(f"{'=' * 60}")
    logger.info(f"SCRAPING LETTER: {letter}")
    logger.info(f"{'=' * 60}")

    # Get athletes for this letter
    athletes = get_athletes_for_letter(letter)
    total = len(athletes)
    logger.info(f"Found {total} athletes for letter {letter}")

    with get_db_connection() as conn:
        cache = LookupCache(conn)
        cursor = conn.cursor()

        # Check for existing progress
        cursor.execute("SELECT * FROM scrape_progress WHERE letter = ?", (letter,))
        progress = cursor.fetchone()

        if progress and start_idx is None:
            start_idx = progress['last_athlete_index']
            logger.info(f"Resuming from index {start_idx}")

        if start_idx is None:
            start_idx = 0
        if end_idx is None:
            end_idx = total

        end_idx = min(end_idx, total)

        # Initialize/update progress record
        cursor.execute("""
            INSERT OR REPLACE INTO scrape_progress (letter, total_athletes, processed_count, last_athlete_index, started_at, updated_at)
            VALUES (?, ?, ?, ?, COALESCE((SELECT started_at FROM scrape_progress WHERE letter = ?), datetime('now')), datetime('now'))
        """, (letter, total, start_idx, start_idx, letter))
        conn.commit()

        # Process athletes
        success_count = 0
        error_count = 0
        total_results = 0

        for i in range(start_idx, end_idx):
            athlete_id, athlete_name = athletes[i]

            result = scrape_athlete(conn, cache, athlete_id, athlete_name)

            # Log result
            cursor.execute("""
                INSERT INTO scrape_log (athlete_id, status, message, results_count)
                VALUES (?, ?, ?, ?)
            """, (athlete_id, result['status'], result['message'], result['results_count']))

            if result['status'] == 'success':
                success_count += 1
                total_results += result['results_count']
            elif result['status'] == 'error':
                error_count += 1

            # Progress update
            if (i + 1) % 50 == 0 or i == end_idx - 1:
                progress_pct = ((i - start_idx + 1) / (end_idx - start_idx)) * 100
                logger.info(f"Progress: {i + 1}/{end_idx} ({progress_pct:.1f}%) - Last: {result['message'][:50]}")

                # Update progress record
                cursor.execute("""
                    UPDATE scrape_progress
                    SET processed_count = ?, last_athlete_index = ?, last_athlete_id = ?, updated_at = datetime('now')
                    WHERE letter = ?
                """, (i + 1, i + 1, athlete_id, letter))
                conn.commit()

            time.sleep(DELAY_BETWEEN_REQUESTS)

        # Mark as completed if we processed everything
        if end_idx >= total:
            cursor.execute("""
                UPDATE scrape_progress
                SET completed_at = datetime('now')
                WHERE letter = ?
            """, (letter,))
            conn.commit()

        logger.info(f"\n{'=' * 60}")
        logger.info(f"LETTER {letter} COMPLETE!")
        logger.info(f"Athletes processed: {success_count}")
        logger.info(f"Total results: {total_results}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"{'=' * 60}")


def show_status():
    """Show scraping status for all letters"""
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ")

    print("\n" + "=" * 70)
    print("SCRAPING STATUS")
    print("=" * 70)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Overall stats
        cursor.execute("SELECT COUNT(*) FROM athletes")
        athlete_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM results")
        result_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM competitions")
        comp_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clubs")
        club_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM venues")
        venue_count = cursor.fetchone()[0]

        print(f"\nTotal athletes: {athlete_count:,}")
        print(f"Total results: {result_count:,}")
        print(f"Total competitions: {comp_count:,}")
        print(f"Total events: {event_count:,}")
        print(f"Total clubs: {club_count:,}")
        print(f"Total venues: {venue_count:,}")

        print("\n" + "-" * 70)
        print(f"{'Letter':<8} {'Progress':<20} {'Results':<12} {'Status'}")
        print("-" * 70)

        for letter in letters:
            cursor.execute("SELECT * FROM scrape_progress WHERE letter = ?", (letter,))
            progress = cursor.fetchone()

            # Count results for athletes starting with this letter
            cursor.execute("""
                SELECT COUNT(*) FROM results r
                JOIN athletes a ON r.athlete_id = a.id
                WHERE a.name LIKE ?
            """, (f"{letter}%",))
            letter_results = cursor.fetchone()[0]

            if progress:
                prog_str = f"{progress['processed_count']}/{progress['total_athletes']}"
                if progress['completed_at']:
                    status = "Complete"
                else:
                    status = "In progress"
            else:
                # Check if we have search file
                search_file = os.path.join(SEARCH_HTML_DIR, f"search_{letter}.html")
                if os.path.exists(search_file):
                    prog_str = "Not started"
                    status = "Ready"
                else:
                    prog_str = "-"
                    status = "No data"

            print(f"{letter:<8} {prog_str:<20} {letter_results:<12,} {status}")

    print("=" * 70)


def verify_data():
    """Verify data integrity"""
    print("\n" + "=" * 70)
    print("DATA VERIFICATION")
    print("=" * 70)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check for orphaned results
        cursor.execute("""
            SELECT COUNT(*) FROM results r
            LEFT JOIN athletes a ON r.athlete_id = a.id
            WHERE a.id IS NULL
        """)
        orphaned_results = cursor.fetchone()[0]
        print(f"Orphaned results (no athlete): {orphaned_results}")

        # Check for results with null events
        cursor.execute("SELECT COUNT(*) FROM results WHERE event_id IS NULL")
        null_events = cursor.fetchone()[0]
        print(f"Results with null event_id: {null_events}")

        # Check for athletes with no results
        cursor.execute("""
            SELECT COUNT(*) FROM athletes a
            LEFT JOIN results r ON a.id = r.athlete_id
            WHERE r.id IS NULL
        """)
        athletes_no_results = cursor.fetchone()[0]
        print(f"Athletes with no results: {athletes_no_results}")

        # Results by year distribution
        print("\nResults by year (last 10 years):")
        cursor.execute("""
            SELECT year, COUNT(*) as count
            FROM results
            WHERE year >= 2015
            GROUP BY year
            ORDER BY year DESC
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"  {row['year']}: {row['count']:,}")

        # Top events by result count
        print("\nTop 10 events by result count:")
        cursor.execute("""
            SELECT e.name, COUNT(*) as count
            FROM results r
            JOIN events e ON r.event_id = e.id
            GROUP BY e.id
            ORDER BY count DESC
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"  {row['name']}: {row['count']:,}")

    print("=" * 70)


# =====================================================
# MAIN ENTRY POINT
# =====================================================

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python comprehensive_scraper.py init              # Initialize database")
        print("  python comprehensive_scraper.py scrape <LETTER>   # Scrape letter")
        print("  python comprehensive_scraper.py scrape <LETTER> <START> <END>")
        print("  python comprehensive_scraper.py status            # Show progress")
        print("  python comprehensive_scraper.py verify            # Verify data")
        print()
        print("Examples:")
        print("  python comprehensive_scraper.py init")
        print("  python comprehensive_scraper.py scrape A")
        print("  python comprehensive_scraper.py scrape S 0 5000")
        print("  python comprehensive_scraper.py status")
        return

    command = sys.argv[1].lower()

    if command == 'init':
        init_database()
        print("Database initialized successfully!")

    elif command == 'scrape':
        if len(sys.argv) < 3:
            print("Please specify a letter to scrape")
            return

        letter = sys.argv[2].upper()
        valid_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ")
        if letter not in valid_letters:
            print(f"Invalid letter: {letter}")
            print(f"Valid letters: {' '.join(valid_letters)}")
            return

        start_idx = int(sys.argv[3]) if len(sys.argv) > 3 else None
        end_idx = int(sys.argv[4]) if len(sys.argv) > 4 else None

        scrape_letter(letter, start_idx, end_idx)

    elif command == 'status':
        show_status()

    elif command == 'verify':
        verify_data()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
