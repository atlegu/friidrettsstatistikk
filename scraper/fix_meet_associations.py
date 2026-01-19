#!/usr/bin/env python3
"""Fix meet associations by matching on name + date + city."""

import sys
sys.stdout.reconfigure(line_buffering=True)

import json
from supabase import create_client
from dotenv import load_dotenv
import os
from collections import defaultdict

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("Loading source data...")
with open('data/all_athlete_results.json', 'r') as f:
    source_data = json.load(f)
print(f"Loaded {len(source_data)} main source results")

# Also load historical data
print("Loading historical data...")
with open('data/historical_athletes_results.json', 'r') as f:
    historical_data = json.load(f)
print(f"Loaded {len(historical_data)} historical results")

source_data.extend(historical_data)
print(f"Total source data: {len(source_data)}")

# Build lookup: (athlete_external_id, event_name, date, performance) -> city
# This allows us to find the correct city for each result
print("\nBuilding city lookup from source data...")
city_lookup = {}
for r in source_data:
    key = (str(r.get('athlete_id')), r.get('event_name'), r.get('date'), r.get('performance'))
    city_lookup[key] = (r.get('city'), r.get('meet_name'))

print(f"Built lookup with {len(city_lookup)} entries")

# Load all athletes to map external_id -> uuid
print("\nLoading athletes...")
athletes = {}
offset = 0
while True:
    batch = supabase.table('athletes').select('id, external_id').range(offset, offset + 999).execute()
    if not batch.data:
        break
    for a in batch.data:
        if a['external_id']:
            athletes[a['external_id']] = a['id']
    offset += 1000
print(f"Loaded {len(athletes)} athletes")

# Load all events to map name -> id
print("\nLoading events...")
events = {}
events_resp = supabase.table('events').select('id, name').execute()
for e in events_resp.data:
    events[e['name']] = e['id']
print(f"Loaded {len(events)} events")

# Load existing meets
print("\nLoading existing meets...")
meets = {}  # (name, date, city) -> id
offset = 0
while True:
    batch = supabase.table('meets').select('id, name, start_date, city').range(offset, offset + 999).execute()
    if not batch.data:
        break
    for m in batch.data:
        key = (m['name'], m['start_date'], m['city'])
        meets[key] = m['id']
    offset += 1000
print(f"Loaded {len(meets)} meets")

def get_or_create_meet(name, date, city):
    """Get or create meet with exact name + date + city match."""
    key = (name, date, city)
    if key in meets:
        return meets[key]

    # Create new meet
    try:
        response = supabase.table('meets').insert({
            'name': name,
            'start_date': date,
            'city': city or 'Ukjent',
            'country': 'NOR'
        }).execute()
        if response.data:
            meets[key] = response.data[0]['id']
            return meets[key]
    except Exception as e:
        print(f"  Failed to create meet {name} at {city}: {e}")
    return None

# Process results and fix associations
print("\nProcessing results...")
batch_size = 1000
offset = 0
fixed = 0
not_found = 0
already_correct = 0

while True:
    results = supabase.table('results').select(
        'id, athlete_id, event_id, meet_id, date, performance'
    ).range(offset, offset + batch_size - 1).execute()

    if not results.data:
        break

    for r in results.data:
        # Skip results before 2011 - these should not be linked to meet result lists
        if r['date'] and r['date'] < '2011-01-01':
            not_found += 1  # Count as "not found" since we're skipping
            continue

        # Find the athlete's external_id
        athlete_ext_id = None
        for ext_id, uuid in athletes.items():
            if uuid == r['athlete_id']:
                athlete_ext_id = ext_id
                break

        if not athlete_ext_id:
            not_found += 1
            continue

        # Find the event name
        event_name = None
        for name, eid in events.items():
            if eid == r['event_id']:
                event_name = name
                break

        if not event_name:
            not_found += 1
            continue

        # Look up the correct city from source data
        lookup_key = (athlete_ext_id, event_name, r['date'], r['performance'])
        if lookup_key not in city_lookup:
            not_found += 1
            continue

        correct_city, correct_meet_name = city_lookup[lookup_key]

        # Get or create the correct meet
        correct_meet_id = get_or_create_meet(correct_meet_name, r['date'], correct_city)

        if not correct_meet_id:
            not_found += 1
            continue

        # Check if already correct
        if r['meet_id'] == correct_meet_id:
            already_correct += 1
            continue

        # Update the result
        try:
            supabase.table('results').update({'meet_id': correct_meet_id}).eq('id', r['id']).execute()
            fixed += 1
        except Exception as e:
            # If there's a duplicate constraint violation, delete this result as it's a duplicate
            if '23505' in str(e):
                try:
                    supabase.table('results').delete().eq('id', r['id']).execute()
                    # Don't count as fixed, it's a duplicate that was removed
                except:
                    pass
            else:
                print(f"  Failed to update result: {e}")

    offset += batch_size
    if offset % 50000 == 0:
        print(f"  Processed {offset} results (fixed: {fixed}, correct: {already_correct}, not found: {not_found})")

print(f"\n=== Summary ===")
print(f"Total processed: {offset}")
print(f"Fixed: {fixed}")
print(f"Already correct: {already_correct}")
print(f"Not found in source: {not_found}")
print(f"New meets created: {len(meets) - 36542}")  # Original count

print("\nDone!")
