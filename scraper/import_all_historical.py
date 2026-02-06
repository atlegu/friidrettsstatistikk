#!/usr/bin/env python3
"""
Full import av alle historiske resultater fra historical_athletes_results.json
Kjøres: python import_all_historical.py
"""

import json
import sys
from supabase import create_client
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

print(f"Starter full import av historiske data: {datetime.now()}")
print("="*80)
sys.stdout.flush()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

with open('data/historical_athletes_results.json', 'r') as f:
    hist = json.load(f)

# Hent events
events = supabase.table('events').select('id, name').execute()
event_name_to_id = {e['name'].lower(): e['id'] for e in events.data}

# Hent sesonger
seasons = supabase.table('seasons').select('id, year').execute()
season_map = {s['year']: s['id'] for s in seasons.data}

# Cache for athletes og meets
athlete_cache = {}
meet_cache = {}

def get_athlete_id(name):
    if name in athlete_cache:
        return athlete_cache[name]
    athletes = supabase.table('athletes').select('id').eq('full_name', name).execute()
    athlete_id = athletes.data[0]['id'] if athletes.data else None
    athlete_cache[name] = athlete_id
    return athlete_id

def fix_date(date_str):
    if not date_str:
        return None
    parts = date_str.split('-')
    year = int(parts[0])
    month = parts[1] if len(parts) > 1 else '01'
    day = parts[2] if len(parts) > 2 else '01'
    if year > 2025:
        year = year - 100
    if month == '00':
        month = '06'
    if day == '00':
        day = '15'
    return f"{year}-{month}-{day}"

def parse_performance(perf_str):
    perf = str(perf_str).replace(',', '.').replace('(ok)', '').strip()

    if perf.count('.') == 2:
        parts = perf.split('.')
        mins = float(parts[0])
        secs = float(parts[1])
        hundredths = float(parts[2]) if len(parts[2]) == 2 else float(parts[2]) / 10
        total_secs = mins * 60 + secs + hundredths / 100
        return total_secs, int(total_secs * 1000)
    else:
        parts = perf.split('.')
        if len(parts) == 2:
            secs = float(parts[0]) + float(parts[1]) / 100
        else:
            secs = float(perf)
        return secs, int(secs * 1000)

def find_or_create_meet(city, meet_name, date, indoor=False):
    if not date:
        return None

    final_name = meet_name or (f"Stevne i {city}" if city else "Ukjent stevne")
    cache_key = f"{final_name}|{date}"

    if cache_key in meet_cache:
        return meet_cache[cache_key]

    meets = supabase.table('meets').select('id').eq('name', final_name).eq('start_date', date).execute()
    if meets.data:
        meet_cache[cache_key] = meets.data[0]['id']
        return meets.data[0]['id']

    year = int(date.split('-')[0])
    season_id = season_map.get(year)

    new_meet = {
        'name': final_name,
        'city': city,
        'start_date': date,
        'end_date': date,
        'indoor': indoor,
    }
    if season_id:
        new_meet['season_id'] = season_id

    result = supabase.table('meets').insert(new_meet).execute()
    meet_id = result.data[0]['id']
    meet_cache[cache_key] = meet_id
    return meet_id

# Hent alle eksisterende resultater for å unngå duplikater
print("Henter eksisterende resultater...")
sys.stdout.flush()

import time

existing = set()
offset = 0
batch_size = 1000
max_retries = 3

while True:
    for attempt in range(max_retries):
        try:
            batch = supabase.table('results').select('athlete_id, event_id, date').range(offset, offset + batch_size - 1).execute()
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1} ved offset {offset}...")
                time.sleep(5)
            else:
                print(f"  Feil ved offset {offset}, hopper over: {e}")
                batch = type('obj', (object,), {'data': []})()

    if not batch.data:
        break
    for r in batch.data:
        existing.add(f"{r['athlete_id']}|{r['event_id']}|{r['date']}")
    offset += batch_size
    if offset % 50000 == 0:
        print(f"  Hentet {offset} resultater...")
        sys.stdout.flush()
        time.sleep(1)  # Pause mellom store batches
    if len(batch.data) < batch_size:
        break

print(f"Fant {len(existing)} eksisterende resultater")
print(f"\nImporterer {len(hist)} historiske resultater...")
sys.stdout.flush()

imported = 0
skipped = 0
errors = 0
no_athlete = 0
no_event = 0

for i, r in enumerate(hist):
    if i % 5000 == 0 and i > 0:
        print(f"  Prosessert {i}/{len(hist)} - Importert: {imported}, Hoppet over: {skipped}")
        sys.stdout.flush()

    name = r.get('name')
    event_name = r.get('event_name', '').lower()
    date = fix_date(r.get('date'))

    if not date or not name or not event_name:
        skipped += 1
        continue

    athlete_id = get_athlete_id(name)
    if not athlete_id:
        no_athlete += 1
        continue

    event_id = event_name_to_id.get(event_name)
    if not event_id:
        no_event += 1
        continue

    key = f"{athlete_id}|{event_id}|{date}"
    if key in existing:
        skipped += 1
        continue

    try:
        perf_display, perf_value = parse_performance(r.get('performance'))
        meet_id = find_or_create_meet(r.get('city'), r.get('meet_name'), date, r.get('indoor', False))

        year = int(date.split('-')[0])
        season_id = season_map.get(year)

        if not season_id:
            skipped += 1
            continue

        new_result = {
            'athlete_id': athlete_id,
            'event_id': event_id,
            'meet_id': meet_id,
            'season_id': season_id,
            'performance': perf_display,
            'performance_value': perf_value,
            'date': date,
            'place': r.get('place'),
            'status': 'OK',
            'verified': True
        }

        for attempt in range(3):
            try:
                supabase.table('results').insert(new_result).execute()
                break
            except Exception as insert_err:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise insert_err
        existing.add(key)
        imported += 1

    except Exception as e:
        errors += 1

    # Pause hver 100. import for å ikke overbelaste
    if imported > 0 and imported % 100 == 0:
        time.sleep(0.5)

print(f"\n{'='*80}")
print(f"FERDIG: {datetime.now()}")
print(f"  Importert: {imported}")
print(f"  Hoppet over (duplikater): {skipped}")
print(f"  Utøver ikke funnet: {no_athlete}")
print(f"  Øvelse ikke funnet: {no_event}")
print(f"  Feil: {errors}")
