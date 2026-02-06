"""
Fix missing gender for athletes using batch processing.

Strategy:
1. Load all results with athlete gender info
2. Group by meet+event
3. For each group, if some athletes have known gender and some don't,
   infer gender for unknown athletes
4. Batch update athletes
"""

import os
import sys
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))


def load_all_results():
    """Load all results with athlete and gender info"""
    print("Loading results...")
    all_results = []
    offset = 0

    while True:
        result = supabase.table('results_full').select(
            'meet_id, event_id, athlete_id, gender'
        ).range(offset, offset + 999).execute()

        if not result.data:
            break

        all_results.extend(result.data)

        if len(result.data) < 1000:
            break

        offset += 1000
        if offset % 50000 == 0:
            print(f"  Loaded {offset} results...", flush=True)

    print(f"Loaded {len(all_results)} results")
    return all_results


def main():
    print("=" * 60, flush=True)
    print("Fixing missing gender using batch processing", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)

    # Load all results
    results = load_all_results()

    # Group by meet+event
    print("Grouping results by meet+event...", flush=True)
    groups = defaultdict(list)
    for r in results:
        key = (r['meet_id'], r['event_id'])
        groups[key].append((r['athlete_id'], r['gender']))

    print(f"Found {len(groups)} meet+event groups", flush=True)
    print(flush=True)

    # Find athletes to update
    print("Finding gender inferences...", flush=True)
    inferred_genders = {}  # athlete_id -> gender

    for (meet_id, event_id), athletes in groups.items():
        # Separate known and unknown gender
        known = [(aid, g) for aid, g in athletes if g is not None]
        unknown = [aid for aid, g in athletes if g is None]

        if not known or not unknown:
            continue

        # Check if all known athletes have same gender
        genders = set(g for _, g in known)
        if len(genders) != 1:
            continue  # Mixed gender event, can't infer

        inferred = genders.pop()

        for athlete_id in unknown:
            if athlete_id not in inferred_genders:
                inferred_genders[athlete_id] = inferred

    print(f"Found {len(inferred_genders)} athletes to update", flush=True)
    print(flush=True)

    if not inferred_genders:
        print("No athletes to update!")
        return

    # Update athletes in batches
    print("Updating athletes...", flush=True)
    male_ids = [aid for aid, g in inferred_genders.items() if g == 'M']
    female_ids = [aid for aid, g in inferred_genders.items() if g == 'F']

    print(f"  Male: {len(male_ids)}", flush=True)
    print(f"  Female: {len(female_ids)}", flush=True)

    # Update males in batches of 100
    batch_size = 100
    updated = 0
    for i in range(0, len(male_ids), batch_size):
        batch = male_ids[i:i + batch_size]
        supabase.table('athletes').update({'gender': 'M'}).in_('id', batch).execute()
        updated += len(batch)
        if updated % 500 == 0:
            print(f"  Updated {updated} athletes...", flush=True)

    for i in range(0, len(female_ids), batch_size):
        batch = female_ids[i:i + batch_size]
        supabase.table('athletes').update({'gender': 'F'}).in_('id', batch).execute()
        updated += len(batch)
        if updated % 500 == 0:
            print(f"  Updated {updated} athletes...", flush=True)

    print(flush=True)
    print("=" * 60, flush=True)
    print(f"Updated {len(inferred_genders)} athletes", flush=True)
    print(f"  Male: {len(male_ids)}", flush=True)
    print(f"  Female: {len(female_ids)}", flush=True)
    print("=" * 60, flush=True)


if __name__ == '__main__':
    main()
