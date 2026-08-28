#!/usr/bin/env python3
"""
Merge duplicate athletes in the database.

Safe auto-merge: same name + same birth year.
Review list: off-by-1, century errors, missing birth year.

Usage:
    python merge_duplicate_athletes.py --dry-run          # Preview only
    python merge_duplicate_athletes.py                    # Execute safe merges
    python merge_duplicate_athletes.py --review           # Generate review CSV
    python merge_duplicate_athletes.py --review --all     # Include off-by-1 and century errors
"""

import os
import sys
import csv
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Logging setup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(f"logs/merge_duplicate_athletes_{timestamp}.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")
if not url or not key:
    logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

supabase = create_client(url, key)


def find_duplicates(category="same_year"):
    """Find duplicate athlete pairs by category."""
    if category == "same_year":
        condition = "a1.birth_year = a2.birth_year"
    elif category == "off_by_1":
        condition = "ABS(a1.birth_year - a2.birth_year) = 1"
    elif category == "century_error":
        condition = "ABS(a1.birth_year - a2.birth_year) = 100"
    elif category == "one_missing":
        condition = "(a1.birth_year IS NULL OR a2.birth_year IS NULL) AND NOT (a1.birth_year IS NULL AND a2.birth_year IS NULL)"
    else:
        raise ValueError(f"Unknown category: {category}")

    query = f"""
    SELECT
        a1.id as id1, a2.id as id2,
        a1.first_name as first1, a1.last_name as last1,
        a1.full_name as full_name1, a1.birth_year as by1,
        a1.gender as gender1, a1.external_id as ext1,
        a2.first_name as first2, a2.last_name as last2,
        a2.full_name as full_name2, a2.birth_year as by2,
        a2.gender as gender2, a2.external_id as ext2,
        (SELECT count(*) FROM results WHERE athlete_id = a1.id) as results1,
        (SELECT count(*) FROM results WHERE athlete_id = a2.id) as results2,
        (SELECT count(*) FROM championship_medals WHERE athlete_id = a1.id) as medals1,
        (SELECT count(*) FROM championship_medals WHERE athlete_id = a2.id) as medals2
    FROM athletes a1
    JOIN athletes a2 ON a1.id < a2.id
        AND LOWER(TRIM(a1.first_name)) = LOWER(TRIM(a2.first_name))
        AND LOWER(TRIM(a1.last_name)) = LOWER(TRIM(a2.last_name))
        AND {condition}
    ORDER BY a1.last_name, a1.first_name
    """

    result = supabase.rpc("exec_sql", {"query": query}).execute()
    # Use postgrest directly
    response = supabase.postgrest.rpc("exec_sql", {"query": query}).execute()
    return response.data


def find_duplicates_direct(category="same_year"):
    """Find duplicate athlete pairs using direct SQL via REST."""

    if category == "same_year":
        where_extra = "AND a1.birth_year = a2.birth_year AND a1.birth_year IS NOT NULL"
    elif category == "off_by_1":
        where_extra = "AND ABS(a1.birth_year - a2.birth_year) = 1"
    elif category == "century_error":
        where_extra = "AND ABS(a1.birth_year - a2.birth_year) = 100"
    elif category == "one_missing":
        where_extra = "AND ((a1.birth_year IS NULL AND a2.birth_year IS NOT NULL) OR (a1.birth_year IS NOT NULL AND a2.birth_year IS NULL))"
    else:
        raise ValueError(f"Unknown category: {category}")

    # Get all athletes
    logger.info(f"Fetching athletes for category: {category}")

    # Fetch all athletes in batches
    all_athletes = []
    page_size = 1000
    offset = 0
    while True:
        resp = supabase.table("athletes").select(
            "id, first_name, last_name, full_name, birth_year, gender, external_id, current_club_id"
        ).range(offset, offset + page_size - 1).execute()
        if not resp.data:
            break
        all_athletes.extend(resp.data)
        if len(resp.data) < page_size:
            break
        offset += page_size

    logger.info(f"Loaded {len(all_athletes)} athletes")

    # Build name index
    name_groups = {}
    for a in all_athletes:
        key = (
            (a["first_name"] or "").strip().lower(),
            (a["last_name"] or "").strip().lower()
        )
        if key not in name_groups:
            name_groups[key] = []
        name_groups[key].append(a)

    # Find pairs
    pairs = []
    for key, group in name_groups.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a1, a2 = group[i], group[j]
                by1 = a1["birth_year"]
                by2 = a2["birth_year"]

                if category == "same_year":
                    if by1 is not None and by2 is not None and by1 == by2:
                        pairs.append((a1, a2))
                elif category == "off_by_1":
                    if by1 is not None and by2 is not None and abs(by1 - by2) == 1:
                        pairs.append((a1, a2))
                elif category == "century_error":
                    if by1 is not None and by2 is not None and abs(by1 - by2) == 100:
                        pairs.append((a1, a2))
                elif category == "one_missing":
                    if (by1 is None) != (by2 is None):
                        pairs.append((a1, a2))

    logger.info(f"Found {len(pairs)} pairs for category: {category}")
    return pairs


def get_result_count(athlete_id):
    """Get result count for an athlete."""
    resp = supabase.table("results").select("id", count="exact").eq("athlete_id", athlete_id).execute()
    return resp.count or 0


def get_medal_count(athlete_id):
    """Get championship medal count for an athlete."""
    resp = supabase.table("championship_medals").select("id", count="exact").eq("athlete_id", athlete_id).execute()
    return resp.count or 0


def choose_target(a1, a2, results1, results2, medals1, medals2):
    """
    Choose which athlete to keep (target) and which to delete (source).
    Priority: more results > has external_id > has birth_year > has gender > has full_name
    Returns (target, source).
    """
    score1 = 0
    score2 = 0

    # More results = keep
    if results1 > results2:
        score1 += 10
    elif results2 > results1:
        score2 += 10

    # More medals = keep
    if medals1 > medals2:
        score1 += 5
    elif medals2 > medals1:
        score2 += 5

    # Has external_id = keep (linked to source data)
    if a1.get("external_id"):
        score1 += 3
    if a2.get("external_id"):
        score2 += 3

    # Has birth_year = keep
    if a1.get("birth_year"):
        score1 += 2
    if a2.get("birth_year"):
        score2 += 2

    # Has gender = keep
    if a1.get("gender"):
        score1 += 1
    if a2.get("gender"):
        score2 += 1

    # Has full_name = keep
    if a1.get("full_name"):
        score1 += 1
    if a2.get("full_name"):
        score2 += 1

    if score1 >= score2:
        return a1, a2  # a1 is target, a2 is source
    else:
        return a2, a1  # a2 is target, a1 is source


def merge_athlete(source_id, target_id, dry_run=True):
    """
    Merge source athlete into target:
    1. Transfer results
    2. Transfer championship_medals
    3. Delete source athlete (club_memberships cascade)
    """
    if dry_run:
        return True

    try:
        # 1. Transfer results
        supabase.table("results").update({
            "athlete_id": target_id,
            "updated_at": datetime.now().isoformat()
        }).eq("athlete_id", source_id).execute()

        # 2. Transfer championship medals
        supabase.table("championship_medals").update({
            "athlete_id": target_id
        }).eq("athlete_id", source_id).execute()

        # 3. Delete source athlete
        supabase.table("athletes").delete().eq("id", source_id).execute()

        return True
    except Exception as e:
        logger.error(f"Error merging {source_id} -> {target_id}: {e}")
        return False


def run_auto_merge(dry_run=True):
    """Auto-merge athletes with same name and same birth year."""
    logger.info(f"{'DRY RUN: ' if dry_run else ''}Finding same-year duplicates...")

    pairs = find_duplicates_direct("same_year")

    if not pairs:
        logger.info("No duplicates found.")
        return

    logger.info(f"Found {len(pairs)} duplicate pairs to merge")

    merged = 0
    skipped = 0
    errors = 0

    # Track already-processed IDs to avoid double-merging
    processed_ids = set()

    for a1, a2 in pairs:
        if a1["id"] in processed_ids or a2["id"] in processed_ids:
            logger.info(f"  SKIP (already processed): {a1['first_name']} {a1['last_name']}")
            skipped += 1
            continue

        results1 = get_result_count(a1["id"])
        results2 = get_result_count(a2["id"])
        medals1 = get_medal_count(a1["id"])
        medals2 = get_medal_count(a2["id"])

        target, source = choose_target(a1, a2, results1, results2, medals1, medals2)

        target_results = results1 if target["id"] == a1["id"] else results2
        source_results = results1 if source["id"] == a1["id"] else results2
        target_medals = medals1 if target["id"] == a1["id"] else medals2
        source_medals = medals1 if source["id"] == a1["id"] else medals2

        name = f"{a1['first_name']} {a1['last_name']}"
        logger.info(
            f"  {'WOULD MERGE' if dry_run else 'MERGING'}: {name} (f.{a1['birth_year']}) — "
            f"keep [{target_results} res, {target_medals} medals] ← delete [{source_results} res, {source_medals} medals]"
        )

        success = merge_athlete(source["id"], target["id"], dry_run=dry_run)
        if success:
            merged += 1
            processed_ids.add(source["id"])
            processed_ids.add(target["id"])
        else:
            errors += 1

    logger.info(f"\nSummary: {merged} merged, {skipped} skipped, {errors} errors")


def generate_review_csv(include_all=False):
    """Generate a CSV file with probable duplicates for manual review."""
    categories = ["off_by_1", "century_error", "one_missing"]
    if not include_all:
        categories = ["off_by_1", "century_error", "one_missing"]

    output_file = f"logs/duplicate_athletes_review_{timestamp}.csv"

    rows = []
    for category in categories:
        logger.info(f"Finding {category} duplicates...")
        pairs = find_duplicates_direct(category)

        for a1, a2 in pairs:
            results1 = get_result_count(a1["id"])
            results2 = get_result_count(a2["id"])

            rows.append({
                "category": category,
                "name": f"{a1['first_name']} {a1['last_name']}",
                "id1": a1["id"],
                "birth_year1": a1["birth_year"],
                "results1": results1,
                "gender1": a1["gender"],
                "external_id1": a1.get("external_id", ""),
                "id2": a2["id"],
                "birth_year2": a2["birth_year"],
                "results2": results2,
                "gender2": a2["gender"],
                "external_id2": a2.get("external_id", ""),
                "url1": f"https://friidrett.live/utover/{a1['id']}",
                "url2": f"https://friidrett.live/utover/{a2['id']}",
            })

    if not rows:
        logger.info("No review candidates found.")
        return

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Wrote {len(rows)} review candidates to {output_file}")

    # Print summary
    from collections import Counter
    cats = Counter(r["category"] for r in rows)
    for cat, count in cats.most_common():
        logger.info(f"  {cat}: {count} pairs")


def main():
    parser = argparse.ArgumentParser(description="Merge duplicate athletes")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--review", action="store_true", help="Generate review CSV instead of merging")
    parser.add_argument("--all", action="store_true", help="Include all categories in review")
    args = parser.parse_args()

    if args.review:
        generate_review_csv(include_all=args.all)
    else:
        if not args.dry_run:
            logger.warning("Running in LIVE mode — changes will be permanent!")
            response = input("Continue? (y/N): ")
            if response.lower() != "y":
                logger.info("Aborted.")
                return

        run_auto_merge(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
