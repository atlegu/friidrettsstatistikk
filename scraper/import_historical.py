"""
Import historical athlete data to Supabase.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from tqdm import tqdm

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
DATA_DIR = Path(__file__).parent / "data"

# ============================================================
# EVENT NAME MAPPING - Extended for historical data
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
    '80 meter': '80m',

    # Middle/Long distance
    '800 meter': '800m',
    '1000 meter': '1000m',
    '1500 meter': '1500m',
    '2000 meter': '2000m',
    '3000 meter': '3000m',
    '5000 meter': '5000m',
    '10000 meter': '10000m',
    '20000 meter': '20000m',
    '1 engelsk mil': '1mile',
    '1 mile': '1mile',
    'Maraton': 'maraton',
    'Halvmaraton': 'halvmaraton',

    # Road races
    '3 km': '3km',
    '5 km': '5km',
    '10 km': '10km',
    '15 km': '15km',
    '20 km': '20km',
    '25 km': '25km',
    '30 km': '30km',
    '100 km': '100km',

    # Hurdles - all variants
    '40 meter hekk': '40mh',
    '40 meter hekk (76,2cm)': '40mh_76_2cm',
    '40 meter hekk (91,4cm)': '40mh_91_4cm',
    '50 meter hekk': '50mh',
    '50 meter hekk (76,2cm)': '50mh_76_2cm',
    '50 meter hekk (84,0cm)': '50mh_84cm',
    '60 meter hekk': '60mh',
    '60 meter hekk (60cm)': '60mh_60cm',
    '60 meter hekk (68,0cm)': '60mh_68cm', '60 meter hekk (68cm)': '60mh_68cm',
    '60 meter hekk (76,2cm)': '60mh_76_2cm',
    '60 meter hekk (84,0cm)': '60mh_84cm', '60 meter hekk (84cm)': '60mh_84cm',
    '60 meter hekk (91,4cm)': '60mh_91_4cm',
    '60 meter hekk (100cm)': '60mh_100cm',
    '60 meter hekk (106,7cm)': '60mh_106_7cm', '60 meter hekk (106,7 cm)': '60mh_106_7cm',
    '80 meter hekk': '80mh',
    '80 meter hekk (68,0cm)': '80mh_68cm', '80 meter hekk (68cm)': '80mh_68cm',
    '80 meter hekk (76,2cm)': '80mh_76_2cm',
    '80 meter hekk (84,0cm)': '80mh_84cm', '80 meter hekk (84,0cm/8,5m)': '80mh_84cm', '80 meter hekk (84cm)': '80mh_84cm',
    '80 meter hekk (91,4cm)': '80mh_91_4cm',
    '100 meter hekk': '100mh',
    '100 meter hekk (84,0cm)': '100mh_84cm', '100 meter hekk (84cm)': '100mh_84cm',
    '100 meter hekk (91,4cm)': '100mh_91_4cm',
    '110 meter hekk': '110mh',
    '110 meter hekk (91,4cm)': '110mh_91_4cm',
    '110 meter hekk (100cm)': '110mh_100cm',
    '110 meter hekk (106,7cm)': '110mh_106_7cm',
    '200 meter hekk': '200mh',
    '200 meter hekk (68,0cm)': '200mh_68cm', '200 meter hekk (68cm)': '200mh_68cm',
    '200 meter hekk (76,2cm)': '200mh_76_2cm',
    '300 meter hekk': '300mh',
    '300 meter hekk (68,0cm)': '300mh_68cm', '300 meter hekk (68cm)': '300mh_68cm',
    '300 meter hekk (76,2cm)': '300mh_76_2cm',
    '300 meter hekk (84,0cm)': '300mh_84cm', '300 meter hekk (84cm)': '300mh_84cm',
    '300 meter hekk (91,4cm)': '300mh_91_4cm', '300 meter hekk (91,4cm-8hk)': '300mh_91_4cm',
    '400 meter hekk': '400mh',
    '400 meter hekk (76,2cm)': '400mh_76_2cm',
    '400 meter hekk (84,0cm)': '400mh_84cm', '400 meter hekk (84cm)': '400mh_84cm',
    '400 meter hekk (91,4cm)': '400mh_91_4cm',

    # Steeplechase
    '1500 meter hinder': '1500mhinder',
    '1500 meter hinder (76,2cm)': '1500mhinder_76_2cm',
    '2000 meter hinder': '2000mhinder',
    '2000 meter hinder (76,2cm)': '2000mhinder_76_2cm',
    '2000 meter hinder (84,0cm)': '2000mhinder_84cm', '2000 meter hinder (84cm)': '2000mhinder_84cm',
    '2000 meter hinder (91,4cm)': '2000mhinder_91_4cm',
    '3000 meter hinder': '3000mhinder',
    '3000 meter hinder (76,2cm)': '3000mhinder_76_2cm',
    '3000 meter hinder (84,0cm)': '3000mhinder_84cm', '3000 meter hinder (84cm)': '3000mhinder_84cm',
    '3000 meter hinder (91,4cm)': '3000mhinder_91_4cm',

    # Jumps
    'Høyde': 'hoyde',
    'Stav': 'stav',
    'Lengde': 'lengde',
    'Tresteg': 'tresteg',
    'Lengde uten tilløp': 'lengde_ut',
    'Høyde uten tilløp': 'hoyde_ut',
    'Tresteg uten tilløp': 'tresteg_ut',

    # Throws - all weight variants
    'Kule': 'kule',
    'Kule 7,26kg': 'kule_7_26kg',
    'Kule 6,0kg': 'kule_6kg',
    'Kule 5,0kg': 'kule_5kg',
    'Kule 4,0kg': 'kule_4kg',
    'Kule 3,0kg': 'kule_3kg',
    'Kule 2,0kg': 'kule_2kg',
    'Diskos': 'diskos',
    'Diskos 2,0kg': 'diskos_2kg',
    'Diskos 1,75kg': 'diskos_1_75kg',
    'Diskos 1,5kg': 'diskos_1_5kg',
    'Diskos 1,0kg': 'diskos_1kg',
    'Diskos 0,75kg': 'diskos_750g',
    'Diskos 750gram': 'diskos_750g',
    'Diskos 600gram': 'diskos_600g',
    'Slegge': 'slegge',
    'Slegge 7,26kg/121,5cm': 'slegge_7_26kg',
    'Slegge 6,0kg/121,5cm': 'slegge_6kg',
    'Slegge 5,0kg/120cm': 'slegge_5kg',
    'Slegge 4,0kg/120cm': 'slegge_4kg',
    'Slegge 3,0kg/120cm': 'slegge_3kg',
    'Slegge 2,0kg/110cm': 'slegge_2kg',
    'Spyd': 'spyd',
    'Spyd 800gram': 'spyd_800g',
    'Spyd 700gram': 'spyd_700g',
    'Spyd 600gram': 'spyd_600g',
    'Spyd 500gram': 'spyd_500g',
    'Spyd 400gram': 'spyd_400g',
    'Vektkast': 'vektkast',
    'Liten ball': 'liten_ball',

    # Combined events
    'Femkamp': '5kamp',
    'Sjukamp': '7kamp',
    'Tikamp': '10kamp',
    '5-kamp': '5kamp',
    '7-kamp': '7kamp',
    '10-kamp': '10kamp',

    # Race walking
    'Kappgang 3000 meter': '3000mg',
    'Kappgang 5000 meter': '5000mg',
    'Kappgang 10000 meter': '10000mg',
    'Kappgang 20 km': '20kmg',
    '3000 meter gange': '3000mg',
    '5000 meter gange': '5000mg',
    '10000 meter gange': '10000mg',
    '20 km gange': '20kmg',

    # Relays
    '4 x 100 meter': '4x100m',
    '4 x 200 meter': '4x200m',
    '4 x 400 meter': '4x400m',
    '4x100 meter': '4x100m',
    '4x200 meter': '4x200m',
    '4x400 meter': '4x400m',
}

# Cache for lookups
_event_cache = {}
_club_cache = {}
_athlete_cache = {}
_meet_cache = {}
_season_cache = {}


def load_seasons():
    """Load all seasons from database into cache."""
    global _season_cache
    response = supabase.table('seasons').select('id, year, name').execute()
    # Map by year and type (indoor/outdoor based on name)
    for s in response.data:
        is_indoor = 'innendørs' in s['name'].lower()
        key = f"{s['year']}_{'indoor' if is_indoor else 'outdoor'}"
        _season_cache[key] = s['id']
    logger.info(f"Loaded {len(response.data)} seasons")


def get_season_id(year, indoor=False):
    """Get season ID from year and indoor flag."""
    if not year:
        return None
    key = f"{year}_{'indoor' if indoor else 'outdoor'}"
    return _season_cache.get(key)


def load_events():
    """Load all events from database into cache."""
    global _event_cache
    response = supabase.table('events').select('id, code, name').execute()
    _event_cache = {e['name']: e['id'] for e in response.data}
    _event_cache.update({e['code']: e['id'] for e in response.data})
    logger.info(f"Loaded {len(response.data)} events")


def get_event_id(event_name):
    """Get event ID from name, using mapping and cache."""
    if not event_name:
        return None

    # Try direct match first
    if event_name in _event_cache:
        return _event_cache[event_name]

    # Try mapped code
    code = EVENT_NAME_TO_CODE.get(event_name)
    if code and code in _event_cache:
        return _event_cache[code]

    # Not found
    return None


def get_or_create_club(name):
    """Get or create a club, return its ID."""
    if not name:
        return None

    if name in _club_cache:
        return _club_cache[name]

    # Check if exists
    response = supabase.table('clubs').select('id').eq('name', name).execute()
    if response.data:
        _club_cache[name] = response.data[0]['id']
        return _club_cache[name]

    # Create new
    try:
        response = supabase.table('clubs').insert({'name': name}).execute()
        if response.data:
            _club_cache[name] = response.data[0]['id']
            return _club_cache[name]
    except Exception as e:
        logger.warning(f"Failed to create club {name}: {e}")

    return None


def parse_name(full_name):
    """Parse full name into first and last name."""
    if not full_name:
        return '', ''

    name_parts = full_name.strip().split()
    if not name_parts:
        return '', ''

    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    return first_name, last_name


def extract_birth_year(birth_date):
    """Extract birth year from birth date string."""
    if not birth_date:
        return None
    try:
        return int(birth_date.split('-')[0])
    except:
        return None


def get_or_create_athlete(external_id, name, birth_date, gender, club_name):
    """Get or create an athlete, return their ID."""
    cache_key = f"hist_{external_id}" if external_id else f"{name}_{birth_date}"

    if cache_key in _athlete_cache:
        return _athlete_cache[cache_key]

    first_name, last_name = parse_name(name)
    birth_year = extract_birth_year(birth_date)
    club_id = get_or_create_club(club_name) if club_name else None

    # Check if exists by external_id
    if external_id:
        response = supabase.table('athletes').select('id').eq('external_id', str(external_id)).execute()
        if response.data:
            _athlete_cache[cache_key] = response.data[0]['id']
            return _athlete_cache[cache_key]

    # Check if exists by name and birth_date
    if name and birth_date:
        response = supabase.table('athletes').select('id').eq('first_name', first_name).eq('last_name', last_name).eq('birth_date', birth_date).execute()
        if response.data:
            _athlete_cache[cache_key] = response.data[0]['id']
            return _athlete_cache[cache_key]

    # Create new - Note: full_name is a generated column, don't include it
    athlete_data = {
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'birth_date': birth_date,
        'birth_year': birth_year,
        'current_club_id': club_id,
    }
    if external_id:
        athlete_data['external_id'] = str(external_id)

    try:
        response = supabase.table('athletes').insert(athlete_data).execute()
        if response.data:
            _athlete_cache[cache_key] = response.data[0]['id']
            return _athlete_cache[cache_key]
    except Exception as e:
        logger.warning(f"Failed to create athlete {name}: {e}")

    return None


def get_or_create_meet(name, date, city, indoor):
    """Get or create a meet, return its ID."""
    if not name or not date:
        return None

    cache_key = f"{name}_{date}_{city}"

    if cache_key in _meet_cache:
        return _meet_cache[cache_key]

    # Check if exists
    response = supabase.table('meets').select('id').eq('name', name).eq('start_date', date).execute()
    if response.data:
        _meet_cache[cache_key] = response.data[0]['id']
        return _meet_cache[cache_key]

    # Create new - city is required, default to 'Ukjent' if not provided
    meet_data = {
        'name': name,
        'start_date': date,
        'city': city or 'Ukjent',
        'indoor': indoor,
        'country': 'NOR',
    }

    try:
        response = supabase.table('meets').insert(meet_data).execute()
        if response.data:
            _meet_cache[cache_key] = response.data[0]['id']
            return _meet_cache[cache_key]
    except Exception as e:
        logger.warning(f"Failed to create meet {name}: {e}")

    return None


def normalize_performance(performance_str):
    """Normalize performance string to database-expected format.

    Converts M.SS.hh format to M:SS.hh format for the database trigger.
    Also cleans up suffixes.
    """
    if not performance_str:
        return None

    # Clean up the string
    perf = performance_str.strip()

    # Remove common suffixes and annotations
    # Examples: "26.5(ok)", "10.25m", "13.24.6mx", "10.25(wind)"
    perf = re.sub(r'\([^)]*\)$', '', perf)  # Remove trailing parenthetical like (ok), (wind)
    perf = re.sub(r'[mxwhia*]+$', '', perf, flags=re.IGNORECASE)  # Remove letter suffixes

    # Convert M.SS.hh or MM.SS.hh to M:SS.hh format
    # Match patterns like 2.21.52 or 14.12.5
    match = re.match(r'^(\d+)\.(\d{2})\.(\d+)$', perf)
    if match:
        minutes, seconds, tenths_or_hundredths = match.groups()
        # Keep single-digit as tenths (5 = 0.5s), don't convert to hundredths
        return f"{minutes}:{seconds}.{tenths_or_hundredths}"

    # Also handle H.MM.SS format (for marathon etc)
    match = re.match(r'^(\d+)\.(\d{2})\.(\d{2})$', perf)
    if match:
        hours, minutes, seconds = match.groups()
        # Check if it's actually hours (value > 60 for first part suggests minutes)
        if int(hours) < 60 and int(minutes) < 60:
            return f"{hours}:{minutes}:{seconds}"

    # Already correct format or simple format (like 10.25)
    return perf


def parse_performance(performance_str):
    """Parse and normalize performance string.

    Returns (normalized_performance, None) - the database trigger calculates the value.
    """
    if not performance_str:
        return None, None

    normalized = normalize_performance(performance_str)
    return normalized, None  # Let database trigger calculate performance_value


def import_historical_results():
    """Import historical results from JSON file to Supabase."""
    results_file = DATA_DIR / 'historical_athletes_results.json'

    if not results_file.exists():
        logger.error(f"Results file not found: {results_file}")
        return

    # Load data
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    logger.info(f"Loaded {len(results)} historical results")

    # Load reference data
    load_events()
    load_seasons()

    # Track statistics
    stats = {
        'total': len(results),
        'imported': 0,
        'skipped_no_event': 0,
        'skipped_no_athlete': 0,
        'skipped_no_meet': 0,
        'skipped_no_season': 0,
        'skipped_invalid': 0,
        'errors': 0,
    }

    # Collect unique events that don't have mapping
    unmapped_events = set()

    # Process in batches
    batch_size = 100
    result_batch = []

    for result in tqdm(results, desc="Importing historical results"):
        try:
            # Skip invalid results
            if not result.get('valid', True):
                stats['skipped_invalid'] += 1
                continue

            # Get event ID
            event_name = result.get('event_name', '')
            event_id = get_event_id(event_name)
            if not event_id:
                unmapped_events.add(event_name)
                stats['skipped_no_event'] += 1
                continue

            # Get athlete ID
            athlete_id = get_or_create_athlete(
                external_id=result.get('athlete_id'),
                name=result.get('name'),
                birth_date=result.get('birth_date'),
                gender=result.get('gender'),
                club_name=result.get('club')
            )
            if not athlete_id:
                stats['skipped_no_athlete'] += 1
                continue

            # Get meet ID
            indoor = result.get('indoor', False)
            meet_id = get_or_create_meet(
                name=result.get('meet_name', ''),
                date=result.get('date'),
                city=result.get('city', ''),
                indoor=indoor
            )
            if not meet_id:
                stats['skipped_no_meet'] += 1
                continue

            # Get club ID for result
            club_id = get_or_create_club(result.get('club'))

            # Parse performance
            raw_perf = result.get('performance')
            performance, performance_value = parse_performance(raw_perf)

            # Performance is required - use raw string if parsing failed
            if not performance and raw_perf:
                performance = str(raw_perf)
            if not performance:
                stats['skipped_invalid'] += 1
                continue

            # Get season ID
            season_year = result.get('season')
            season_id = get_season_id(season_year, indoor)
            if not season_id:
                stats['skipped_no_season'] += 1
                continue

            # Clean and validate wind value
            wind = result.get('wind')
            if wind is not None:
                try:
                    wind = float(wind)
                except (ValueError, TypeError):
                    wind = None

            # Build result record - using correct column names
            # Note: performance_value is calculated by database trigger
            result_data = {
                'athlete_id': athlete_id,
                'event_id': event_id,
                'meet_id': meet_id,
                'season_id': season_id,
                'club_id': club_id,
                'performance': str(performance) if performance else None,
                'date': result.get('date'),
                'wind': wind,
                'place': result.get('place'),
                'status': 'OK',
            }

            result_batch.append(result_data)

            # Insert batch
            if len(result_batch) >= batch_size:
                try:
                    supabase.table('results').insert(result_batch).execute()
                    stats['imported'] += len(result_batch)
                except Exception as e:
                    logger.error(f"Batch insert failed: {e}")
                    stats['errors'] += len(result_batch)
                result_batch = []

        except Exception as e:
            logger.warning(f"Error processing result: {e}")
            stats['errors'] += 1

    # Insert remaining batch
    if result_batch:
        try:
            supabase.table('results').insert(result_batch).execute()
            stats['imported'] += len(result_batch)
        except Exception as e:
            logger.error(f"Final batch insert failed: {e}")
            stats['errors'] += len(result_batch)

    # Log statistics
    logger.info(f"""
    Import completed!
    - Total: {stats['total']}
    - Imported: {stats['imported']}
    - Skipped (no event mapping): {stats['skipped_no_event']}
    - Skipped (no athlete): {stats['skipped_no_athlete']}
    - Skipped (no meet): {stats['skipped_no_meet']}
    - Skipped (no season): {stats['skipped_no_season']}
    - Skipped (invalid): {stats['skipped_invalid']}
    - Errors: {stats['errors']}
    """)

    if unmapped_events:
        logger.warning(f"Unmapped events ({len(unmapped_events)}): {sorted(unmapped_events)[:20]}...")

    return stats


def main():
    """Main import function."""
    logger.info("Starting historical data import...")
    import_historical_results()
    logger.info("Import complete!")


if __name__ == '__main__':
    main()
