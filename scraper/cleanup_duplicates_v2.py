"""
Efficient cleanup of same-meet duplicate results.

Uses a chunked approach that won't time out:
1. Process athletes in batches
2. For each athlete, find and remove duplicates
3. Smaller queries that complete quickly
"""

import os
import time
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


def get_athletes_with_duplicates(limit=1000, offset=0):
    """Get athletes who have duplicate results."""
    query = """
    SELECT DISTINCT r1.athlete_id
    FROM results r1
    JOIN results r2 ON r1.athlete_id = r2.athlete_id
        AND r1.event_id = r2.event_id
        AND r1.meet_id = r2.meet_id
        AND r1.date = r2.date
        AND r1.performance = r2.performance
        AND r1.id < r2.id
    LIMIT %s OFFSET %s
    """ % (limit, offset)

    resp = supabase.rpc('exec_sql', {'query': query}).execute()
    return resp.data if resp.data else []


def cleanup_athlete_duplicates(athlete_id):
    """Remove duplicates for a single athlete."""
    # Get all results for this athlete with duplicate info
    resp = supabase.table('results').select(
        'id, athlete_id, event_id, meet_id, date, performance'
    ).eq('athlete_id', athlete_id).execute()

    if not resp.data:
        return 0

    # Group by (event_id, meet_id, date, performance) and find duplicates
    seen = {}
    to_delete = []

    for r in resp.data:
        key = (r['event_id'], r['meet_id'], r['date'], r['performance'])
        if key in seen:
            # This is a duplicate - mark for deletion
            to_delete.append(r['id'])
        else:
            seen[key] = r['id']

    if to_delete:
        # Delete in batches
        batch_size = 100
        for i in range(0, len(to_delete), batch_size):
            batch = to_delete[i:i+batch_size]
            try:
                supabase.table('results').delete().in_('id', batch).execute()
            except Exception as e:
                logger.error(f"Error deleting batch for athlete {athlete_id}: {e}")

    return len(to_delete)


def main():
    logger.info("Starting efficient duplicate cleanup...")

    # Get all athlete IDs
    logger.info("Loading all athlete IDs...")
    all_athletes = []
    offset = 0
    batch_size = 1000

    while True:
        resp = supabase.table('athletes').select('id').range(offset, offset + batch_size - 1).execute()
        if not resp.data:
            break
        all_athletes.extend([a['id'] for a in resp.data])
        offset += batch_size
        if len(resp.data) < batch_size:
            break

    logger.info(f"Found {len(all_athletes)} athletes")

    total_deleted = 0
    athletes_with_dupes = 0

    for athlete_id in tqdm(all_athletes, desc="Processing athletes"):
        deleted = cleanup_athlete_duplicates(athlete_id)
        if deleted > 0:
            total_deleted += deleted
            athletes_with_dupes += 1
            if athletes_with_dupes % 100 == 0:
                logger.info(f"Processed {athletes_with_dupes} athletes with duplicates, deleted {total_deleted} total")

    logger.info(f"Cleanup complete. Deleted {total_deleted} duplicates from {athletes_with_dupes} athletes")

    # Get final count
    resp = supabase.table('results').select('id', count='exact').execute()
    logger.info(f"Final result count: {resp.count}")


if __name__ == "__main__":
    main()
