"""
Fix script: Add weight-specific events and re-import throw results.
This script:
1. Adds weight-specific events to the database
2. Deletes existing results with generic throw event codes
3. The user should then run fast_import.py to re-import
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

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def add_weight_events():
    """Add weight-specific events to the database."""
    logger.info("Adding weight-specific events...")

    # Note: column is 'category' not 'event_category'
    events_to_add = [
        # Shot put (Kule)
        {'code': 'kule_2kg', 'name': 'Kule 2,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 201},
        {'code': 'kule_3kg', 'name': 'Kule 3,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 202},
        {'code': 'kule_4kg', 'name': 'Kule 4,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 203},
        {'code': 'kule_5kg', 'name': 'Kule 5,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 204},
        {'code': 'kule_6kg', 'name': 'Kule 6,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 205},
        {'code': 'kule_7_26kg', 'name': 'Kule 7,26kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 206},
        # Discus
        {'code': 'diskos_600g', 'name': 'Diskos 600gram', 'result_type': 'distance', 'category': 'throw', 'sort_order': 211},
        {'code': 'diskos_750g', 'name': 'Diskos 750gram', 'result_type': 'distance', 'category': 'throw', 'sort_order': 212},
        {'code': 'diskos_1kg', 'name': 'Diskos 1,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 213},
        {'code': 'diskos_1_5kg', 'name': 'Diskos 1,5kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 214},
        {'code': 'diskos_1_75kg', 'name': 'Diskos 1,75kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 215},
        {'code': 'diskos_2kg', 'name': 'Diskos 2,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 216},
        # Hammer (Slegge)
        {'code': 'slegge_2kg', 'name': 'Slegge 2,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 221},
        {'code': 'slegge_3kg', 'name': 'Slegge 3,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 222},
        {'code': 'slegge_4kg', 'name': 'Slegge 4,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 223},
        {'code': 'slegge_5kg', 'name': 'Slegge 5,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 224},
        {'code': 'slegge_6kg', 'name': 'Slegge 6,0kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 225},
        {'code': 'slegge_7_26kg', 'name': 'Slegge 7,26kg', 'result_type': 'distance', 'category': 'throw', 'sort_order': 226},
        # Javelin (Spyd)
        {'code': 'spyd_400g', 'name': 'Spyd 400gram', 'result_type': 'distance', 'category': 'throw', 'sort_order': 231},
        {'code': 'spyd_500g', 'name': 'Spyd 500gram', 'result_type': 'distance', 'category': 'throw', 'sort_order': 232},
        {'code': 'spyd_600g', 'name': 'Spyd 600gram', 'result_type': 'distance', 'category': 'throw', 'sort_order': 233},
        {'code': 'spyd_700g', 'name': 'Spyd 700gram', 'result_type': 'distance', 'category': 'throw', 'sort_order': 234},
        {'code': 'spyd_800g', 'name': 'Spyd 800gram', 'result_type': 'distance', 'category': 'throw', 'sort_order': 235},
    ]

    added = 0
    skipped = 0

    for event in events_to_add:
        try:
            # Check if event already exists
            existing = supabase.table('events').select('id').eq('code', event['code']).execute()
            if existing.data:
                logger.info(f"  Event {event['code']} already exists, skipping")
                skipped += 1
                continue

            # Insert new event
            supabase.table('events').insert(event).execute()
            logger.info(f"  Added event: {event['code']} ({event['name']})")
            added += 1
        except Exception as e:
            logger.error(f"  Error adding event {event['code']}: {e}")

    logger.info(f"Events added: {added}, skipped (already exist): {skipped}")
    return added


def delete_generic_throw_results():
    """Delete results that use generic throw event codes."""
    logger.info("Finding generic throw events...")

    # Find the event IDs for generic throw events
    generic_codes = ['kule', 'diskos', 'slegge', 'spyd']

    resp = supabase.table('events').select('id, code').in_('code', generic_codes).execute()
    events_found = {e['code']: e['id'] for e in resp.data}

    if not events_found:
        logger.info("No generic throw events found in database")
        return 0

    logger.info(f"Found {len(events_found)} generic throw events: {list(events_found.keys())}")

    # Delete results for each event type separately to avoid URL length issues
    total_deleted = 0

    for event_code, event_id in events_found.items():
        # Count results for this event
        count_resp = supabase.table('results').select('id', count='exact').eq('event_id', event_id).execute()
        event_count = count_resp.count or 0

        if event_count == 0:
            logger.info(f"  No results for {event_code}")
            continue

        logger.info(f"  Deleting {event_count} results for {event_code}...")

        # Delete in small batches using eq() instead of in_()
        deleted_for_event = 0
        batch_size = 100

        while deleted_for_event < event_count:
            # Get a batch of result IDs
            batch_resp = supabase.table('results').select('id').eq('event_id', event_id).limit(batch_size).execute()

            if not batch_resp.data:
                break

            # Delete one by one to avoid URL issues
            for result in batch_resp.data:
                try:
                    supabase.table('results').delete().eq('id', result['id']).execute()
                    deleted_for_event += 1
                except Exception as e:
                    logger.warning(f"    Error deleting result {result['id']}: {e}")

            logger.info(f"    Deleted {deleted_for_event}/{event_count} for {event_code}...")

        total_deleted += deleted_for_event
        logger.info(f"  Completed {event_code}: {deleted_for_event} deleted")

    logger.info(f"Total deleted: {total_deleted} results")
    return total_deleted


def main():
    logger.info("=" * 60)
    logger.info("FIX WEIGHT EVENTS SCRIPT")
    logger.info("=" * 60)

    # Step 1: Add weight-specific events
    logger.info("\n--- Step 1: Adding weight-specific events ---")
    added = add_weight_events()

    # Step 2: Delete generic throw results
    logger.info("\n--- Step 2: Deleting results with generic throw events ---")
    deleted = delete_generic_throw_results()

    logger.info("\n" + "=" * 60)
    logger.info("DONE!")
    logger.info(f"  - Events added: {added}")
    logger.info(f"  - Results deleted: {deleted}")
    logger.info("")
    logger.info("Next step: Run 'python fast_import.py' to re-import the data")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
