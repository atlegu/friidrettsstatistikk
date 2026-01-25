"""
Fix missing results by re-importing with improved meet name matching.
The original import failed because meet names in JSON don't have city prefix,
but database meets have "City, Meet Name" format.
"""

import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_DIR = Path(__file__).parent / "data"

# Event name mapping (same as fast_import.py)
EVENT_MAP = {
    '30 meter': '30m', '40 meter': '40m', '50 meter': '50m', '55 meter': '55m',
    '60 meter': '60m', '80 meter': '80m', '100 meter': '100m', '150 meter': '150m', '200 meter': '200m',
    '300 meter': '300m', '400 meter': '400m', '600 meter': '600m', '800 meter': '800m',
    '1000 meter': '1000m', '1500 meter': '1500m', '2000 meter': '2000m', '3000 meter': '3000m',
    '5000 meter': '5000m', '10000 meter': '10000m', '20000 meter': '20000m', '25000 meter': '25000m',
    '3 km': '3km', '5 km': '5km', '10 km': '10km', '1 mile': '1mile', '2 miles': '2miles',
    'Halvmaraton': 'halvmaraton', 'Maraton': 'maraton', '100 km': '100km',
    '30 meter hekk 84,0cm': '30mh_84cm', '30 meter hekk (84,0cm)': '30mh_84cm',
    '40 meter hekk': '40mh',
    '40 meter hekk (76,2cm)': '40mh_76_2cm', '40 meter hekk (84,0cm)': '40mh_84cm',
    '40 meter hekk (91,4cm)': '40mh_91_4cm', '40 meter hekk (100cm)': '40mh_100cm',
    '55 meter hekk (84,0cm)': '55mh_84cm', '55 meter hekk (84cm)': '55mh_84cm',
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
    '100 meter hekk (76,2cm)': '100mh_76_2cm',
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
    '400 meter hekk (68,0cm)': '400mh_68cm', '400 meter hekk (68cm)': '400mh_68cm',
    '400 meter hekk (76,2cm)': '400mh_76_2cm',
    '400 meter hekk (84,0cm)': '400mh_84cm', '400 meter hekk (84cm)': '400mh_84cm',
    '400 meter hekk (91,4cm)': '400mh_91_4cm',
    '1500 meter hinder': '1500mhinder',
    '1500 meter hinder (76,2cm)': '1500mhinder_76_2cm',
    '1500 meter hinder (91,4cm)': '1500mhinder_91_4cm',
    '2000 meter hinder': '2000mhinder',
    '2000 meter hinder (76,2cm)': '2000mhinder_76_2cm',
    '2000 meter hinder (84,0cm)': '2000mhinder_84cm', '2000 meter hinder (84cm)': '2000mhinder_84cm',
    '2000 meter hinder (91,4cm)': '2000mhinder_91_4cm',
    '3000 meter hinder': '3000mhinder',
    '3000 meter hinder (76,2cm)': '3000mhinder_76_2cm',
    '3000 meter hinder (84,0cm)': '3000mhinder_84cm', '3000 meter hinder (84cm)': '3000mhinder_84cm',
    '3000 meter hinder (91,4cm)': '3000mhinder_91_4cm',
    'Høyde': 'hoyde', 'Høyde uten tilløp': 'hoyde_ut',
    'Stav': 'stav',
    'Lengde': 'lengde', 'Lengde uten tilløp': 'lengde_ut',
    'Tresteg': 'tresteg', 'Tresteg uten tilløp': 'tresteg_ut',
    'Kule': 'kule',
    'Kule 1kg': 'kule_1kg', 'Kule 2kg': 'kule_2kg', 'Kule 3kg': 'kule_3kg',
    'Kule 4kg': 'kule_4kg', 'Kule 5kg': 'kule_5kg', 'Kule 6kg': 'kule_6kg',
    'Kule 7,26kg': 'kule_7_26kg',
    'Diskos': 'diskos',
    'Diskos 0,6kg': 'diskos_0_6kg', 'Diskos 0,75kg': 'diskos_0_75kg',
    'Diskos 1kg': 'diskos_1kg', 'Diskos 1,5kg': 'diskos_1_5kg',
    'Diskos 1,75kg': 'diskos_1_75kg', 'Diskos 2kg': 'diskos_2kg',
    'Slegge': 'slegge',
    'Slegge 2kg': 'slegge_2kg', 'Slegge 3kg': 'slegge_3kg',
    'Slegge 4kg': 'slegge_4kg', 'Slegge 5kg': 'slegge_5kg',
    'Slegge 6kg': 'slegge_6kg', 'Slegge 7,26kg': 'slegge_7_26kg',
    'Spyd': 'spyd',
    'Spyd 400g': 'spyd_400g', 'Spyd 500g': 'spyd_500g',
    'Spyd 600g': 'spyd_600g', 'Spyd 700g': 'spyd_700g',
    'Spyd 800g': 'spyd_800g',
    'Liten ball': 'litenball', 'Liten ball 150g': 'litenball_150g',
    'Vektkast': 'vektkast',
    'Vektkast 4kg': 'vektkast_4kg', 'Vektkast 7,26kg': 'vektkast_7_26kg',
    'Vektkast 9,08kg': 'vektkast_9_08kg', 'Vektkast 11,34kg': 'vektkast_11_34kg',
    'Vektkast 15,88kg': 'vektkast_15_88kg',
    'Tikamp': 'tikamp', 'Sjukamp': 'sjukamp', 'Femkamp': 'femkamp',
    'Tikamp U20': 'tikamp_u20', 'Sjukamp U20': 'sjukamp_u20',
    '4 x 100 meter': '4x100m', '4 x 200 meter': '4x200m', '4 x 400 meter': '4x400m',
    '4 x 800 meter': '4x800m', '4 x 1500 meter': '4x1500m',
    'Svensk stafett': 'svenskstafett', 'Olympisk stafett': 'olympiskstafett',
    '3000 meter gange': '3000mg', '5000 meter gange': '5000mg',
    '10000 meter gange': '10000mg', '20 km gange': '20kmg',
    '10 km terrengløp': '10km_terreng', 'Terrengløp kort': 'terreng_kort',
    'Terrengløp lang': 'terreng_lang',
}

LONG_DISTANCE_EVENTS = {
    '800m', '1000m', '1500m', '2000m', '3000m', '5000m', '10000m',
    '3000mhinder', '2000mhinder', '1500mhinder',
    '3000mg', '5000mg', '10000mg',
}


def clean_club_name(club):
    """Clean up club name."""
    if not club:
        return None
    club = str(club).strip()
    if club.lower() in ('ukjent', 'unknown', ''):
        return None
    return club


def validate_date(date_str):
    """Validate and clean date string."""
    if not date_str:
        return None
    date_str = str(date_str).strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    return None


def clean_performance(perf, event_code=None):
    """Clean performance value."""
    if perf is None:
        return None
    perf_str = str(perf).strip()
    if perf_str.endswith('(ok)'):
        perf_str = perf_str[:-4].strip()
    # Remove trailing + (e.g., "4.14+" means clearance with no failures)
    if perf_str.endswith('+'):
        perf_str = perf_str[:-1].strip()
    # Remove trailing unit suffixes like "m", "A", "`" (e.g., "28.90m", "7.74A")
    # Match: digits, optional decimal, digits, then strip any trailing non-digit chars
    match = re.match(r'^(\d+\.?\d*).*$', perf_str)
    if match:
        perf_str = match.group(1)
    if perf_str.count('.') == 2:
        parts = perf_str.split('.')
        if all(p.isdigit() for p in parts):
            minutes = int(parts[0])
            seconds = int(parts[1])
            centiseconds = parts[2]
            total_seconds = minutes * 60 + seconds
            return f"{total_seconds}.{centiseconds}"
    if perf_str.count('.') > 1:
        return None
    if '-' in perf_str:
        return None
    if '(' in perf_str or ')' in perf_str:
        return None
    if event_code and event_code in LONG_DISTANCE_EVENTS:
        if perf_str and '.' in perf_str:
            parts = perf_str.split('.')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                minutes = int(parts[0])
                seconds = int(parts[1])
                if seconds < 60 and minutes < 200:
                    total_seconds = minutes * 60 + seconds
                    return f"{total_seconds}.00"
    return perf_str if perf_str else None


def extract_short_name(full_name):
    """Extract short name from 'City, Meet Name' format."""
    if not full_name:
        return None
    # If there's a comma, take everything after it
    if ', ' in full_name:
        return full_name.split(', ', 1)[1].strip()
    return full_name.strip()


def build_meet_lookup():
    """Build meet lookup with both full names and short names."""
    logger.info("Loading meets from database...")

    # Fetch all meets
    all_meets = []
    offset = 0
    batch_size = 1000

    while True:
        resp = supabase.table('meets').select('id, name, start_date').range(offset, offset + batch_size - 1).execute()
        if not resp.data:
            break
        all_meets.extend(resp.data)
        offset += batch_size
        if len(resp.data) < batch_size:
            break

    logger.info(f"Loaded {len(all_meets)} meets")

    # Build lookup with multiple keys
    # Key: (short_name, date) -> meet_id
    # Also keep (full_name, date) -> meet_id
    meet_lookup = {}

    for m in all_meets:
        full_name = m['name']
        date = m['start_date']
        meet_id = m['id']

        # Add full name lookup
        meet_lookup[(full_name, date)] = meet_id

        # Add short name lookup (after comma)
        short_name = extract_short_name(full_name)
        if short_name and short_name != full_name:
            # Only add if not already present (prefer full match)
            key = (short_name, date)
            if key not in meet_lookup:
                meet_lookup[key] = meet_id

    logger.info(f"Built lookup with {len(meet_lookup)} entries")
    return meet_lookup




def main():
    # Load JSON data
    json_path = DATA_DIR / "all_athlete_results.json"
    logger.info(f"Loading results from {json_path}...")
    with open(json_path, 'r') as f:
        results = json.load(f)
    logger.info(f"Loaded {len(results)} results from JSON")

    # Load lookup tables
    logger.info("Loading events...")
    events = {}
    resp = supabase.table('events').select('id, code, name').execute()
    for e in resp.data:
        events[e['code']] = e['id']
        events[e['name']] = e['id']
    logger.info(f"Loaded {len(events)} event mappings")

    logger.info("Loading seasons...")
    seasons = {}
    resp = supabase.table('seasons').select('id, year, indoor').execute()
    for s in resp.data:
        seasons[(s['year'], s['indoor'])] = s['id']
    logger.info(f"Loaded {len(seasons)} seasons")

    logger.info("Loading clubs...")
    clubs = {}
    offset = 0
    batch_size = 1000
    while True:
        resp = supabase.table('clubs').select('id, name').range(offset, offset + batch_size - 1).execute()
        if not resp.data:
            break
        for c in resp.data:
            clubs[c['name']] = c['id']
        offset += batch_size
        if len(resp.data) < batch_size:
            break
    logger.info(f"Loaded {len(clubs)} clubs")

    logger.info("Loading athletes...")
    athletes = {}
    offset = 0
    batch_size = 1000
    while True:
        resp = supabase.table('athletes').select('id, external_id').range(offset, offset + batch_size - 1).execute()
        if not resp.data:
            break
        for a in resp.data:
            if a['external_id']:
                athletes[str(a['external_id'])] = a['id']
        offset += batch_size
        logger.info(f"Loaded {offset} athletes so far...")
        if len(resp.data) < batch_size:
            break
    logger.info(f"Loaded {len(athletes)} athletes total")

    # Build improved meet lookup
    meets = build_meet_lookup()

    # Process results - no duplicate check, we'll use upsert
    logger.info("Processing results...")
    new_records = []
    skipped = {'no_event': 0, 'no_athlete': 0, 'no_meet': 0, 'invalid_perf': 0, 'invalid_date': 0, 'no_season': 0}
    seen_keys = set()  # Deduplicate within the batch

    for r in tqdm(results, desc="Processing"):
        # Get event ID
        event_name = r.get('event_name', '')
        event_code = EVENT_MAP.get(event_name)
        event_id = events.get(event_code) or events.get(event_name)
        if not event_id:
            skipped['no_event'] += 1
            continue

        # Clean performance
        perf = clean_performance(r.get('performance'), event_code)
        if not perf:
            skipped['invalid_perf'] += 1
            continue

        # Validate date
        date = validate_date(r.get('date'))
        if not date:
            skipped['invalid_date'] += 1
            continue

        # Get athlete ID
        ext_id = str(r.get('athlete_id')) if r.get('athlete_id') else None
        athlete_id = athletes.get(ext_id) if ext_id else None
        if not athlete_id:
            skipped['no_athlete'] += 1
            continue

        # Get meet ID - try multiple lookups
        meet_name = r.get('meet_name', '')
        meet_id = meets.get((meet_name, date))
        if not meet_id:
            skipped['no_meet'] += 1
            continue

        # Parse round - default to 'final' for uniqueness constraint
        round_val = r.get('round')
        if round_val not in ['heat', 'final', 'semi', 'qualification']:
            round_val = 'final'

        heat_num = r.get('heat') or 1

        # Deduplicate within batch
        result_key = (athlete_id, event_id, meet_id, round_val, heat_num)
        if result_key in seen_keys:
            continue
        seen_keys.add(result_key)

        # Get season ID - required field, skip if not found
        year = r.get('season', 2025)
        indoor = r.get('indoor', False)
        season_id = seasons.get((year, indoor))
        if not season_id:
            skipped['no_season'] += 1
            continue

        # Get club ID
        club_name = clean_club_name(r.get('club'))
        club_id = clubs.get(club_name) if club_name else None

        new_records.append({
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': perf,
            'date': date,
            'wind': r.get('wind'),
            'place': r.get('place'),
            'round': round_val,
            'heat_number': heat_num,
            'club_id': club_id,
            'verified': True,
        })

    logger.info(f"Skipped: {skipped}")
    logger.info(f"New records to insert: {len(new_records)}")

    if not new_records:
        logger.info("No new records to insert!")
        return

    # Upsert in batches - ignore conflicts (duplicates)
    batch_size = 500
    inserted = 0
    failed = 0

    for i in tqdm(range(0, len(new_records), batch_size), desc="Upserting"):
        batch = new_records[i:i+batch_size]
        try:
            # Use upsert with ignore_duplicates to skip existing records
            supabase.table('results').upsert(batch, on_conflict='athlete_id,event_id,meet_id,round,heat_number', ignore_duplicates=True).execute()
            inserted += len(batch)
        except Exception as e:
            logger.error(f"Batch error at {i}: {e}")
            # Try one by one
            for record in batch:
                try:
                    supabase.table('results').upsert(record, on_conflict='athlete_id,event_id,meet_id,round,heat_number', ignore_duplicates=True).execute()
                    inserted += 1
                except Exception as e2:
                    failed += 1
                    if failed <= 10:
                        logger.warning(f"Single upsert failed: {e2}")

    logger.info(f"Upserted {inserted} results (duplicates ignored), {failed} failed")


if __name__ == "__main__":
    main()
