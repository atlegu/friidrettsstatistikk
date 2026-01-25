"""
Efficient cleanup of same-meet duplicate results with rate limiting.
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


def cleanup_athlete_duplicates(athlete_id, max_retries=3):
    """Remove duplicates for a single athlete with retry logic."""
    for attempt in range(max_retries):
        try:
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
                    to_delete.append(r['id'])
                else:
                    seen[key] = r['id']

            if to_delete:
                batch_size = 50  # Smaller batches
                for i in range(0, len(to_delete), batch_size):
                    batch = to_delete[i:i+batch_size]
                    supabase.table('results').delete().in_('id', batch).execute()
                    time.sleep(0.1)  # Small delay between batches

            return len(to_delete)
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Retry {attempt + 1} for athlete {athlete_id}: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed after {max_retries} attempts for athlete {athlete_id}: {e}")
                return 0
    return 0


def main():
    logger.info("Starting duplicate cleanup with rate limiting...")

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

    for i, athlete_id in enumerate(tqdm(all_athletes, desc="Processing athletes")):
        deleted = cleanup_athlete_duplicates(athlete_id)
        if deleted > 0:
            total_deleted += deleted
            athletes_with_dupes += 1

        # Rate limiting: small delay every 10 athletes
        if i % 10 == 0:
            time.sleep(0.05)

        # Progress logging every 500 athletes
        if (i + 1) % 500 == 0:
            logger.info(f"Progress: {i + 1}/{len(all_athletes)} athletes, deleted {total_deleted} duplicates")

    logger.info(f"Cleanup complete. Deleted {total_deleted} duplicates from {athletes_with_dupes} athletes")

    # Get final count
    resp = supabase.table('results').select('id', count='exact').limit(1).execute()
    logger.info(f"Final result count: {resp.count}")


if __name__ == "__main__":
    main()
