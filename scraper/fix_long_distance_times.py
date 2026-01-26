"""
Fix incorrectly stored times for long distance events.

Some results have times stored in H.MM format (1.09 = 1 hour 9 minutes)
instead of total seconds. This script identifies and fixes them.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def parse_hour_minute_format(perf_str: str) -> tuple[float, int] | None:
    """
    Parse H.MM or H.MM.SS format and return (total_seconds, total_centiseconds).
    Returns None if not in expected format.
    """
    try:
        parts = perf_str.split('.')
        if len(parts) == 2:
            # H.MM format (e.g., "1.09" = 1 hour 9 minutes)
            hours = int(parts[0])
            minutes = int(parts[1])
            if hours >= 1 and hours <= 3 and minutes >= 0 and minutes <= 59:
                total_seconds = hours * 3600 + minutes * 60
                return total_seconds, int(total_seconds * 100)
        elif len(parts) == 3:
            # H.MM.SS format (e.g., "1.09.30" = 1 hour 9 minutes 30 seconds)
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            if hours >= 1 and hours <= 3 and minutes >= 0 and minutes <= 59:
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return total_seconds, int(total_seconds * 100)
    except:
        pass
    return None


def main():
    # Events that typically have times over 1 hour
    long_events = [
        '20000 meter',
        '25000 meter',
        '30000 meter',
        'Kappgang 20000 meter',
        'Kappgang 50000 meter',
    ]

    # Get event IDs
    events = supabase.table('events').select('id, name').in_('name', long_events).execute()
    event_ids = {e['name']: e['id'] for e in events.data}

    print(f"Found events: {list(event_ids.keys())}")
    print()

    total_fixed = 0

    for event_name, event_id in event_ids.items():
        # Get results that look suspicious (performance_value < 50000 centiseconds = 500 seconds)
        # Real times for these events should be at least 3000+ seconds (50+ minutes)
        results = supabase.table('results').select(
            'id, performance, performance_value'
        ).eq('event_id', event_id).lt('performance_value', 50000).execute()

        if not results.data:
            continue

        print(f"\n{event_name}:")
        print("-" * 60)

        for r in results.data:
            perf = r['performance']
            old_val = r['performance_value']

            # Try to parse as H.MM format
            parsed = parse_hour_minute_format(perf)
            if parsed:
                new_seconds, new_centiseconds = parsed
                new_perf = f"{new_seconds:.2f}"

                print(f"  Fixing: {perf} ({old_val} cs) -> {new_perf} ({new_centiseconds} cs)")

                # Update the result
                supabase.table('results').update({
                    'performance': new_perf,
                    'performance_value': new_centiseconds
                }).eq('id', r['id']).execute()

                total_fixed += 1
            else:
                print(f"  Skipping: {perf} ({old_val} cs) - doesn't match H.MM pattern")

    print()
    print("=" * 60)
    print(f"Total fixed: {total_fixed} results")


if __name__ == '__main__':
    main()
