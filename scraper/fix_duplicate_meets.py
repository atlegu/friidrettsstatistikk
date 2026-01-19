"""
Fix duplicate meets in the database.
For each set of duplicates (same name, start_date), keep one and merge results.
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

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def fix_duplicates():
    """Fix duplicate meets by merging results to one and deleting others."""
    logger.info("Finding duplicate meets...")

    # Get all meets with pagination
    all_meets = []
    offset = 0
    while True:
        resp = supabase.table('meets').select('id, name, start_date, city').order('id').range(offset, offset + 999).execute()
        all_meets.extend(resp.data)
        if len(resp.data) < 1000:
            break
        offset += 1000

    logger.info(f"Total meets: {len(all_meets)}")

    # Group by (name, start_date)
    grouped = {}
    for m in all_meets:
        key = (m['name'], m['start_date'])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(m)

    # Find duplicates
    duplicates = {k: v for k, v in grouped.items() if len(v) > 1}
    logger.info(f"Found {len(duplicates)} sets of duplicate meets")

    if not duplicates:
        logger.info("No duplicates to fix!")
        return

    total_merged = 0
    total_deleted_results = 0
    total_deleted_meets = 0
    errors = 0

    for (name, date), meets in tqdm(duplicates.items(), desc="Fixing duplicates"):
        try:
            # Keep the one with the longest/most specific city name (prefer non-empty)
            # If tied, use the first ID (oldest)
            meets_sorted = sorted(meets, key=lambda x: (-len(x.get('city') or ''), x['id']))
            keeper = meets_sorted[0]
            to_delete = meets_sorted[1:]

            for old_meet in to_delete:
                old_id = old_meet['id']
                keeper_id = keeper['id']

                # Count results in old meet
                count_resp = supabase.table('results').select('id', count='exact').eq('meet_id', old_id).execute()
                result_count = count_resp.count or 0

                if result_count == 0:
                    # No results, just delete the meet
                    supabase.table('meets').delete().eq('id', old_id).execute()
                    total_deleted_meets += 1
                    continue

                # Get results from old meet in batches
                results_to_process = []
                r_offset = 0
                while True:
                    batch = supabase.table('results').select('id, athlete_id, event_id, round, heat_number').eq('meet_id', old_id).range(r_offset, r_offset + 999).execute()
                    results_to_process.extend(batch.data)
                    if len(batch.data) < 1000:
                        break
                    r_offset += 1000

                # For each result, check if it can be moved or should be deleted
                results_to_move = []
                results_to_delete = []

                for r in results_to_process:
                    # Check if this result already exists in keeper meet
                    existing = supabase.table('results').select('id').eq('meet_id', keeper_id).eq('athlete_id', r['athlete_id']).eq('event_id', r['event_id']).eq('round', r['round']).eq('heat_number', r['heat_number']).limit(1).execute()

                    if existing.data:
                        results_to_delete.append(r['id'])
                    else:
                        results_to_move.append(r['id'])

                # Delete duplicate results
                if results_to_delete:
                    # Delete in batches of 100
                    for i in range(0, len(results_to_delete), 100):
                        batch_ids = results_to_delete[i:i+100]
                        supabase.table('results').delete().in_('id', batch_ids).execute()
                    total_deleted_results += len(results_to_delete)

                # Move remaining results
                if results_to_move:
                    # Update in batches of 100
                    for i in range(0, len(results_to_move), 100):
                        batch_ids = results_to_move[i:i+100]
                        supabase.table('results').update({'meet_id': keeper_id}).in_('id', batch_ids).execute()
                    total_merged += len(results_to_move)

                # Delete the old meet
                supabase.table('meets').delete().eq('id', old_id).execute()
                total_deleted_meets += 1

        except Exception as e:
            logger.error(f"Error fixing {name} on {date}: {e}")
            errors += 1

    logger.info(f"""
    Done!
    - Duplicate meets deleted: {total_deleted_meets}
    - Results moved: {total_merged}
    - Duplicate results deleted: {total_deleted_results}
    - Errors: {errors}
    """)


if __name__ == '__main__':
    fix_duplicates()
