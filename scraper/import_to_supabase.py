"""
Import scraped data to Supabase.
"""

import json
import os
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
# Prefer service key for admin access, fall back to anon key
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_ANON_KEY) must be set in .env file")

if not os.getenv('SUPABASE_SERVICE_KEY'):
    logger.warning("Using anon key - may fail due to RLS policies. Set SUPABASE_SERVICE_KEY for admin access.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Data directory
DATA_DIR = Path(__file__).parent / "data"

# ============================================================
# EVENT NAME MAPPING
# Maps scraped event names to database event codes
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
    '1 engelsk mil': '1mile',

    # Hurdles - need to handle different heights
    '60 meter hekk': '60mh',
    '100 meter hekk': '100mh',
    '110 meter hekk (106,7cm)': '110mh',
    '110 meter hekk (100cm)': '110mh',
    '110 meter hekk (91,4cm)': '110mh',
    '400 meter hekk (91,4cm)': '400mh',
    '400 meter hekk (76,2cm)': '400mh',
    '200 meter hekk (76,2cm)': '200mh',
    '300 meter hekk (76,2cm)': '300mh',
    '300 meter hekk (84,0cm)': '300mh',

    # Steeplechase
    '3000 meter hinder (91,4cm)': '3000mhinder',
    '2000 meter hinder (91,4cm)': '2000mhinder',
    '1500 meter hinder (76,2cm)': '1500mhinder',

    # Jumps
    'Høyde': 'hoyde',
    'Stav': 'stav',
    'Lengde': 'lengde',
    'Tresteg': 'tresteg',

    # Throws - need to handle different weights
    'Kule 7,26kg': 'kule',
    'Kule 6,0kg': 'kule',
    'Kule 5,0kg': 'kule',
    'Kule 4,0kg': 'kule',
    'Kule 3,0kg': 'kule',
    'Diskos 2,0kg': 'diskos',
    'Diskos 1,75kg': 'diskos',
    'Diskos 1,5kg': 'diskos',
    'Diskos 1,0kg': 'diskos',
    'Diskos 0,75kg': 'diskos',
    'Slegge 7,26kg/121,5cm': 'slegge',
    'Slegge 6,0kg/121,5cm': 'slegge',
    'Slegge 5,0kg/120cm': 'slegge',
    'Slegge 4,0kg/120cm': 'slegge',
    'Slegge 3,0kg/120cm': 'slegge',
    'Spyd 800gram': 'spyd',
    'Spyd 700gram': 'spyd',
    'Spyd 600gram': 'spyd',
    'Spyd 500gram': 'spyd',
    'Spyd 400gram': 'spyd',

    # Combined events
    'Femkamp': '5kamp',
    'Sjukamp': '7kamp',
    'Tikamp': '10kamp',

    # Race walking
    'Kappgang 3000 meter': '3000mg',
    'Kappgang 5000 meter': '5000mg',
    'Kappgang 10000 meter': '10000mg',
    'Kappgang 20 km': '20kmg',

    # Standing jumps (indoor)
    'Lengde uten tilløp': 'lengde_ut',
    'Høyde uten tilløp': 'hoyde_ut',
    'Tresteg uten tilløp': 'tresteg_ut',
}

# Cache for lookups
_event_cache = {}
_club_cache = {}
_athlete_cache = {}
_meet_cache = {}
_season_cache = {}


def load_events():
    """Load all events from database into cache."""
    global _event_cache
    response = supabase.table('events').select('id, code, name').execute()
    _event_cache = {e['name']: e['id'] for e in response.data}
    _event_cache.update({e['code']: e['id'] for e in response.data})
    logger.info(f"Loaded {len(response.data)} events")


def load_seasons():
    """Load all seasons from database into cache."""
    global _season_cache
    response = supabase.table('seasons').select('id, year, indoor').execute()
    for s in response.data:
        key = (s['year'], s['indoor'])
        _season_cache[key] = s['id']
    logger.info(f"Loaded {len(response.data)} seasons")


def get_event_id(event_name):
    """Get event ID from name, using mapping and cache."""
    # Try direct match first
    if event_name in _event_cache:
        return _event_cache[event_name]

    # Try mapped code
    code = EVENT_NAME_TO_CODE.get(event_name)
    if code and code in _event_cache:
        return _event_cache[code]

    # Not found
    return None


def get_season_id(year, indoor):
    """Get season ID from year and indoor flag."""
    key = (year, indoor)
    return _season_cache.get(key)


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
    response = supabase.table('clubs').insert({'name': name}).execute()
    if response.data:
        _club_cache[name] = response.data[0]['id']
        return _club_cache[name]

    return None


def get_or_create_athlete(external_id, name, birth_date, gender, club_name):
    """Get or create an athlete, return their ID."""
    cache_key = external_id or f"{name}_{birth_date}"

    if cache_key in _athlete_cache:
        return _athlete_cache[cache_key]

    # Parse name
    name_parts = name.split() if name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    # Get club ID
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

    # Create new
    athlete_data = {
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'birth_date': birth_date,
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
    cache_key = f"{name}_{date}_{city}"

    if cache_key in _meet_cache:
        return _meet_cache[cache_key]

    # Check if exists
    response = supabase.table('meets').select('id').eq('name', name).eq('start_date', date).execute()
    if response.data:
        _meet_cache[cache_key] = response.data[0]['id']
        return _meet_cache[cache_key]

    # Create new
    meet_data = {
        'name': name,
        'start_date': date,
        'city': city,
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


def parse_round(round_str):
    """Convert round string to enum value."""
    round_map = {
        'heat': 'heat',
        'final': 'final',
        'semi': 'semi',
        'qualification': 'qualification',
    }
    return round_map.get(round_str)


def import_results(results_file):
    """Import results from JSON file to Supabase."""
    # Load data
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    logger.info(f"Loaded {len(results)} results from {results_file}")

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
        'errors': 0,
    }

    # Collect unique events that don't have mapping
    unmapped_events = set()

    # Process in batches
    batch_size = 100
    result_batch = []

    for result in tqdm(results, desc="Importing results"):
        try:
            # Get event ID
            event_id = get_event_id(result.get('event_name', ''))
            if not event_id:
                unmapped_events.add(result.get('event_name', 'Unknown'))
                stats['skipped_no_event'] += 1
                continue

            # Get season ID
            year = result.get('season', 2025)
            indoor = result.get('indoor', False)
            season_id = get_season_id(year, indoor)

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

            # Build result record
            result_data = {
                'athlete_id': athlete_id,
                'event_id': event_id,
                'meet_id': meet_id,
                'season_id': season_id,
                'performance': result.get('performance'),
                'date': result.get('date'),
                'wind': result.get('wind'),
                'place': result.get('place'),
                'round': parse_round(result.get('round')),
                'heat_number': result.get('heat'),
                'club_id': club_id,
                'verified': True,  # Scraped from official source
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
    - Errors: {stats['errors']}
    """)

    if unmapped_events:
        logger.warning(f"Unmapped events: {sorted(unmapped_events)}")

    return stats


def main():
    """Main import function."""
    results_file = DATA_DIR / 'results_raw.json'

    if not results_file.exists():
        logger.error(f"Results file not found: {results_file}")
        logger.info("Run scraper_v2.py first to generate data.")
        return

    import_results(results_file)


if __name__ == '__main__':
    main()
