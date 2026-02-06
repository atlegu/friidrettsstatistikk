"""
Fix time format for middle/long distance events.

Problem: Times are stored as total seconds (e.g., "102.58" instead of "1:42.58")
Solution: Convert to proper M:SS.cc or H:MM:SS format for display.
"""

import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

DRY_RUN = False  # Set to False to actually update


def seconds_to_time_format(seconds_str):
    """Convert seconds string to proper time format.
    
    Examples:
        "102.58" -> "1:42.58" (for 800m)
        "222.5" -> "3:42.50" (for 1500m)
        "498.25" -> "8:18.25" (for 3000m)
    """
    try:
        total_seconds = float(seconds_str)
        
        # Extract minutes and remaining seconds
        minutes = int(total_seconds // 60)
        remaining_seconds = total_seconds % 60
        
        if minutes == 0:
            # Less than a minute - probably already correct or a sprint
            return None
        
        # Format: M:SS.cc or MM:SS.cc
        # Handle the decimal part
        secs_int = int(remaining_seconds)
        hundredths = round((remaining_seconds - secs_int) * 100)
        
        if hundredths > 0:
            return f"{minutes}:{secs_int:02d}.{hundredths:02d}"
        else:
            return f"{minutes}:{secs_int:02d}"
            
    except (ValueError, TypeError):
        return None


def is_seconds_format(perf):
    """Check if performance is in seconds format (not M:SS.cc)."""
    if not perf:
        return False
    
    # Already in proper format with colon
    if ':' in perf:
        return False
    
    # Check if it's a numeric value that looks like seconds
    try:
        val = float(perf)
        # Times between 60 and 1800 seconds (1 min to 30 min) are likely middle distance
        # stored incorrectly in seconds format
        return 60 <= val <= 1800
    except:
        return False


def fix_time_formats():
    """Find and fix all middle/long distance times in seconds format."""
    
    # Events that should have M:SS.cc format
    events = supabase.table('events').select('id, code, name').in_(
        'code', ['600m', '800m', '1000m', '1500m', '1mile', '2000m', '3000m', '5000m', '10000m']
    ).execute()
    
    event_map = {e['id']: e for e in events.data}
    event_ids = list(event_map.keys())
    
    print(f"Checking events: {[e['name'] for e in events.data]}")
    
    # Get all results for these events with pagination
    all_results = []
    batch_size = 1000

    for event_id in event_ids:
        event_name = event_map[event_id]['name']
        offset = 0
        while True:
            results = supabase.table('results').select(
                'id, performance, performance_value, athlete_id, event_id'
            ).eq('event_id', event_id).range(offset, offset + batch_size - 1).execute()

            if not results.data:
                break

            all_results.extend(results.data)
            print(f"  Fetched {len(results.data)} {event_name} results (offset {offset})")

            if len(results.data) < batch_size:
                break
            offset += batch_size

    print(f"\nTotal results to check: {len(all_results)}")
    
    to_fix = []
    for r in all_results:
        if is_seconds_format(r['performance']):
            new_format = seconds_to_time_format(r['performance'])
            if new_format:
                to_fix.append({
                    'id': r['id'],
                    'old': r['performance'],
                    'new': new_format,
                    'event_id': r['event_id']
                })
    
    print(f"Results to convert: {len(to_fix)}")
    
    # Group by event for reporting
    by_event = {}
    for f in to_fix:
        event_name = event_map[f['event_id']]['name']
        if event_name not in by_event:
            by_event[event_name] = []
        by_event[event_name].append(f)
    
    for event_name, fixes in by_event.items():
        print(f"\n{event_name}: {len(fixes)} results")
        for f in fixes[:5]:  # Show first 5
            print(f"  {f['old']} -> {f['new']}")
        if len(fixes) > 5:
            print(f"  ... and {len(fixes)-5} more")
    
    if not DRY_RUN:
        fixed_count = 0
        total = len(to_fix)
        for i, f in enumerate(to_fix):
            try:
                supabase.table('results').update({
                    'performance': f['new']
                }).eq('id', f['id']).execute()
                fixed_count += 1
                if fixed_count % 500 == 0:
                    print(f"  Progress: {fixed_count}/{total} ({100*fixed_count/total:.1f}%)")
            except Exception as e:
                print(f"  Error fixing {f['id']}: {e}")
        return fixed_count
    
    return len(to_fix)


if __name__ == '__main__':
    print("=" * 60)
    print("FIXING TIME FORMAT (SECONDS -> M:SS.CC)")
    print("=" * 60)
    
    if DRY_RUN:
        print("*** DRY RUN - ingen endringer vil bli gjort ***")
        print("Sett DRY_RUN = False for a faktisk oppdatere\n")
    
    fixed = fix_time_formats()
    
    print(f"\n{'='*60}")
    print(f"TOTALT: {fixed} resultater {'vil bli oppdatert' if DRY_RUN else 'oppdatert'}")
    print("=" * 60)
    
    if DRY_RUN:
        print("\nFor a faktisk oppdatere, endre DRY_RUN = False i scriptet")
