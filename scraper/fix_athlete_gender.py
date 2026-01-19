"""
Fix athlete gender in database.
Updates athletes with NULL gender based on the men/women results files.
"""

import json
import os
from pathlib import Path
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
DATA_DIR = Path(__file__).parent / "data"


def fix_gender():
    """Update athlete gender based on the men/women result files."""
    logger.info("Loading gender data from result files...")

    # Build athlete_id -> gender mapping
    athlete_gender = {}

    men_file = DATA_DIR / 'men_results_raw.json'
    women_file = DATA_DIR / 'women_results_raw.json'

    if men_file.exists():
        with open(men_file, 'r', encoding='utf-8') as f:
            men_results = json.load(f)
            for r in men_results:
                if r.get('athlete_id'):
                    athlete_gender[str(r['athlete_id'])] = 'M'
            logger.info(f"Found {len([a for a in athlete_gender.values() if a == 'M'])} male athletes")

    if women_file.exists():
        with open(women_file, 'r', encoding='utf-8') as f:
            women_results = json.load(f)
            for r in women_results:
                if r.get('athlete_id'):
                    athlete_gender[str(r['athlete_id'])] = 'F'
            logger.info(f"Found {len([a for a in athlete_gender.values() if a == 'F'])} female athletes")

    logger.info(f"Total unique athletes with gender: {len(athlete_gender)}")

    # Get all athletes from database with their external_id
    logger.info("Fetching athletes from database...")
    all_athletes = []
    offset = 0
    batch_size = 1000
    while True:
        resp = supabase.table('athletes').select('id, external_id, gender').range(offset, offset + batch_size - 1).execute()
        all_athletes.extend(resp.data)
        if len(resp.data) < batch_size:
            break
        offset += batch_size

    logger.info(f"Found {len(all_athletes)} athletes in database")

    # Find athletes that need gender update
    updates = []
    for athlete in all_athletes:
        ext_id = athlete.get('external_id')
        current_gender = athlete.get('gender')

        if ext_id and ext_id in athlete_gender:
            new_gender = athlete_gender[ext_id]
            if current_gender != new_gender:
                updates.append({
                    'id': athlete['id'],
                    'gender': new_gender
                })

    logger.info(f"Found {len(updates)} athletes needing gender update")

    if not updates:
        logger.info("No updates needed!")
        return

    # Update in batches
    batch_size = 100
    updated = 0
    errors = 0

    for i in tqdm(range(0, len(updates), batch_size), desc="Updating gender"):
        batch = updates[i:i+batch_size]
        for athlete in batch:
            try:
                supabase.table('athletes').update({'gender': athlete['gender']}).eq('id', athlete['id']).execute()
                updated += 1
            except Exception as e:
                logger.error(f"Error updating athlete {athlete['id']}: {e}")
                errors += 1

    logger.info(f"""
    Done!
    - Athletes updated: {updated}
    - Errors: {errors}
    """)


if __name__ == '__main__':
    fix_gender()
