"""
Import men's data to Supabase.
Based on import_women.py but uses men_results_raw.json
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

# Event name mapping
EVENT_MAP = {
    '30 meter': '30m', '40 meter': '40m', '50 meter': '50m', '55 meter': '55m',
    '60 meter': '60m', '80 meter': '80m', '100 meter': '100m', '150 meter': '150m', '200 meter': '200m',
    '300 meter': '300m', '400 meter': '400m', '600 meter': '600m', '800 meter': '800m',
    '1000 meter': '1000m', '1500 meter': '1500m', '2000 meter': '2000m', '3000 meter': '3000m',
    '5000 meter': '5000m', '10000 meter': '10000m', '20000 meter': '20000m', '25000 meter': '25000m',
    '3 km': '3km', '5 km': '5km', '10 km': '10km', '1 mile': '1mile', '2 miles': '2miles',
    'Halvmaraton': 'halvmaraton', 'Maraton': 'maraton', '100 km': '100km',
    '60 meter hekk': '60mh',
    '60 meter hekk (60cm)': '60mh', '60 meter hekk (68,0cm)': '60mh', '60 meter hekk (76,2cm)': '60mh',
    '60 meter hekk (84,0cm)': '60mh', '60 meter hekk (91,4cm)': '60mh',
    '60 meter hekk (100cm)': '60mh', '60 meter hekk (106,7 cm)': '60mh',
    '80 meter hekk (68,0cm)': '80mh', '80 meter hekk (76,2cm)': '80mh',
    '80 meter hekk (84,0cm)': '80mh', '80 meter hekk (84,0cm/8,5m)': '80mh', '80 meter hekk (91,4cm)': '80mh',
    '100 meter hekk': '100mh', '100 meter hekk (84,0cm)': '100mh', '100 meter hekk (91,4cm)': '100mh',
    '110 meter hekk (106,7cm)': '110mh', '110 meter hekk (100cm)': '110mh', '110 meter hekk (91,4cm)': '110mh',
    '200 meter hekk': '200mh', '200 meter hekk (68,0cm)': '200mh', '200 meter hekk (76,2cm)': '200mh',
    '300 meter hekk (68,0cm)': '300mh', '300 meter hekk (76,2cm)': '300mh',
    '300 meter hekk (84,0cm)': '300mh', '300 meter hekk (91,4cm)': '300mh', '300 meter hekk (91,4cm-8hk)': '300mh',
    '400 meter hekk (76,2cm)': '400mh', '400 meter hekk (84,0cm)': '400mh', '400 meter hekk (91,4cm)': '400mh',
    '40 meter hekk (76,2cm)': '40mh', '40 meter hekk (91,4cm)': '40mh',
    '1500 meter hinder (76,2cm)': '1500mhinder',
    '2000 meter hinder (76,2cm)': '2000mhinder', '2000 meter hinder (84,0cm)': '2000mhinder',
    '2000 meter hinder (91,4cm)': '2000mhinder',
    '3000 meter hinder (76,2cm)': '3000mhinder', '3000 meter hinder (84,0cm)': '3000mhinder',
    '3000 meter hinder (91,4cm)': '3000mhinder',
    'Høyde': 'hoyde', 'Høyde uten tilløp': 'hoyde_ut',
    'Stav': 'stav',
    'Lengde': 'lengde', 'Lengde uten tilløp': 'lengde_ut', 'Lengde (Sone 0,5m)': 'lengde',
    'Tresteg': 'tresteg', 'Tresteg uten tilløp': 'tresteg_ut', 'Tresteg (Sone 0,5m)': 'tresteg',
    'Kule': 'kule', 'Kule 2,0kg': 'kule', 'Kule 3,0kg': 'kule', 'Kule 4,0kg': 'kule',
    'Kule 5,0kg': 'kule', 'Kule 5,44kg (12lb)': 'kule', 'Kule 5,5kg': 'kule',
    'Kule 6,0kg': 'kule', 'Kule 7,26kg': 'kule',
    'Diskos': 'diskos', 'Diskos 600gram': 'diskos', 'Diskos 750gram': 'diskos',
    'Diskos 1,0kg': 'diskos', 'Diskos 1,5kg': 'diskos', 'Diskos 1,6kg': 'diskos',
    'Diskos 1,75kg': 'diskos', 'Diskos 2,0kg': 'diskos', 'Diskos 2,5kg': 'diskos',
    'Slegge': 'slegge',
    'Slegge 2,0kg/110cm': 'slegge', 'Slegge 3,0kg/110cm': 'slegge',
    'Slegge 3,0kg/120cm': 'slegge', 'Slegge 3,0Kg (119,5cm)': 'slegge',
    'Slegge 4,0kg/119,5cm': 'slegge', 'Slegge 4,0kg/120cm': 'slegge',
    'Slegge 5,0kg/120cm': 'slegge', 'Slegge 6,0kg/121,5cm': 'slegge', 'Slegge 7,26kg/121,5cm': 'slegge',
    'Spyd': 'spyd', 'Spyd 400gram': 'spyd', 'Spyd 500gram': 'spyd', 'Spyd 600gram': 'spyd',
    'Spyd 700gram': 'spyd', 'Spyd 700 gram (2025)': 'spyd', 'Spyd 800gram': 'spyd',
    'Liten Ball': 'litenball', 'Liten Ball 150gram': 'litenball', 'Liten Ball 300gram': 'litenball',
    'Slengball': 'slengball', 'Slengball 1,0Kg': 'slengball', 'Slengball800gr': 'slengball',
    'VektKast4,0kg': 'vektkast', 'VektKast 5,45Kg': 'vektkast', 'VektKast 7,26Kg': 'vektkast',
    'VektKast 9,08Kg': 'vektkast', 'VektKast 11,34Kg': 'vektkast', 'VektKast 15,88Kg': 'vektkast',
    'Supervekt 15,88Kg': 'supervekt', 'Supervekt 25,4Kg': 'supervekt',
    'Femkamp': '5kamp', 'Sjukamp': '7kamp', 'Tikamp': '10kamp',
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


def clean_performance(perf):
    if not perf:
        return None
    perf_str = str(perf).strip()

    if perf_str.endswith('(ok)'):
        perf_str = perf_str[:-4].strip()

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

    return perf_str if perf_str else None


def load_lookup_tables():
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
    clubs = set()
    for r in results:
        club = clean_club_name(r.get('club'))
        if club:
            clubs.add(club)

    resp = supabase.table('clubs').select('id, name').execute()
    existing = {c['name']: c['id'] for c in resp.data}

    new_clubs = [c for c in clubs if c not in existing]
    logger.info(f"Inserting {len(new_clubs)} new clubs (existing: {len(existing)})...")

    if new_clubs:
        club_list = [{'name': c} for c in new_clubs]
        batch_size = 500
        for i in range(0, len(club_list), batch_size):
            batch = club_list[i:i+batch_size]
            try:
                supabase.table('clubs').insert(batch).execute()
            except Exception as e:
                logger.warning(f"Club batch error: {e}")

    resp = supabase.table('clubs').select('id, name').execute()
    return {c['name']: c['id'] for c in resp.data}


def batch_upsert_athletes(results):
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
                'gender': 'M',  # All men
                'birth_date': r.get('birth_date'),
            }

    logger.info(f"Inserting {len(athletes)} men athletes...")

    athlete_list = list(athletes.values())
    batch_size = 500
    for i in tqdm(range(0, len(athlete_list), batch_size), desc="Athletes"):
        batch = athlete_list[i:i+batch_size]
        try:
            supabase.table('athletes').upsert(batch, on_conflict='external_id').execute()
        except Exception as e:
            logger.warning(f"Batch insert error: {e}")

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
    meets = {}
    for r in results:
        name = r.get('meet_name', '')
        date = r.get('date')
        if name and date:
            key = (name, date)
            if key not in meets:
                meets[key] = {
                    'name': name,
                    'start_date': date,
                    'city': r.get('city', ''),
                    'indoor': r.get('indoor', False),
                }

    logger.info(f"Inserting {len(meets)} meets...")

    meet_list = list(meets.values())
    batch_size = 500
    for i in tqdm(range(0, len(meet_list), batch_size), desc="Meets"):
        batch = meet_list[i:i+batch_size]
        try:
            supabase.table('meets').insert(batch).execute()
        except Exception as e:
            for m in batch:
                try:
                    supabase.table('meets').insert(m).execute()
                except:
                    pass

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
    logger.info(f"Preparing {len(results)} results...")

    result_records = []
    skipped = {'no_event': 0, 'no_athlete': 0, 'no_meet': 0, 'invalid_perf': 0}

    for r in results:
        perf = clean_performance(r.get('performance'))
        if not perf:
            skipped['invalid_perf'] += 1
            continue

        event_name = r.get('event_name', '')
        event_code = EVENT_MAP.get(event_name)
        event_id = events.get(event_code) or events.get(event_name)
        if not event_id:
            skipped['no_event'] += 1
            continue

        ext_id = str(r.get('athlete_id')) if r.get('athlete_id') else None
        athlete_id = athletes.get(ext_id) if ext_id else None
        if not athlete_id:
            skipped['no_athlete'] += 1
            continue

        meet_key = (r.get('meet_name', ''), r.get('date'))
        meet_id = meets.get(meet_key)
        if not meet_id:
            skipped['no_meet'] += 1
            continue

        year = r.get('season', 2024)
        indoor = r.get('indoor', False)
        season_id = seasons.get((year, indoor))

        club_name = clean_club_name(r.get('club'))
        club_id = clubs.get(club_name) if club_name else None

        round_val = r.get('round')
        if round_val not in ['heat', 'final', 'semi', 'qualification']:
            round_val = 'final'

        heat_num = r.get('heat')
        if heat_num is None:
            heat_num = 1

        result_records.append({
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': perf,
            'date': r.get('date'),
            'wind': r.get('wind'),
            'place': r.get('place'),
            'round': round_val,
            'heat_number': heat_num,
            'club_id': club_id,
            'verified': True,
        })

    logger.info(f"Prepared {len(result_records)} results (skipped: {skipped})")

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

    batch_size = 1000
    inserted = 0
    errors = 0
    for i in tqdm(range(0, len(result_records), batch_size), desc="Results"):
        batch = result_records[i:i+batch_size]
        try:
            supabase.table('results').upsert(
                batch,
                on_conflict='athlete_id,event_id,meet_id,round,heat_number'
            ).execute()
            inserted += len(batch)
        except Exception as e:
            errors += 1
            logger.error(f"Batch upsert error at {i}: {e}")

    logger.info(f"Inserted {inserted} results")
    return inserted


def main():
    logger.info("Loading men's data...")
    with open(DATA_DIR / 'men_results_raw.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    logger.info(f"Loaded {len(results)} men's results")

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
