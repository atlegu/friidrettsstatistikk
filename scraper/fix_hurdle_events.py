"""
Fix script: Add height-specific hurdle events and re-import hurdle results.
This script:
1. Adds height-specific hurdle events to the database
2. Deletes existing results with generic hurdle event codes
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


def add_hurdle_events():
    """Add height-specific hurdle events to the database."""
    logger.info("Adding height-specific hurdle events...")

    events_to_add = [
        # 30 meter hekk
        {'code': '30mh_84cm', 'name': '30 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 291},
        # 40 meter hekk
        {'code': '40mh_76_2cm', 'name': '40 meter hekk (76,2cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 301},
        {'code': '40mh_84cm', 'name': '40 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 302},
        {'code': '40mh_91_4cm', 'name': '40 meter hekk (91,4cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 303},
        {'code': '40mh_100cm', 'name': '40 meter hekk (100cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 304},
        # 55 meter hekk
        {'code': '55mh_84cm', 'name': '55 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 306},

        # 60 meter hekk (indoor)
        {'code': '60mh_60cm', 'name': '60 meter hekk (60cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 311},
        {'code': '60mh_68cm', 'name': '60 meter hekk (68,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 312},
        {'code': '60mh_76_2cm', 'name': '60 meter hekk (76,2cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 313},
        {'code': '60mh_84cm', 'name': '60 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 314},
        {'code': '60mh_91_4cm', 'name': '60 meter hekk (91,4cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 315},
        {'code': '60mh_100cm', 'name': '60 meter hekk (100cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 316},
        {'code': '60mh_106_7cm', 'name': '60 meter hekk (106,7cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 317},

        # 80 meter hekk
        {'code': '80mh_68cm', 'name': '80 meter hekk (68,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 321},
        {'code': '80mh_76_2cm', 'name': '80 meter hekk (76,2cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 322},
        {'code': '80mh_84cm', 'name': '80 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 323},
        {'code': '80mh_91_4cm', 'name': '80 meter hekk (91,4cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 324},

        # 100 meter hekk
        {'code': '100mh_76_2cm', 'name': '100 meter hekk (76,2cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 330},
        {'code': '100mh_84cm', 'name': '100 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 331},
        {'code': '100mh_91_4cm', 'name': '100 meter hekk (91,4cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 332},

        # 110 meter hekk
        {'code': '110mh_91_4cm', 'name': '110 meter hekk (91,4cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 341},
        {'code': '110mh_100cm', 'name': '110 meter hekk (100cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 342},
        {'code': '110mh_106_7cm', 'name': '110 meter hekk (106,7cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 343},

        # 200 meter hekk
        {'code': '200mh_68cm', 'name': '200 meter hekk (68,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 351},
        {'code': '200mh_76_2cm', 'name': '200 meter hekk (76,2cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 352},

        # 300 meter hekk
        {'code': '300mh_68cm', 'name': '300 meter hekk (68,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 361},
        {'code': '300mh_76_2cm', 'name': '300 meter hekk (76,2cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 362},
        {'code': '300mh_84cm', 'name': '300 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 363},
        {'code': '300mh_91_4cm', 'name': '300 meter hekk (91,4cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 364},

        # 400 meter hekk
        {'code': '400mh_68cm', 'name': '400 meter hekk (68,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 370},
        {'code': '400mh_76_2cm', 'name': '400 meter hekk (76,2cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 371},
        {'code': '400mh_84cm', 'name': '400 meter hekk (84,0cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 372},
        {'code': '400mh_91_4cm', 'name': '400 meter hekk (91,4cm)', 'result_type': 'time', 'category': 'hurdles', 'sort_order': 373},

        # Steeplechase (hinder)
        {'code': '1500mhinder_76_2cm', 'name': '1500 meter hinder (76,2cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 381},
        {'code': '1500mhinder_91_4cm', 'name': '1500 meter hinder (91,4cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 382},
        {'code': '2000mhinder_76_2cm', 'name': '2000 meter hinder (76,2cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 391},
        {'code': '2000mhinder_84cm', 'name': '2000 meter hinder (84,0cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 392},
        {'code': '2000mhinder_91_4cm', 'name': '2000 meter hinder (91,4cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 393},
        {'code': '3000mhinder_76_2cm', 'name': '3000 meter hinder (76,2cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 401},
        {'code': '3000mhinder_84cm', 'name': '3000 meter hinder (84,0cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 402},
        {'code': '3000mhinder_91_4cm', 'name': '3000 meter hinder (91,4cm)', 'result_type': 'time', 'category': 'steeplechase', 'sort_order': 403},
    ]

    added = 0
    skipped = 0

    for event in events_to_add:
        try:
            existing = supabase.table('events').select('id').eq('code', event['code']).execute()
            if existing.data:
                logger.info(f"  Event {event['code']} already exists, skipping")
                skipped += 1
                continue

            supabase.table('events').insert(event).execute()
            logger.info(f"  Added event: {event['code']} ({event['name']})")
            added += 1
        except Exception as e:
            logger.error(f"  Error adding event {event['code']}: {e}")

    logger.info(f"Events added: {added}, skipped (already exist): {skipped}")
    return added


def delete_generic_hurdle_results():
    """Delete results using bulk delete by event_id directly."""
    logger.info("Deleting results with generic hurdle event codes...")

    # Generic hurdle codes that will be replaced by height-specific ones
    generic_codes = ['40mh', '60mh', '80mh', '100mh', '110mh', '200mh', '300mh', '400mh',
                     '1500mhinder', '2000mhinder', '3000mhinder']

    resp = supabase.table('events').select('id, code').in_('code', generic_codes).execute()
    events_found = {e['code']: e['id'] for e in resp.data}

    if not events_found:
        logger.info("No generic hurdle events found in database")
        return 0

    logger.info(f"Found {len(events_found)} generic hurdle events: {list(events_found.keys())}")

    total_deleted = 0

    for event_code, event_id in events_found.items():
        # Count results
        count_resp = supabase.table('results').select('id', count='exact').eq('event_id', event_id).execute()
        event_count = count_resp.count or 0

        if event_count == 0:
            logger.info(f"  No results for {event_code}")
            continue

        logger.info(f"  Deleting {event_count} results for {event_code}...")

        # Delete ALL results for this event_id in one go
        try:
            supabase.table('results').delete().eq('event_id', event_id).execute()
            logger.info(f"  Deleted all {event_count} results for {event_code}")
            total_deleted += event_count
        except Exception as e:
            logger.error(f"  Error deleting results for {event_code}: {e}")

    logger.info(f"Total deleted: {total_deleted} results")
    return total_deleted


def main():
    logger.info("=" * 60)
    logger.info("FIX HURDLE EVENTS SCRIPT")
    logger.info("=" * 60)

    # Step 1: Add height-specific events
    logger.info("\n--- Step 1: Adding height-specific hurdle events ---")
    added = add_hurdle_events()

    # Step 2: Delete generic hurdle results
    logger.info("\n--- Step 2: Deleting results with generic hurdle events ---")
    deleted = delete_generic_hurdle_results()

    logger.info("\n" + "=" * 60)
    logger.info("DONE!")
    logger.info(f"  - Events added: {added}")
    logger.info(f"  - Results deleted: {deleted}")
    logger.info("")
    logger.info("Next step: Run 'python fast_import.py' to re-import the data")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
