"""
Fix road race times that are stored incorrectly.

Problems identified:
1. 10 km: Times like "1.00", "1.30" are meant to be 1 hour 0 min, 1 hour 30 min
   but are stored as if they were 1.00 seconds, 1.30 seconds

2. 100 km: Times like "6.33", "7.01" are meant to be 6 hours 33 min, 7 hours 1 min
   but are stored as if they were 6.33 seconds, 7.01 seconds

The pattern is: "H.MM" format being misinterpreted as seconds instead of hours:minutes

Fix: Convert H.MM to proper seconds
- "1.30" = 1 hour 30 min = 90 min = 5400 sec = 540000 hundredths
"""

import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

DRY_RUN = False  # Set to False to actually update

def parse_hour_min(performance):
    """Parse H.MM format and return total seconds."""
    match = re.match(r'^(\d+)\.(\d{2})$', performance)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        if minutes < 60:  # Valid minutes
            total_seconds = (hours * 60 + minutes) * 60
            return total_seconds
    return None

def fix_event_times(event_name, max_wrong_value, expected_min_hours=1):
    """Fix times for a specific event."""
    print(f"\n{'='*60}")
    print(f"Fixing {event_name}")
    print(f"{'='*60}")

    # Get event ID
    event = supabase.table('events').select('id').eq('name', event_name).limit(1).execute()
    if not event.data:
        print(f"  Event '{event_name}' not found!")
        return 0

    event_id = event.data[0]['id']

    # Get results with suspicious values (H.MM format stored as seconds)
    results = supabase.table('results').select(
        'id, performance, performance_value, athlete_id'
    ).eq('event_id', event_id).lt('performance_value', max_wrong_value).execute()

    if not results.data:
        print(f"  No suspicious results found")
        return 0

    fixed_count = 0
    for r in results.data:
        perf = r['performance']
        old_value = r['performance_value']

        # Check if it matches H.MM pattern
        total_seconds = parse_hour_min(perf)
        if total_seconds is None:
            continue

        # Calculate correct performance_value (hundredths of seconds)
        new_value = total_seconds * 100

        # Sanity check - for 10km, times should be 27-120 minutes typically
        # For 100km, times should be 6-15 hours typically
        hours = total_seconds / 3600
        if hours < expected_min_hours * 0.5 or hours > 24:
            print(f"  SKIP {perf} -> {hours:.1f}h seems wrong")
            continue

        # Get athlete name for logging
        athlete = supabase.table('athletes').select('full_name').eq('id', r['athlete_id']).limit(1).execute()
        athlete_name = athlete.data[0]['full_name'] if athlete.data else 'Unknown'

        hours = total_seconds // 3600
        mins = (total_seconds % 3600) // 60

        print(f"  {athlete_name}: {perf} -> {hours}h {mins}m ({old_value} -> {new_value})")

        if not DRY_RUN:
            supabase.table('results').update({
                'performance_value': new_value
            }).eq('id', r['id']).execute()

        fixed_count += 1

    return fixed_count

print("=" * 60)
print("FIXING ROAD RACE TIMES")
print("=" * 60)
if DRY_RUN:
    print("*** DRY RUN - ingen endringer vil bli gjort ***")
    print("Sett DRY_RUN = False for å faktisk oppdatere")

total_fixed = 0

# Fix 10 km - times stored as < 200 are likely H.MM format (1-2 hours)
total_fixed += fix_event_times('10 km', max_wrong_value=200, expected_min_hours=1)

# Fix 100 km - times stored as < 2000 are likely H.MM format (6-20 hours)
total_fixed += fix_event_times('100 km', max_wrong_value=2000, expected_min_hours=6)

# Check 3 km for any issues
total_fixed += fix_event_times('3 km', max_wrong_value=100, expected_min_hours=0.1)

# Fix Halvmaraton - times stored as < 10000 are likely H.MM format (1-2.5 hours)
# Normal half marathon: 1:05-2:30 = 3900-9000 seconds = 390000-900000 hundredths
total_fixed += fix_event_times('Halvmaraton', max_wrong_value=500000, expected_min_hours=1)

# Fix Maraton - times stored as < 20000 are likely H.MM format (2-6 hours)
# Normal marathon: 2:00-6:00 = 7200-21600 seconds = 720000-2160000 hundredths
total_fixed += fix_event_times('Maraton', max_wrong_value=2000000, expected_min_hours=2)

print(f"\n{'='*60}")
print(f"TOTALT: {total_fixed} resultater {'vil bli oppdatert' if DRY_RUN else 'oppdatert'}")
print("=" * 60)

if DRY_RUN:
    print("\nFor å faktisk oppdatere, endre DRY_RUN = False i scriptet")
