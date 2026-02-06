"""
Fix NULL performance_values for middle/long distance events.
The format conversion script updated performance but not performance_value.
"""

import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def parse_time_to_hundredths(perf):
    """Convert M:SS.cc or M:SS format to hundredths of seconds."""
    if not perf or ':' not in perf:
        return None

    # Try M:SS.cc format (e.g., "1:42.58")
    match = re.match(r'^(\d+):(\d{2})\.(\d{1,2})$', perf)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        cents = match.group(3)
        # Pad to 2 digits if needed (e.g., "1:42.5" -> 50 hundredths)
        cents = int(cents.ljust(2, '0'))
        return (mins * 60 + secs) * 100 + cents

    # Try M:SS format (e.g., "1:42")
    match = re.match(r'^(\d+):(\d{2})$', perf)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        return (mins * 60 + secs) * 100

    # Try H:MM:SS format (e.g., "1:08:07" for marathon)
    match = re.match(r'^(\d+):(\d{2}):(\d{2})$', perf)
    if match:
        hours = int(match.group(1))
        mins = int(match.group(2))
        secs = int(match.group(3))
        return (hours * 3600 + mins * 60 + secs) * 100

    return None


def fix_null_performance_values():
    """Fix all NULL performance_values for middle/long distance events."""

    # Events that need fixing
    events = supabase.table('events').select('id, code, name').in_(
        'code', ['600m', '800m', '1000m', '1500m', '1mile', '2000m', '3000m', '5000m', '10000m']
    ).execute()

    event_map = {e['id']: e for e in events.data}

    print("Fixing NULL performance_values:")
    total_fixed = 0

    for e in events.data:
        event_id = e['id']
        event_name = e['name']

        # Count first
        count_result = supabase.table('results').select('id', count='exact').eq(
            'event_id', event_id
        ).is_('performance_value', 'null').execute()

        if count_result.count == 0:
            continue

        print(f"\n{event_name}: {count_result.count} records with NULL performance_value")

        fixed = 0
        errors = 0
        batch_size = 1000

        while True:
            # Fetch batch of records with NULL performance_value
            results = supabase.table('results').select(
                'id, performance'
            ).eq('event_id', event_id).is_(
                'performance_value', 'null'
            ).limit(batch_size).execute()

            if not results.data:
                break

            for r in results.data:
                perf = r['performance']
                new_value = parse_time_to_hundredths(perf)

                if new_value:
                    try:
                        supabase.table('results').update({
                            'performance_value': new_value
                        }).eq('id', r['id']).execute()
                        fixed += 1
                    except Exception as ex:
                        errors += 1
                        if errors <= 3:
                            print(f"  Error: {ex}")
                else:
                    # Can't parse - log it
                    if errors == 0:
                        print(f"  Could not parse: '{perf}'")
                    errors += 1

            print(f"  Progress: {fixed} fixed, {errors} errors")

        print(f"  Done: {fixed} fixed for {event_name}")
        total_fixed += fixed

    return total_fixed


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING NULL PERFORMANCE_VALUES")
    print("=" * 60)

    fixed = fix_null_performance_values()

    print(f"\n{'='*60}")
    print(f"TOTAL: {fixed} records fixed")
    print("=" * 60)
