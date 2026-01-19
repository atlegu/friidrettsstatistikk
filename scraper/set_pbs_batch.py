#!/usr/bin/env python3
"""Set is_pb and is_national_record using batch updates."""

import sys
sys.stdout.reconfigure(line_buffering=True)

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Get all events with their result_type
# First, reset all flags using smaller batches
print("Resetting all PB and NR flags...")
reset_batch_size = 100
offset = 0
reset_count = 0

while True:
    # Find results with is_pb=true
    results = supabase.table('results').select('id').eq('is_pb', True).range(offset, offset + reset_batch_size - 1).execute()
    if not results.data:
        break

    ids = [r['id'] for r in results.data]
    try:
        supabase.table('results').update({'is_pb': False}).in_('id', ids).execute()
    except Exception as e:
        # Fall back to individual updates
        for rid in ids:
            try:
                supabase.table('results').update({'is_pb': False}).eq('id', rid).execute()
            except:
                pass
    reset_count += len(ids)
    if reset_count % 10000 == 0:
        print(f"  Reset {reset_count} PB flags...")

print(f"  Reset {reset_count} PB flags total")

offset = 0
reset_count = 0
while True:
    results = supabase.table('results').select('id').eq('is_national_record', True).range(offset, offset + reset_batch_size - 1).execute()
    if not results.data:
        break

    ids = [r['id'] for r in results.data]
    try:
        supabase.table('results').update({'is_national_record': False}).in_('id', ids).execute()
    except:
        for rid in ids:
            try:
                supabase.table('results').update({'is_national_record': False}).eq('id', rid).execute()
            except:
                pass
    reset_count += len(ids)

print(f"  Reset {reset_count} NR flags total")

print("\nLoading events...")
events_resp = supabase.table('events').select('id, name, result_type').execute()
events = {e['id']: e for e in events_resp.data}
print(f"Loaded {len(events)} events")

# Sprint events where manual times should be excluded
SPRINT_EVENTS = {'60 meter', '100 meter', '200 meter'}
sprint_event_ids = {e['id'] for e in events_resp.data if e['name'] in SPRINT_EVENTS}
print(f"Sprint events (manual times excluded): {SPRINT_EVENTS}")

def is_manual_time(performance):
    """Check if performance is a manual time (1 decimal)."""
    if not performance or '.' not in str(performance):
        return False
    decimals = len(str(performance).split('.')[-1])
    return decimals == 1

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

# Calculate PBs
print("\nCalculating personal bests...")
batch_size = 1000
offset = 0
manual_skipped = 0

best_by_athlete_event = {}  # key: (athlete_id, event_id), value: (result_id, performance_value)

while True:
    results = supabase.table('results').select(
        'id, athlete_id, event_id, performance_value, performance'
    ).gt('performance_value', 0).range(offset, offset + batch_size - 1).execute()

    if not results.data:
        break

    for r in results.data:
        event = events.get(r['event_id'])
        if not event:
            continue

        # Skip manual times for sprint events
        if r['event_id'] in sprint_event_ids and is_manual_time(r['performance']):
            manual_skipped += 1
            continue

        key = (r['athlete_id'], r['event_id'])
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

print(f"Found {len(best_by_athlete_event)} athlete/event PBs (skipped {manual_skipped} manual times)")

# Calculate NRs
print("\nCalculating national records...")
best_by_event_gender = {}  # key: (event_id, gender), value: (result_id, performance_value)
manual_skipped_nr = 0

offset = 0
while True:
    results = supabase.table('results').select(
        'id, athlete_id, event_id, performance_value, performance'
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

        # Skip manual times for sprint events
        if r['event_id'] in sprint_event_ids and is_manual_time(r['performance']):
            manual_skipped_nr += 1
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

print(f"Found {len(best_by_event_gender)} event/gender records (skipped {manual_skipped_nr} manual times)")

# Now update in batches using .in_() filter
print("\nUpdating is_pb flags in batches...")
pb_ids = [result_id for result_id, _ in best_by_athlete_event.values()]

# Update in batches of 500 (Supabase limit for .in_())
batch_size = 200
for i in range(0, len(pb_ids), batch_size):
    batch = pb_ids[i:i+batch_size]
    try:
        supabase.table('results').update({'is_pb': True}).in_('id', batch).execute()
    except Exception as e:
        print(f"  Error updating batch {i}: {e}")
        # Fall back to individual updates
        for result_id in batch:
            try:
                supabase.table('results').update({'is_pb': True}).eq('id', result_id).execute()
            except:
                pass

    if (i + batch_size) % 10000 == 0:
        print(f"  Updated {min(i + batch_size, len(pb_ids))} / {len(pb_ids)} PBs...")

print(f"Updated {len(pb_ids)} personal bests")

# Update NRs
print("\nUpdating is_national_record flags...")
nr_ids = [result_id for result_id, _ in best_by_event_gender.values()]

for i in range(0, len(nr_ids), batch_size):
    batch = nr_ids[i:i+batch_size]
    try:
        supabase.table('results').update({'is_national_record': True}).in_('id', batch).execute()
    except Exception as e:
        print(f"  Error updating NR batch {i}: {e}")
        for result_id in batch:
            try:
                supabase.table('results').update({'is_national_record': True}).eq('id', result_id).execute()
            except:
                pass

print(f"Updated {len(nr_ids)} national records")

# Verify
print("\nVerifying...")
pb_count = supabase.table('results').select('id', count='exact').eq('is_pb', True).execute()
print(f"Results with is_pb=true: {pb_count.count}")

nr_count = supabase.table('results').select('id', count='exact').eq('is_national_record', True).execute()
print(f"Results with is_national_record=true: {nr_count.count}")

print("\nDone!")
