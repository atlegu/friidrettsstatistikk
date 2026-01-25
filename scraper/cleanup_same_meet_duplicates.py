"""
Cleanup same-meet duplicate results.

These are results where the same athlete, event, meet, date, and performance
exist multiple times (likely with different round/heat_number values from
duplicate imports).

This script keeps one result per unique (athlete_id, event_id, meet_id, date, performance)
and deletes the rest.
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def main():
    logger.info("Finding same-meet duplicates...")

    total_deleted = 0
    batch_num = 0

    while True:
        batch_num += 1

        # Find duplicates - get the IDs to delete (keep the one with smaller id)
        # We need to do this in raw SQL since Supabase Python doesn't support complex queries well
        # Instead, let's fetch batches of potential duplicates and process them

        # Get a batch of results grouped by (athlete_id, event_id, meet_id, date, performance)
        # where count > 1
        resp = supabase.rpc('get_duplicate_result_ids', {'batch_limit': 10000}).execute()

        if not resp.data or len(resp.data) == 0:
            logger.info("No more duplicates found")
            break

        ids_to_delete = [r['id'] for r in resp.data]

        if not ids_to_delete:
            break

        logger.info(f"Batch {batch_num}: Deleting {len(ids_to_delete)} duplicate results...")

        # Delete in smaller batches
        batch_size = 500
        for i in range(0, len(ids_to_delete), batch_size):
            batch = ids_to_delete[i:i+batch_size]
            try:
                supabase.table('results').delete().in_('id', batch).execute()
                total_deleted += len(batch)
            except Exception as e:
                logger.error(f"Error deleting batch: {e}")

        logger.info(f"Total deleted so far: {total_deleted}")

    logger.info(f"Cleanup complete. Total deleted: {total_deleted}")

    # Get final count
    resp = supabase.table('results').select('id', count='exact').execute()
    logger.info(f"Final result count: {resp.count}")


if __name__ == "__main__":
    main()
