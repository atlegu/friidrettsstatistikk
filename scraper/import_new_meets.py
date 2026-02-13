"""
Import scraped meet results from CSV into Supabase database.
Reads the CSV output from scrape_new_meets.py and:
1. Creates meets if they don't exist
2. Matches athletes by name + birth_year
3. Maps events to event IDs
4. Inserts results
"""

import csv
import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Data directory
DATA_DIR = Path(__file__).parent / "new_meets_data"

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

# Events we intentionally skip (para, wheelchair, combined events with non-standard format)
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

# Combined events (need special mapping)
COMBINED_EVENT_PATTERNS = {
    r'4 Kamp': '4kamp',
    r'5 Kamp': '5kamp',
    r'7 Kamp': '7kamp',
}

# ============================================================
# Caches
# ============================================================
_event_cache = {}      # event_code -> event_id
_club_cache = {}       # club_name -> club_id
_athlete_cache = {}    # (name, birth_year, gender) -> athlete_id
_meet_cache = {}       # (name, date) -> meet_id
_season_cache = {}     # (year, indoor) -> season_id


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
    # Paginate to get all clubs (Supabase default limit is 1000)
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
    """Load athletes for fast matching. Only load name+birth_year+gender+id."""
    global _athlete_cache
    # Supabase REST API limits to 1000 rows per request, so paginate properly
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
    Only converts when there are exactly 2 dots and the format looks like m.ss.hh
    """
    if not result_str:
        return result_str

    # Match patterns like 1.59.39 or 16.08.70 (m.ss.hh or mm.ss.hh)
    match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{1,2})$', result_str)
    if match:
        minutes, seconds, hundredths = match.groups()
        return f"{minutes}:{seconds}.{hundredths}"

    return result_str


def get_event_id(event_name):
    """Get event ID from scraped event name."""
    if event_name in SKIP_EVENTS:
        return None

    # Check combined events
    for pattern, code in COMBINED_EVENT_PATTERNS.items():
        if event_name.startswith(pattern):
            return _event_cache.get(code)

    # Try mapped code
    code = EVENT_NAME_TO_CODE.get(event_name)
    if code:
        return _event_cache.get(code)

    # Try direct match
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
    # Indoor season: if date is in Dec, it belongs to next year's indoor season
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

    # Create new club
    try:
        response = supabase.table('clubs').insert({'name': name}).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
    except Exception as e:
        # Might already exist from concurrent insert
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

    # Check if exists
    response = supabase.table('meets').select('id').eq(
        'name', name
    ).eq('start_date', date).execute()

    if response.data:
        _meet_cache[cache_key] = response.data[0]['id']
        return _meet_cache[cache_key]

    # Also check with city prefix (existing data might have "Oslo, Bislett Games")
    if location:
        city_name = f"{location}, {name}"
        response = supabase.table('meets').select('id').eq(
            'name', city_name
        ).eq('start_date', date).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            return _meet_cache[cache_key]

    # Determine season
    year = int(date[:4])
    if indoor and int(date[5:7]) >= 10:
        year += 1
    season_id = _season_cache.get((year, indoor))

    # Parse city from location (e.g., "Metz/FRA" -> "Metz", "Oslo" -> "Oslo")
    city = location.split('/')[0] if location else ''

    # Determine country
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

    # Create new meet
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

    # Try without gender (some athletes might have NULL gender)
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


def parse_performance_value(result_str, event_name):
    """Convert performance string to sortable integer value.
    - Time events: hundredths of a second (6.82 -> 682, 1:52.33 -> 11233)
    - Distance/height: millimeters (5.84 -> 5840, 15.23 -> 15230)
    - Points: raw points value
    """
    if not result_str:
        return None

    result_str = result_str.strip()

    # Determine result type from event name
    distance_events = {'Høyde', 'Stav', 'Lengde', 'Tresteg', 'Høyde uten tilløp',
                       'Lengde uten tilløp', 'Tresteg uten tilløp',
                       'Lengde (Sone 0,5m)', 'Tresteg (Sone 0,5m)'}
    throw_events = {'Kule', 'Diskos', 'Slegge', 'Spyd', 'VektKast'}
    combined_events = {'Kamp'}

    is_distance = event_name in distance_events or any(
        event_name.startswith(t) for t in throw_events
    )
    is_combined = any(k in event_name for k in combined_events)

    if is_combined:
        # Points - just parse the number
        try:
            return int(result_str)
        except ValueError:
            return None

    if is_distance:
        # Distance in mm (e.g., "5.84" -> 5840)
        try:
            return int(float(result_str) * 1000)
        except ValueError:
            return None

    # Time event
    try:
        # Handle mm:ss.hh format
        if ':' in result_str:
            parts = result_str.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return int((minutes * 60 + seconds) * 100)
            elif len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return int((hours * 3600 + minutes * 60 + seconds) * 100)
        else:
            # Plain seconds
            return int(float(result_str) * 100)
    except ValueError:
        return None


def load_meets_metadata():
    """Load meet metadata from missing_meets.json for location info."""
    import json
    meets_file = DATA_DIR / 'missing_meets.json'
    if meets_file.exists():
        with open(meets_file, 'r') as f:
            meets = json.load(f)
        return {m['external_id']: m for m in meets}
    return {}


def import_csv(csv_file):
    """Import results from CSV file to Supabase."""
    # Load reference data
    logger.info("Loading reference data...")
    load_events()
    load_seasons()
    load_clubs()
    load_athletes()

    # Load meet metadata for location info
    meets_metadata = load_meets_metadata()

    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info(f"Read {len(rows)} rows from {csv_file}")

    # Track statistics
    stats = {
        'total': len(rows),
        'imported': 0,
        'matched_existing_athlete': 0,
        'created_new_athlete': 0,
        'skipped_no_event': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'skipped_duplicate': 0,
        'errors': 0,
    }
    unmapped_events = defaultdict(int)

    # Group rows by meet for efficient processing
    meets_rows = defaultdict(list)
    for row in rows:
        meet_key = (row['meet_name'], row['meet_date'])
        meets_rows[meet_key].append(row)

    logger.info(f"Processing {len(meets_rows)} meets...")

    for (meet_name, meet_date), meet_rows in meets_rows.items():
        # Get meet metadata
        external_id = int(meet_rows[0].get('meet_external_id', 0))
        meta = meets_metadata.get(external_id, {})
        location = meta.get('location', '')
        is_indoor = meet_rows[0].get('is_indoor', 'True') == 'True'

        # Get or create meet
        meet_id = get_or_create_meet(meet_name, meet_date, location, is_indoor)
        if not meet_id:
            stats['skipped_no_meet'] += len(meet_rows)
            continue

        # Get season
        season_id = get_season_id(meet_date, is_indoor)

        # Build batch of results for this meet
        result_batch = []

        for row in meet_rows:
            event_name = row['event']
            event_class = row['event_class']

            # Get event ID
            event_id = get_event_id(event_name)
            if not event_id:
                if event_name not in SKIP_EVENTS:
                    unmapped_events[event_name] += 1
                stats['skipped_no_event'] += 1
                continue

            # Get gender
            gender = get_gender(event_class)

            # Parse birth year
            birth_year = int(row['birth_year']) if row.get('birth_year') else None

            # Match athlete
            athlete_name = row['athlete_name']
            athlete_id = match_athlete(athlete_name, birth_year, gender)

            if athlete_id:
                stats['matched_existing_athlete'] += 1
            else:
                # Create new athlete
                athlete_id = create_athlete(athlete_name, birth_year, gender, row.get('club'))
                if athlete_id:
                    stats['created_new_athlete'] += 1
                else:
                    stats['skipped_no_athlete'] += 1
                    continue

            # Get club ID
            club_id = get_or_create_club(row.get('club'))

            # Parse performance - fix European period-separated time format
            result_str = fix_performance_format(row['result'])
            performance_value = parse_performance_value(result_str, event_name)

            # Parse place
            place = int(row['place']) if row.get('place') and row['place'].isdigit() else None

            # Parse wind
            wind = None
            if row.get('wind'):
                try:
                    wind = float(row['wind'])
                except ValueError:
                    pass

            # Build result record
            # Build result record (performance_value computed by DB trigger)
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

            # Check wind legality for sprint/jump events
            if wind is not None and wind > 2.0:
                result_data['is_wind_legal'] = False

            result_batch.append(result_data)

        # Insert batch for this meet
        if result_batch:
            try:
                # Insert in chunks of 50 to reduce blast radius of errors
                for i in range(0, len(result_batch), 50):
                    chunk = result_batch[i:i+50]
                    supabase.table('results').insert(chunk).execute()
                    stats['imported'] += len(chunk)
                logger.info(f"  Imported {len(result_batch)} results for {meet_name} ({meet_date})")
            except Exception as e:
                # Try inserting one by one to salvage what we can
                logger.warning(f"  Batch failed for {meet_name}, trying one-by-one: {e}")
                for result_data in result_batch:
                    try:
                        supabase.table('results').insert(result_data).execute()
                        stats['imported'] += 1
                    except Exception as e2:
                        logger.debug(f"    Failed single: {result_data['performance']} - {e2}")
                        stats['errors'] += 1

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("IMPORT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total rows: {stats['total']}")
    logger.info(f"Imported: {stats['imported']}")
    logger.info(f"  Matched existing athletes: {stats['matched_existing_athlete']}")
    logger.info(f"  Created new athletes: {stats['created_new_athlete']}")
    logger.info(f"Skipped (no event mapping): {stats['skipped_no_event']}")
    logger.info(f"Skipped (no athlete): {stats['skipped_no_athlete']}")
    logger.info(f"Skipped (no meet): {stats['skipped_no_meet']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info("=" * 60)

    if unmapped_events:
        logger.warning(f"\nUnmapped events (not in SKIP_EVENTS):")
        for event, count in sorted(unmapped_events.items(), key=lambda x: -x[1]):
            logger.warning(f"  {event}: {count} results")


def main():
    # Find most recent CSV file
    csv_files = sorted(DATA_DIR.glob('new_results_*.csv'))
    if not csv_files:
        logger.error("No CSV files found in new_meets_data/")
        return

    csv_file = csv_files[-1]  # Most recent
    logger.info(f"Importing from: {csv_file}")

    # Allow specifying a specific file
    if len(sys.argv) > 1:
        csv_file = Path(sys.argv[1])
        if not csv_file.exists():
            logger.error(f"File not found: {csv_file}")
            return

    import_csv(csv_file)


if __name__ == '__main__':
    main()
