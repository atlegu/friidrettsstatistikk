#!/usr/bin/env python3
"""Set is_pb and is_national_record using SQL for much faster execution."""

import sys
sys.stdout.reconfigure(line_buffering=True)

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("Setting PBs and NRs using direct SQL queries...")

# SQL to set is_pb for best result per athlete/event
# For time events: lower is better
# For distance/height/points: higher is better
pb_sql = """
WITH ranked_results AS (
    SELECT
        r.id,
        ROW_NUMBER() OVER (
            PARTITION BY r.athlete_id, r.event_id
            ORDER BY
                CASE WHEN e.result_type = 'time' THEN r.performance_value ELSE -r.performance_value END ASC
        ) as rn
    FROM results r
    JOIN events e ON r.event_id = e.id
    WHERE r.performance_value IS NOT NULL
      AND r.performance_value > 0
)
UPDATE results
SET is_pb = true
WHERE id IN (SELECT id FROM ranked_results WHERE rn = 1);
"""

# SQL to set is_national_record for best result per event/gender
nr_sql = """
WITH ranked_results AS (
    SELECT
        r.id,
        ROW_NUMBER() OVER (
            PARTITION BY r.event_id, a.gender
            ORDER BY
                CASE WHEN e.result_type = 'time' THEN r.performance_value ELSE -r.performance_value END ASC
        ) as rn
    FROM results r
    JOIN events e ON r.event_id = e.id
    JOIN athletes a ON r.athlete_id = a.id
    WHERE r.performance_value IS NOT NULL
      AND r.performance_value > 0
      AND r.status = 'OK'
      AND a.gender IS NOT NULL
)
UPDATE results
SET is_national_record = true
WHERE id IN (SELECT id FROM ranked_results WHERE rn = 1);
"""

# First, reset all flags
print("Resetting all PB flags...")
reset_pb_sql = "UPDATE results SET is_pb = false WHERE is_pb = true;"
reset_nr_sql = "UPDATE results SET is_national_record = false WHERE is_national_record = true;"

try:
    # Try using rpc if available
    print("Attempting SQL via RPC...")
    supabase.rpc('exec_sql', {'query': reset_pb_sql}).execute()
except Exception as e:
    print(f"RPC not available: {e}")
    print("Using Supabase MCP tool instead would work better here.")
    print("Please run this SQL directly in Supabase dashboard or via MCP.")

print("\nSQL queries to run:")
print("=" * 60)
print("\n-- Reset PB flags")
print(reset_pb_sql)
print("\n-- Reset NR flags")
print(reset_nr_sql)
print("\n-- Set PB flags")
print(pb_sql)
print("\n-- Set NR flags")
print(nr_sql)
