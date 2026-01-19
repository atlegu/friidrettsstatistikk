"""
Fast batch import to Supabase using service role key.
Optimized for speed with batch operations.
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

# Event name mapping (maps source event names to standardized codes)
EVENT_MAP = {
    # Running events
    '30 meter': '30m', '40 meter': '40m', '50 meter': '50m', '55 meter': '55m',
    '60 meter': '60m', '80 meter': '80m', '100 meter': '100m', '150 meter': '150m', '200 meter': '200m',
    '300 meter': '300m', '400 meter': '400m', '600 meter': '600m', '800 meter': '800m',
    '1000 meter': '1000m', '1500 meter': '1500m', '2000 meter': '2000m', '3000 meter': '3000m',
    '5000 meter': '5000m', '10000 meter': '10000m', '20000 meter': '20000m', '25000 meter': '25000m',
    # Road races
    '3 km': '3km', '5 km': '5km', '10 km': '10km', '1 mile': '1mile', '2 miles': '2miles',
    'Halvmaraton': 'halvmaraton', 'Maraton': 'maraton', '100 km': '100km',
    # Hurdles - height-specific events
    # 30 meter hekk
    '30 meter hekk 84,0cm': '30mh_84cm', '30 meter hekk (84,0cm)': '30mh_84cm',
    # 40 meter hekk
    '40 meter hekk': '40mh',
    '40 meter hekk (76,2cm)': '40mh_76_2cm', '40 meter hekk (84,0cm)': '40mh_84cm',
    '40 meter hekk (91,4cm)': '40mh_91_4cm', '40 meter hekk (100cm)': '40mh_100cm',
    # 55 meter hekk
    '55 meter hekk (84,0cm)': '55mh_84cm', '55 meter hekk (84cm)': '55mh_84cm',
    # 60 meter hekk (indoor)
    '60 meter hekk': '60mh',
    '60 meter hekk (60cm)': '60mh_60cm',
    '60 meter hekk (68,0cm)': '60mh_68cm', '60 meter hekk (68cm)': '60mh_68cm',
    '60 meter hekk (76,2cm)': '60mh_76_2cm',
    '60 meter hekk (84,0cm)': '60mh_84cm', '60 meter hekk (84cm)': '60mh_84cm',
    '60 meter hekk (91,4cm)': '60mh_91_4cm',
    '60 meter hekk (100cm)': '60mh_100cm',
    '60 meter hekk (106,7cm)': '60mh_106_7cm', '60 meter hekk (106,7 cm)': '60mh_106_7cm',
    # 80 meter hekk
    '80 meter hekk': '80mh',
    '80 meter hekk (68,0cm)': '80mh_68cm', '80 meter hekk (68cm)': '80mh_68cm',
    '80 meter hekk (76,2cm)': '80mh_76_2cm',
    '80 meter hekk (84,0cm)': '80mh_84cm', '80 meter hekk (84,0cm/8,5m)': '80mh_84cm', '80 meter hekk (84cm)': '80mh_84cm',
    '80 meter hekk (91,4cm)': '80mh_91_4cm',
    # 100 meter hekk
    '100 meter hekk': '100mh',
    '100 meter hekk (76,2cm)': '100mh_76_2cm',
    '100 meter hekk (84,0cm)': '100mh_84cm', '100 meter hekk (84cm)': '100mh_84cm',
    '100 meter hekk (91,4cm)': '100mh_91_4cm',
    # 110 meter hekk
    '110 meter hekk': '110mh',
    '110 meter hekk (91,4cm)': '110mh_91_4cm',
    '110 meter hekk (100cm)': '110mh_100cm',
    '110 meter hekk (106,7cm)': '110mh_106_7cm',
    # 200 meter hekk
    '200 meter hekk': '200mh',
    '200 meter hekk (68,0cm)': '200mh_68cm', '200 meter hekk (68cm)': '200mh_68cm',
    '200 meter hekk (76,2cm)': '200mh_76_2cm',
    # 300 meter hekk
    '300 meter hekk': '300mh',
    '300 meter hekk (68,0cm)': '300mh_68cm', '300 meter hekk (68cm)': '300mh_68cm',
    '300 meter hekk (76,2cm)': '300mh_76_2cm',
    '300 meter hekk (84,0cm)': '300mh_84cm', '300 meter hekk (84cm)': '300mh_84cm',
    '300 meter hekk (91,4cm)': '300mh_91_4cm', '300 meter hekk (91,4cm-8hk)': '300mh_91_4cm',
    # 400 meter hekk
    '400 meter hekk': '400mh',
    '400 meter hekk (68,0cm)': '400mh_68cm', '400 meter hekk (68cm)': '400mh_68cm',
    '400 meter hekk (76,2cm)': '400mh_76_2cm',
    '400 meter hekk (84,0cm)': '400mh_84cm', '400 meter hekk (84cm)': '400mh_84cm',
    '400 meter hekk (91,4cm)': '400mh_91_4cm',
    # Steeplechase - height-specific events
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
    # Jumps
    'Høyde': 'hoyde', 'Høyde uten tilløp': 'hoyde_ut',
    'Stav': 'stav',
    'Lengde': 'lengde', 'Lengde uten tilløp': 'lengde_ut', 'Lengde (Sone 0,5m)': 'lengde',
    'Tresteg': 'tresteg', 'Tresteg uten tilløp': 'tresteg_ut', 'Tresteg (Sone 0,5m)': 'tresteg',
    # Shot put - various weights (now mapped to specific weight events)
    'Kule': 'kule',
    'Kule 2,0kg': 'kule_2kg', 'Kule 2,0KG': 'kule_2kg',
    'Kule 3,0kg': 'kule_3kg', 'Kule 3,0KG': 'kule_3kg',
    'Kule 4,0kg': 'kule_4kg', 'Kule 4,0KG': 'kule_4kg',
    'Kule 5,0kg': 'kule_5kg', 'Kule 5,0KG': 'kule_5kg', 'Kule 5,44kg (12lb)': 'kule_5kg', 'Kule 5,5kg': 'kule_5kg',
    'Kule 6,0kg': 'kule_6kg', 'Kule 6,0KG': 'kule_6kg',
    'Kule 7,26kg': 'kule_7_26kg', 'Kule 7,26KG': 'kule_7_26kg',
    # Discus - various weights (now mapped to specific weight events)
    'Diskos': 'diskos',
    'Diskos 600gram': 'diskos_600g', 'Diskos 600GRAM': 'diskos_600g',
    'Diskos 750gram': 'diskos_750g', 'Diskos 750GRAM': 'diskos_750g',
    'Diskos 1,0kg': 'diskos_1kg', 'Diskos 1,0KG': 'diskos_1kg',
    'Diskos 1,5kg': 'diskos_1_5kg', 'Diskos 1,5KG': 'diskos_1_5kg', 'Diskos 1,6kg': 'diskos_1_5kg',
    'Diskos 1,75kg': 'diskos_1_75kg', 'Diskos 1,75KG': 'diskos_1_75kg',
    'Diskos 2,0kg': 'diskos_2kg', 'Diskos 2,0KG': 'diskos_2kg', 'Diskos 2,5kg': 'diskos_2kg',
    # Hammer - various weights/lengths (now mapped to specific weight events)
    'Slegge': 'slegge',
    'Slegge 2,0kg/110cm': 'slegge_2kg', 'Slegge 2,0kg': 'slegge_2kg',
    'Slegge 3,0kg/110cm': 'slegge_3kg', 'Slegge 3,0kg/120cm': 'slegge_3kg',
    'Slegge 3,0Kg (119,5cm)': 'slegge_3kg', 'Slegge 3,0kg': 'slegge_3kg',
    'Slegge 4,0kg/119,5cm': 'slegge_4kg', 'Slegge 4,0kg/120cm': 'slegge_4kg', 'Slegge 4,0kg': 'slegge_4kg',
    'Slegge 5,0kg/120cm': 'slegge_5kg', 'Slegge 5,0kg': 'slegge_5kg',
    'Slegge 6,0kg/121,5cm': 'slegge_6kg', 'Slegge 6,0kg': 'slegge_6kg',
    'Slegge 7,26kg/121,5cm': 'slegge_7_26kg', 'Slegge 7,26kg': 'slegge_7_26kg',
    # Javelin - various weights (now mapped to specific weight events)
    'Spyd': 'spyd',
    'Spyd 400gram': 'spyd_400g', 'Spyd 400GRAM': 'spyd_400g',
    'Spyd 500gram': 'spyd_500g', 'Spyd 500GRAM': 'spyd_500g',
    'Spyd 600gram': 'spyd_600g', 'Spyd 600GRAM': 'spyd_600g',
    'Spyd 700gram': 'spyd_700g', 'Spyd 700 gram (2025)': 'spyd_700g', 'Spyd 700GRAM': 'spyd_700g',
    'Spyd 800gram': 'spyd_800g', 'Spyd 800GRAM': 'spyd_800g',
    # Throws - other
    'Liten Ball': 'litenball', 'Liten Ball 150gram': 'litenball', 'Liten Ball 300gram': 'litenball',
    'Slengball': 'slengball', 'Slengball 1,0Kg': 'slengball', 'Slengball800gr': 'slengball',
    'VektKast4,0kg': 'vektkast', 'VektKast 5,45Kg': 'vektkast', 'VektKast 7,26Kg': 'vektkast',
    'VektKast 9,08Kg': 'vektkast', 'VektKast 11,34Kg': 'vektkast', 'VektKast 15,88Kg': 'vektkast',
    'Supervekt 15,88Kg': 'supervekt', 'Supervekt 25,4Kg': 'supervekt',
    # Multi-events
    'Femkamp': '5kamp', 'Sjukamp': '7kamp', 'Tikamp': '10kamp',
    # Walking
    'Kappgang 400 meter': 'kappgang', 'Kappgang 600 meter': 'kappgang', 'Kappgang 800 meter': 'kappgang',
    'Kappgang 1 km': 'kappgang', 'Kappgang 1000 meter': 'kappgang', 'Kappgang 1500 meter': 'kappgang',
    'Kappgang 2000 meter': 'kappgang', 'Kappgang 3 km': 'kappgang', 'Kappgang 3000 meter': 'kappgang',
    'Kappgang 5 km': 'kappgang', 'Kappgang 5000 meter': 'kappgang',
    'Kappgang 10 km': 'kappgang', 'Kappgang 10000 meter': 'kappgang', 'Kappgang 20 km': 'kappgang',
}


def clean_club_name(name):
    if not name or re.search(r'\d{2}[,\.]\d', name) or len(name) > 80:
        return None
    return name.strip()


def validate_date(date_str):
    """Validate and clean date string. Returns None if invalid."""
    if not date_str:
        return None
    try:
        # Check format
        parts = str(date_str).split('-')
        if len(parts) != 3:
            return None
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        # Validate ranges
        if year < 1900 or year > 2100:
            return None
        if month < 1 or month > 12:
            return None
        if day < 1 or day > 31:
            return None
        return date_str
    except:
        return None


# Events where times in "M.SS" format should be interpreted as minutes:seconds
# (not seconds.hundredths)
LONG_DISTANCE_EVENTS = {
    '800m', '1000m', '1500m', '2000m', '3000m', '5000m', '10000m', '20000m', '25000m',
    '1mile', '2miles', 'halvmaraton', 'maraton', '100km',
    '3000mhinder', '3000mhinder_76_2cm', '3000mhinder_84cm', '3000mhinder_91_4cm',
    '2000mhinder', '2000mhinder_76_2cm', '2000mhinder_84cm', '2000mhinder_91_4cm',
    '1500mhinder', '1500mhinder_76_2cm', '1500mhinder_91_4cm',
}


def clean_performance(perf, event_code=None):
    """Clean and validate performance value. Returns None if invalid.

    Converts time format M.SS.cc to total seconds (e.g., 1.35.23 -> 95.23).
    For long distance events, also converts M.SS to M:SS.00 format.
    """
    if not perf:
        return None
    perf_str = str(perf).strip()

    # Remove (ok) suffix
    if perf_str.endswith('(ok)'):
        perf_str = perf_str[:-4].strip()

    # Check for time format: M.SS.cc or MM.SS.cc (minutes.seconds.centiseconds)
    # Valid examples: "1.35.23" -> 95.23, "4.19.53" -> 259.53
    if perf_str.count('.') == 2:
        parts = perf_str.split('.')
        # Check if it's a valid time format (all parts are numeric)
        if all(p.isdigit() for p in parts):
            minutes = int(parts[0])
            seconds = int(parts[1])
            centiseconds = parts[2]
            # Convert to total seconds with centiseconds
            total_seconds = minutes * 60 + seconds
            return f"{total_seconds}.{centiseconds}"

    # Invalid if has multiple periods and not a valid time format
    if perf_str.count('.') > 1:
        return None

    # Invalid if contains dashes (like multi-event breakdown "11,06-6,13-9,69")
    if '-' in perf_str:
        return None

    # Invalid if contains parentheses (remaining after stripping ok)
    if '(' in perf_str or ')' in perf_str:
        return None

    # Handle manual times for long distance events: "M.SS" -> convert to seconds
    # e.g., "2.33" for 800m means 2:33 (153 seconds), not 2.33 seconds
    if event_code and event_code in LONG_DISTANCE_EVENTS:
        if perf_str and '.' in perf_str:
            parts = perf_str.split('.')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                minutes = int(parts[0])
                seconds = int(parts[1])
                # If seconds part is 0-59, it's likely M.SS format (minutes.seconds)
                if seconds < 60 and minutes < 200:  # reasonable time limits
                    total_seconds = minutes * 60 + seconds
                    return f"{total_seconds}.00"

    return perf_str if perf_str else None


def load_lookup_tables():
    """Load events and seasons into lookup dicts."""
    events = {}
    resp = supabase.table('events').select('id, code, name').execute()
    for e in resp.data:
        events[e['code']] = e['id']
        events[e['name']] = e['id']

    seasons = {}
    resp = supabase.table('seasons').select('id, year, indoor').execute()
    for s in resp.data:
        seasons[(s['year'], s['indoor'])] = s['id']

    return events, seasons


def batch_upsert_clubs(results):
    """Insert all unique clubs and return name->id mapping."""
    clubs = set()
    for r in results:
        club = clean_club_name(r.get('club'))
        if club:
            clubs.add(club)

    # First fetch existing clubs
    resp = supabase.table('clubs').select('id, name').execute()
    existing = {c['name']: c['id'] for c in resp.data}

    # Find new clubs
    new_clubs = [c for c in clubs if c not in existing]
    logger.info(f"Inserting {len(new_clubs)} new clubs (existing: {len(existing)})...")

    # Insert new clubs in batches
    if new_clubs:
        club_list = [{'name': c} for c in new_clubs]
        batch_size = 500
        for i in range(0, len(club_list), batch_size):
            batch = club_list[i:i+batch_size]
            try:
                supabase.table('clubs').insert(batch).execute()
            except Exception as e:
                logger.warning(f"Club batch error: {e}")

    # Fetch all clubs to get IDs
    resp = supabase.table('clubs').select('id, name').execute()
    return {c['name']: c['id'] for c in resp.data}


def batch_upsert_athletes(results):
    """Insert all unique athletes and return external_id->id mapping."""
    athletes = {}
    for r in results:
        ext_id = r.get('athlete_id')
        if ext_id and ext_id not in athletes:
            name = r.get('name', '')
            parts = name.split() if name else []
            athletes[ext_id] = {
                'external_id': str(ext_id),
                'first_name': parts[0] if parts else '',
                'last_name': ' '.join(parts[1:]) if len(parts) > 1 else '',
                'gender': r.get('gender'),
                'birth_date': r.get('birth_date'),
            }

    logger.info(f"Inserting {len(athletes)} athletes...")

    # Insert in batches
    athlete_list = list(athletes.values())
    batch_size = 500
    for i in tqdm(range(0, len(athlete_list), batch_size), desc="Athletes"):
        batch = athlete_list[i:i+batch_size]
        try:
            supabase.table('athletes').upsert(batch, on_conflict='external_id').execute()
        except Exception as e:
            logger.warning(f"Batch insert error: {e}")

    # Fetch all athletes to get IDs (with pagination)
    all_athletes = []
    offset = 0
    batch_size = 1000
    while True:
        resp = supabase.table('athletes').select('id, external_id').range(offset, offset + batch_size - 1).execute()
        all_athletes.extend(resp.data)
        if len(resp.data) < batch_size:
            break
        offset += batch_size

    return {a['external_id']: a['id'] for a in all_athletes if a['external_id']}


def batch_upsert_meets(results):
    """Insert all unique meets and return (name, date)->id mapping."""
    meets = {}
    for r in results:
        name = r.get('meet_name', '')
        date = validate_date(r.get('date'))
        if name and date:
            key = (name, date)
            if key not in meets:
                meets[key] = {
                    'name': name,
                    'start_date': date,
                    'city': r.get('city', ''),
                    'indoor': r.get('indoor', False),
                }

    logger.info(f"Upserting {len(meets)} meets...")

    # Upsert in batches (handles duplicates by name+date)
    meet_list = list(meets.values())
    batch_size = 500
    for i in tqdm(range(0, len(meet_list), batch_size), desc="Meets"):
        batch = meet_list[i:i+batch_size]
        try:
            supabase.table('meets').upsert(batch, on_conflict='name,start_date').execute()
        except Exception as e:
            # Try one by one if batch fails
            for m in batch:
                try:
                    supabase.table('meets').upsert([m], on_conflict='name,start_date').execute()
                except:
                    pass

    # Fetch all meets to get IDs (with pagination)
    all_meets = []
    offset = 0
    batch_size = 1000
    while True:
        resp = supabase.table('meets').select('id, name, start_date').range(offset, offset + batch_size - 1).execute()
        all_meets.extend(resp.data)
        if len(resp.data) < batch_size:
            break
        offset += batch_size

    return {(m['name'], m['start_date']): m['id'] for m in all_meets}


def batch_insert_results(results, events, seasons, clubs, athletes, meets):
    """Insert all results in batches."""
    logger.info(f"Preparing {len(results)} results...")

    result_records = []
    skipped = {'no_event': 0, 'no_athlete': 0, 'no_meet': 0, 'invalid_perf': 0, 'invalid_date': 0}

    for r in results:
        # Get event ID first (needed for performance parsing)
        event_name = r.get('event_name', '')
        event_code = EVENT_MAP.get(event_name)
        event_id = events.get(event_code) or events.get(event_name)
        if not event_id:
            skipped['no_event'] += 1
            continue

        # Clean and validate performance value (pass event_code for proper parsing)
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

        # Get meet ID (use validated date)
        meet_key = (r.get('meet_name', ''), date)
        meet_id = meets.get(meet_key)
        if not meet_id:
            skipped['no_meet'] += 1
            continue

        # Get season ID
        year = r.get('season', 2025)
        indoor = r.get('indoor', False)
        season_id = seasons.get((year, indoor))

        # Get club ID
        club_name = clean_club_name(r.get('club'))
        club_id = clubs.get(club_name) if club_name else None

        # Parse round - default to 'final' for uniqueness constraint
        round_val = r.get('round')
        if round_val not in ['heat', 'final', 'semi', 'qualification']:
            round_val = 'final'

        # Heat number - default to 1 for uniqueness constraint
        heat_num = r.get('heat')
        if heat_num is None:
            heat_num = 1

        result_records.append({
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': perf,  # Use cleaned performance
            'date': date,  # Use validated date
            'wind': r.get('wind'),
            'place': r.get('place'),
            'round': round_val,
            'heat_number': heat_num,
            'club_id': club_id,
            'verified': True,
        })

    logger.info(f"Prepared {len(result_records)} results (skipped: {skipped})")

    # Deduplicate: keep first occurrence of each unique key
    seen = set()
    unique_records = []
    for r in result_records:
        key = (r['athlete_id'], r['event_id'], r['meet_id'], r['round'], r['heat_number'])
        if key not in seen:
            seen.add(key)
            unique_records.append(r)

    duplicates_removed = len(result_records) - len(unique_records)
    logger.info(f"After dedup: {len(unique_records)} unique results ({duplicates_removed} duplicates removed)")
    result_records = unique_records

    # Upsert in batches with binary search for failures
    batch_size = 1000
    inserted = 0
    skipped_records = 0

    def upsert_batch(batch):
        """Try to upsert a batch, returns (success_count, failed_records)."""
        if not batch:
            return 0, []
        try:
            supabase.table('results').upsert(
                batch,
                on_conflict='athlete_id,event_id,meet_id,round,heat_number'
            ).execute()
            return len(batch), []
        except Exception as e:
            if len(batch) == 1:
                # Single record failed - skip it
                return 0, batch
            # Binary search: split batch in half and try each
            mid = len(batch) // 2
            left_success, left_failed = upsert_batch(batch[:mid])
            right_success, right_failed = upsert_batch(batch[mid:])
            return left_success + right_success, left_failed + right_failed

    for i in tqdm(range(0, len(result_records), batch_size), desc="Results"):
        batch = result_records[i:i+batch_size]
        success, failed = upsert_batch(batch)
        inserted += success
        skipped_records += len(failed)
        if failed and skipped_records <= 20:
            for rec in failed[:3]:  # Log first few
                logger.debug(f"Failed: {rec.get('performance')} date={rec.get('date')}")

    if skipped_records > 0:
        logger.warning(f"Skipped {skipped_records} invalid records")

    logger.info(f"Inserted {inserted} results")
    return inserted


def main():
    logger.info("Loading data...")
    # Load from men and women files which include gender field
    results = []

    men_file = DATA_DIR / 'men_results_raw.json'
    women_file = DATA_DIR / 'women_results_raw.json'
    all_athlete_file = DATA_DIR / 'all_athlete_results.json'

    # Build athlete_id -> gender map from men/women files
    athlete_gender = {}

    if men_file.exists():
        with open(men_file, 'r', encoding='utf-8') as f:
            men_results = json.load(f)
            logger.info(f"Loaded {len(men_results)} men's results from rankings")
            for r in men_results:
                if r.get('athlete_id'):
                    athlete_gender[r['athlete_id']] = 'M'
            results.extend(men_results)

    if women_file.exists():
        with open(women_file, 'r', encoding='utf-8') as f:
            women_results = json.load(f)
            logger.info(f"Loaded {len(women_results)} women's results from rankings")
            for r in women_results:
                if r.get('athlete_id'):
                    athlete_gender[r['athlete_id']] = 'F'
            results.extend(women_results)

    # Also load complete athlete results (ALL competitions, not just top results)
    if all_athlete_file.exists() and athlete_gender:
        with open(all_athlete_file, 'r', encoding='utf-8') as f:
            all_athlete_results = json.load(f)
            logger.info(f"Loaded {len(all_athlete_results)} results from individual athlete profiles")

        # Create a set of existing results to avoid duplicates
        # Key: (athlete_id, event_name, date, performance)
        existing_keys = set()
        for r in results:
            key = (r.get('athlete_id'), r.get('event_name'), r.get('date'), r.get('performance'))
            existing_keys.add(key)

        # Add results from all_athlete_results that aren't duplicates
        added = 0
        skipped_no_gender = 0
        skipped_duplicate = 0
        for r in all_athlete_results:
            aid = r.get('athlete_id')
            if aid not in athlete_gender:
                skipped_no_gender += 1
                continue

            key = (aid, r.get('event_name'), r.get('date'), r.get('performance'))
            if key in existing_keys:
                skipped_duplicate += 1
                continue

            # Add gender and include
            r['gender'] = athlete_gender[aid]
            results.append(r)
            existing_keys.add(key)
            added += 1

        logger.info(f"Added {added} unique results from athlete profiles")
        logger.info(f"Skipped {skipped_duplicate} duplicates, {skipped_no_gender} without gender")
    elif not results:
        logger.warning("Men/women files not found, falling back to all_athlete_results.json only")
        with open(all_athlete_file, 'r', encoding='utf-8') as f:
            results = json.load(f)

    logger.info(f"Total loaded: {len(results)} results")

    logger.info("Loading lookup tables...")
    events, seasons = load_lookup_tables()
    logger.info(f"Loaded {len(events)} events, {len(seasons)} seasons")

    logger.info("Upserting clubs...")
    clubs = batch_upsert_clubs(results)
    logger.info(f"Clubs ready: {len(clubs)}")

    logger.info("Upserting athletes...")
    athletes = batch_upsert_athletes(results)
    logger.info(f"Athletes ready: {len(athletes)}")

    logger.info("Upserting meets...")
    meets = batch_upsert_meets(results)
    logger.info(f"Meets ready: {len(meets)}")

    logger.info("Inserting results...")
    inserted = batch_insert_results(results, events, seasons, clubs, athletes, meets)

    logger.info(f"""
    Import complete!
    - Clubs: {len(clubs)}
    - Athletes: {len(athletes)}
    - Meets: {len(meets)}
    - Results: {inserted}
    """)


if __name__ == '__main__':
    main()
