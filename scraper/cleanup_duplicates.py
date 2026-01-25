"""
Cleanup duplicate results created by the import.

The import created new meets without city prefix ("Norgeslekene") when
meets with city prefix already existed ("Jessheim, Norgeslekene").

This script:
1. Finds meets without city prefix that have a matching city-prefixed meet
2. Updates all results from the short-name meet to point to the prefixed meet
3. Deletes the now-empty short-name meets
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def extract_short_name(full_name):
    """Extract short name from 'City, Meet Name' format."""
    if not full_name:
        return None
    if ', ' in full_name:
        return full_name.split(', ', 1)[1].strip()
    return full_name.strip()


def main():
    # Step 1: Load all meets
    logger.info("Loading all meets...")
    all_meets = []
    offset = 0
    batch_size = 1000

    while True:
        resp = supabase.table('meets').select('id, name, start_date').range(offset, offset + batch_size - 1).execute()
        if not resp.data:
            break
        all_meets.extend(resp.data)
        offset += batch_size
        if len(resp.data) < batch_size:
            break

    logger.info(f"Loaded {len(all_meets)} meets")

    # Build lookup: (short_name, date) -> list of meet_ids with that short name
    # and (full_name, date) -> meet_id for full names
    short_to_meets = {}  # (short_name, date) -> [(meet_id, full_name), ...]

    for m in all_meets:
        name = m['name']
        date = m['start_date']
        meet_id = m['id']

        # Get the short name
        short_name = extract_short_name(name)

        key = (short_name, date)
        if key not in short_to_meets:
            short_to_meets[key] = []
        short_to_meets[key].append((meet_id, name))

    # Step 2: Find duplicate pairs where we have both a short name and a prefixed name
    # We want to keep the prefixed one and merge results from the short one
    to_merge = []  # [(short_meet_id, prefixed_meet_id), ...]

    for (short_name, date), meets in short_to_meets.items():
        if len(meets) < 2:
            continue

        # Separate into prefixed and non-prefixed
        prefixed = [(mid, name) for mid, name in meets if ', ' in name]
        non_prefixed = [(mid, name) for mid, name in meets if ', ' not in name]

        if prefixed and non_prefixed:
            # We have both - merge non-prefixed into prefixed
            prefixed_id = prefixed[0][0]  # Take first prefixed meet
            for non_prefixed_id, _ in non_prefixed:
                to_merge.append((non_prefixed_id, prefixed_id))

    logger.info(f"Found {len(to_merge)} meets to merge")

    if not to_merge:
        logger.info("No duplicates to merge!")
        return

    # Step 3: For each pair, update results and delete the short-name meet
    merged = 0
    results_moved = 0

    for short_meet_id, prefixed_meet_id in tqdm(to_merge, desc="Merging"):
        try:
            # Get results from the short-name meet
            resp = supabase.table('results').select('id').eq('meet_id', short_meet_id).execute()
            result_ids = [r['id'] for r in resp.data]

            if result_ids:
                # Update results to point to prefixed meet
                # Do in batches
                batch_size = 500
                for i in range(0, len(result_ids), batch_size):
                    batch = result_ids[i:i+batch_size]
                    supabase.table('results').update({'meet_id': prefixed_meet_id}).in_('id', batch).execute()
                results_moved += len(result_ids)

            # Delete the short-name meet
            supabase.table('meets').delete().eq('id', short_meet_id).execute()
            merged += 1

        except Exception as e:
            logger.error(f"Error merging {short_meet_id} -> {prefixed_meet_id}: {e}")

    logger.info(f"Merged {merged} meets, moved {results_moved} results")

    # Final count
    resp = supabase.table('results').select('id', count='exact').execute()
    logger.info(f"Final result count: {resp.count}")


if __name__ == "__main__":
    main()
