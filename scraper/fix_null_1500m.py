"""
Fix NULL performance_values for 1500m and other remaining events.
Skip records that can't be parsed.
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
        cents = int(cents.ljust(2, '0'))
        return (mins * 60 + secs) * 100 + cents

    # Try M:SS format (e.g., "1:42")
    match = re.match(r'^(\d+):(\d{2})$', perf)
    if match:
        mins = int(match.group(1))
        secs = int(match.group(2))
        return (mins * 60 + secs) * 100

    return None


def fix_event(event_code, event_name):
    """Fix NULL performance_values for a specific event."""
    events = supabase.table('events').select('id').eq('code', event_code).execute()
    if not events.data:
        print(f"Event {event_code} not found")
        return 0

    event_id = events.data[0]['id']

    # Get count
    count_result = supabase.table('results').select('id', count='exact').eq(
        'event_id', event_id
    ).is_('performance_value', 'null').execute()

    if count_result.count == 0:
        print(f"{event_name}: No NULL values")
        return 0

    print(f"\n{event_name}: {count_result.count} records with NULL performance_value")

    fixed = 0
    skipped = 0
    processed_ids = set()  # Track processed to avoid loops

    while True:
        # Fetch batch of records
        results = supabase.table('results').select(
            'id, performance'
        ).eq('event_id', event_id).is_(
            'performance_value', 'null'
        ).limit(1000).execute()

        if not results.data:
            break

        batch_fixed = 0
        batch_skipped = 0

        for r in results.data:
            if r['id'] in processed_ids:
                # Already tried this one, skip
                batch_skipped += 1
                continue

            processed_ids.add(r['id'])
            perf = r['performance']
            new_value = parse_time_to_hundredths(perf)

            if new_value:
                try:
                    supabase.table('results').update({
                        'performance_value': new_value
                    }).eq('id', r['id']).execute()
                    batch_fixed += 1
                    fixed += 1
                except Exception as ex:
                    batch_skipped += 1
                    skipped += 1
            else:
                # Can't parse - mark with a placeholder value (0) to skip in future
                # Actually, let's just skip these and track them
                batch_skipped += 1
                skipped += 1

        print(f"  Progress: {fixed} fixed, {skipped} skipped")

        # If no progress was made in this batch, we're done (only unparseable left)
        if batch_fixed == 0:
            print(f"  Stopping - remaining records cannot be parsed")
            break

    return fixed


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING NULL PERFORMANCE_VALUES - 1500M AND OTHERS")
    print("=" * 60)

    total = 0
    for code, name in [('1500m', '1500 meter'), ('3000m', '3000 meter'),
                       ('5000m', '5000 meter'), ('600m', '600 meter')]:
        total += fix_event(code, name)

    print(f"\n{'='*60}")
    print(f"TOTAL: {total} records fixed")
    print("=" * 60)
