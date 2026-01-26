"""
Fix incorrectly stored times for marathon/half marathon events.

Some results have times stored in MM.SS format (71.54 = 71 min 54 sec)
but were interpreted as seconds. This script identifies and fixes them.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def parse_minute_second_format(perf_str: str, perf_val: int) -> tuple[float, int] | None:
    """
    Parse MM.SS format and return (total_seconds, total_centiseconds).
    Returns None if not in expected format or already correct.

    We detect MM.SS format by checking if:
    - performance_value is suspiciously low (< 50000 cs = 500 seconds)
    - The performance string looks like MM.SS (e.g., "71.54")
    """
    try:
        # If already correct (high value), skip
        if perf_val > 100000:  # > 1000 seconds, probably correct
            return None

        parts = perf_str.split('.')
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1][:2])  # Take first 2 digits

            # Sanity check: reasonable half marathon/marathon time
            # Half marathon: 60-180 minutes, Marathon: 120-360 minutes
            if 60 <= minutes <= 360 and 0 <= seconds <= 59:
                total_seconds = minutes * 60 + seconds
                return total_seconds, int(total_seconds * 100)
    except:
        pass
    return None


def main():
    # Events that typically have times in MM.SS format
    marathon_events = [
        'Halvmaraton',
        'Maraton',
    ]

    # Get event IDs
    events = supabase.table('events').select('id, name').in_('name', marathon_events).execute()
    event_ids = {e['name']: e['id'] for e in events.data}

    print(f"Found events: {list(event_ids.keys())}")
    print()

    total_fixed = 0

    for event_name, event_id in event_ids.items():
        # Get results that look suspicious (performance_value < 50000 = 500 seconds)
        # Real half marathon times should be at least 3600 seconds (60 minutes)
        results = supabase.table('results').select(
            'id, performance, performance_value'
        ).eq('event_id', event_id).lt('performance_value', 50000).execute()

        if not results.data:
            print(f"\n{event_name}: No suspicious results found")
            continue

        print(f"\n{event_name}:")
        print("-" * 70)

        for r in results.data:
            perf = r['performance']
            old_val = r['performance_value']

            # Try to parse as MM.SS format
            parsed = parse_minute_second_format(perf, old_val)
            if parsed:
                new_seconds, new_centiseconds = parsed
                new_perf = f"{new_seconds:.2f}"

                # Format for display
                mins = int(new_seconds // 60)
                secs = new_seconds % 60
                time_display = f"{mins}:{secs:05.2f}"

                print(f"  Fixing: {perf} ({old_val} cs) -> {new_perf} ({new_centiseconds} cs) = {time_display}")

                # Update the result
                supabase.table('results').update({
                    'performance': new_perf,
                    'performance_value': new_centiseconds
                }).eq('id', r['id']).execute()

                total_fixed += 1
            else:
                print(f"  Skipping: {perf} ({old_val} cs) - doesn't match MM.SS pattern or already correct")

    print()
    print("=" * 70)
    print(f"Total fixed: {total_fixed} results")


if __name__ == '__main__':
    main()
