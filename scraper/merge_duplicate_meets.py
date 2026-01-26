"""
Merge duplicate meets in the database.
Keeps the meet with more results and moves results from duplicates to it.
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def normalize_name(name):
    '''Normalize meet name for comparison'''
    # Remove location prefix (e.g., 'Lubbock/TX/USA, ' or 'Aarhus/DEN, ')
    if ', ' in name:
        parts = name.split(', ', 1)
        # Check if first part looks like a location (contains / or is short city name)
        if '/' in parts[0] or len(parts[0]) < 20:
            name = parts[1]
    return name.lower().strip()


def main():
    # Get all meets from Nov 2025 onwards
    meets = supabase.table('meets').select(
        'id, name, city, start_date'
    ).gte('start_date', '2025-11-01').order('start_date').execute()

    print(f'Total meets from Nov 2025: {len(meets.data)}')

    # Group by date
    by_date = defaultdict(list)
    for m in meets.data:
        by_date[m['start_date']].append(m)

    # Find duplicates and merge them
    merged_count = 0
    deleted_meets = 0

    for date, meet_list in by_date.items():
        if len(meet_list) < 2:
            continue

        # Group by normalized name
        by_norm_name = defaultdict(list)
        for m in meet_list:
            norm = normalize_name(m['name'])
            by_norm_name[norm].append(m)

        # For each group with duplicates
        for norm_name, dups in by_norm_name.items():
            if len(dups) < 2:
                continue

            # Get result counts for each
            meets_with_counts = []
            for m in dups:
                count = supabase.table('results').select('id', count='exact').eq('meet_id', m['id']).execute()
                meets_with_counts.append((m, count.count or 0))

            # Sort by result count (descending) - keep the one with most results
            meets_with_counts.sort(key=lambda x: x[1], reverse=True)

            keep_meet = meets_with_counts[0][0]
            keep_count = meets_with_counts[0][1]

            # Merge others into the keeper
            for m, count in meets_with_counts[1:]:
                if count > 0:
                    # Move results to the keeper
                    print(f"Moving {count} results from '{m['name']}' to '{keep_meet['name']}' ({date})")

                    # Update results to point to the keeper meet
                    supabase.table('results').update({
                        'meet_id': keep_meet['id']
                    }).eq('meet_id', m['id']).execute()

                    merged_count += count

                # Delete the duplicate meet
                print(f"Deleting duplicate meet: '{m['name']}' ({date})")
                supabase.table('meets').delete().eq('id', m['id']).execute()
                deleted_meets += 1

    print()
    print('=' * 60)
    print(f'Merged {merged_count} results')
    print(f'Deleted {deleted_meets} duplicate meets')

    # Verify remaining meets
    remaining = supabase.table('meets').select('id', count='exact').gte('start_date', '2025-11-01').execute()
    print(f'Remaining meets from Nov 2025: {remaining.count}')


if __name__ == '__main__':
    main()
