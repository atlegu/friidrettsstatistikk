"""
Fix missing gender for athletes using multiple strategies:

1. Gender-specific events (100m hurdles = Women, 110m hurdles = Men, etc.)
2. Inference by association (if athlete A competed in same event/meet as
   known-gender athlete B, they're likely the same gender)
"""

import os
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def get_all_athletes_with_missing_gender():
    """Get all athletes with missing gender, paginated"""
    all_athletes = []
    offset = 0

    while True:
        result = supabase.table('athletes').select(
            'id'
        ).is_('gender', 'null').range(offset, offset + 999).execute()

        if not result.data:
            break

        all_athletes.extend([a['id'] for a in result.data])

        if len(result.data) < 1000:
            break

        offset += 1000

    return all_athletes


def fix_by_gender_specific_events(athlete_ids):
    """Fix gender based on gender-specific events"""
    # Get event IDs for gender-specific events
    events = supabase.table('events').select('id, name').execute()

    female_events = []
    male_events = []

    for e in events.data:
        name = e['name']
        if name.startswith('100 meter hekk') or name == '7-kamp':
            female_events.append(e['id'])
        elif name.startswith('110 meter hekk') or name == '10-kamp':
            male_events.append(e['id'])

    print(f"  Female-only events: {len(female_events)}")
    print(f"  Male-only events: {len(male_events)}")

    fixed = []
    remaining = []

    for i, athlete_id in enumerate(athlete_ids):
        # Check female events
        female_results = supabase.table('results').select(
            'id'
        ).eq('athlete_id', athlete_id).in_(
            'event_id', female_events
        ).limit(1).execute()

        if female_results.data:
            supabase.table('athletes').update({'gender': 'F'}).eq('id', athlete_id).execute()
            fixed.append(athlete_id)
            continue

        # Check male events
        male_results = supabase.table('results').select(
            'id'
        ).eq('athlete_id', athlete_id).in_(
            'event_id', male_events
        ).limit(1).execute()

        if male_results.data:
            supabase.table('athletes').update({'gender': 'M'}).eq('id', athlete_id).execute()
            fixed.append(athlete_id)
            continue

        remaining.append(athlete_id)

        if (i + 1) % 500 == 0:
            print(f"    Processed {i + 1}/{len(athlete_ids)}...")

    return fixed, remaining


def fix_by_association(athlete_ids):
    """
    Fix gender by finding athletes who competed together.
    If athlete A with unknown gender competed in the same event at the
    same meet as athlete B with known gender, A is likely the same gender.
    """
    fixed = []
    remaining = []

    # Build a lookup of meet+event combinations for unknown athletes
    print("  Building athlete result index...")

    athlete_results = {}
    for i, athlete_id in enumerate(athlete_ids):
        # Get this athlete's results
        results = supabase.table('results').select(
            'meet_id, event_id'
        ).eq('athlete_id', athlete_id).limit(50).execute()

        if results.data:
            athlete_results[athlete_id] = [
                (r['meet_id'], r['event_id']) for r in results.data
            ]

        if (i + 1) % 500 == 0:
            print(f"    Indexed {i + 1}/{len(athlete_ids)} athletes...")

    print(f"  Found {len(athlete_results)} athletes with results")

    # For each unknown athlete, find co-competitors with known gender
    print("  Inferring gender from co-competitors...")

    for i, (athlete_id, competitions) in enumerate(athlete_results.items()):
        inferred_gender = None

        for meet_id, event_id in competitions:
            if inferred_gender:
                break

            # Find other athletes in this event at this meet with known gender
            cocompetitors = supabase.table('results_full').select(
                'athlete_id, gender'
            ).eq('meet_id', meet_id).eq('event_id', event_id).neq(
                'athlete_id', athlete_id
            ).not_.is_('gender', 'null').limit(5).execute()

            if cocompetitors.data:
                # Check if all co-competitors have the same gender
                genders = set(c['gender'] for c in cocompetitors.data if c['gender'])
                if len(genders) == 1:
                    inferred_gender = genders.pop()

        if inferred_gender:
            supabase.table('athletes').update({'gender': inferred_gender}).eq('id', athlete_id).execute()
            fixed.append(athlete_id)
        else:
            remaining.append(athlete_id)

        if (i + 1) % 200 == 0:
            print(f"    Processed {i + 1}/{len(athlete_results)}, fixed {len(fixed)}...")

    # Add athletes with no results to remaining
    for athlete_id in athlete_ids:
        if athlete_id not in athlete_results and athlete_id not in fixed:
            remaining.append(athlete_id)

    return fixed, remaining


def main():
    print("=" * 60)
    print("Fixing missing gender for athletes")
    print("=" * 60)
    print()

    # Get all athletes with missing gender
    print("Getting athletes with missing gender...")
    missing_athletes = get_all_athletes_with_missing_gender()
    print(f"Found {len(missing_athletes)} athletes with missing gender")
    print()

    # Strategy 1: Gender-specific events
    print("Strategy 1: Gender-specific events...")
    fixed1, remaining1 = fix_by_gender_specific_events(missing_athletes)
    print(f"  Fixed: {len(fixed1)}")
    print(f"  Remaining: {len(remaining1)}")
    print()

    # Strategy 2: Inference by association
    if remaining1:
        print("Strategy 2: Inference by association...")
        fixed2, remaining2 = fix_by_association(remaining1)
        print(f"  Fixed: {len(fixed2)}")
        print(f"  Remaining: {len(remaining2)}")
        print()
    else:
        fixed2 = []
        remaining2 = []

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total athletes with missing gender: {len(missing_athletes)}")
    print(f"Fixed by gender-specific events: {len(fixed1)}")
    print(f"Fixed by association: {len(fixed2)}")
    print(f"Total fixed: {len(fixed1) + len(fixed2)}")
    print(f"Could not determine: {len(remaining2)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
