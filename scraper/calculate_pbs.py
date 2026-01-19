#!/usr/bin/env python3
"""Calculate and set is_pb and is_national_record flags for all results."""

import sys
sys.stdout.reconfigure(line_buffering=True)

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Get all events with their result_type
print("Loading events...")
events_resp = supabase.table('events').select('id, name, result_type').execute()
events = {e['id']: e for e in events_resp.data}
print(f"Loaded {len(events)} events")

# For time events: lower is better
# For distance/height/points: higher is better
def is_better(new_value, old_value, result_type):
    if result_type == 'time':
        return new_value < old_value
    return new_value > old_value

# Get athletes with their gender (with pagination)
print("Loading athletes...")
athletes = {}
athlete_offset = 0
while True:
    athletes_resp = supabase.table('athletes').select('id, gender').range(athlete_offset, athlete_offset + 999).execute()
    if not athletes_resp.data:
        break
    for a in athletes_resp.data:
        athletes[a['id']] = a['gender']
    athlete_offset += 1000
print(f"Loaded {len(athletes)} athletes")

# First, let's calculate PBs per athlete/event
print("\nCalculating personal bests...")

batch_size = 1000
offset = 0

# Track best result per athlete/event
best_by_athlete_event = {}  # key: (athlete_id, event_id), value: (result_id, performance_value)

while True:
    results = supabase.table('results').select(
        'id, athlete_id, event_id, performance_value'
    ).gt('performance_value', 0).range(offset, offset + batch_size - 1).execute()

    if not results.data:
        break

    for r in results.data:
        key = (r['athlete_id'], r['event_id'])
        event = events.get(r['event_id'])
        if not event:
            continue

        result_type = event['result_type']
        value = r['performance_value']

        if key not in best_by_athlete_event:
            best_by_athlete_event[key] = (r['id'], value)
        else:
            current_best_id, current_best_value = best_by_athlete_event[key]
            if is_better(value, current_best_value, result_type):
                best_by_athlete_event[key] = (r['id'], value)

    offset += batch_size
    if offset % 100000 == 0:
        print(f"  Processed {offset} results...")

print(f"Found {len(best_by_athlete_event)} athlete/event PBs")

# Update PBs in batches
print("\nUpdating is_pb flags...")
pb_ids = [result_id for result_id, _ in best_by_athlete_event.values()]

for i in range(0, len(pb_ids), 100):
    batch = pb_ids[i:i+100]
    for result_id in batch:
        supabase.table('results').update({'is_pb': True}).eq('id', result_id).execute()
    if (i + 100) % 10000 == 0:
        print(f"  Updated {i + 100} PBs...")

print(f"Updated {len(pb_ids)} personal bests")

# Now calculate national records (best per event/gender)
print("\nCalculating national records...")
best_by_event_gender = {}  # key: (event_id, gender), value: (result_id, performance_value)

offset = 0
while True:
    results = supabase.table('results').select(
        'id, athlete_id, event_id, performance_value'
    ).gt('performance_value', 0).eq('status', 'OK').range(offset, offset + batch_size - 1).execute()

    if not results.data:
        break

    for r in results.data:
        athlete_gender = athletes.get(r['athlete_id'])
        if not athlete_gender:
            continue

        event = events.get(r['event_id'])
        if not event:
            continue

        key = (r['event_id'], athlete_gender)
        result_type = event['result_type']
        value = r['performance_value']

        if key not in best_by_event_gender:
            best_by_event_gender[key] = (r['id'], value)
        else:
            current_best_id, current_best_value = best_by_event_gender[key]
            if is_better(value, current_best_value, result_type):
                best_by_event_gender[key] = (r['id'], value)

    offset += batch_size
    if offset % 100000 == 0:
        print(f"  Processed {offset} results...")

print(f"Found {len(best_by_event_gender)} event/gender records")

# Update national records
print("\nUpdating is_national_record flags...")
nr_ids = [result_id for result_id, _ in best_by_event_gender.values()]

for i, result_id in enumerate(nr_ids):
    supabase.table('results').update({'is_national_record': True}).eq('id', result_id).execute()
    if (i + 1) % 50 == 0:
        print(f"  Updated {i + 1} NRs...")

print(f"Updated {len(nr_ids)} national records")
print("\nDone!")
