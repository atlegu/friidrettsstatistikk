"""Kjør migrasjon via Supabase REST API"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

migration_sql = """
DROP VIEW IF EXISTS personal_bests_detailed;

CREATE VIEW personal_bests_detailed AS
WITH wind_affected_events AS (
  SELECT id FROM events
  WHERE code IN ('60m', '80m', '100m', '150m', '200m', 'lengde', 'tresteg')
     OR code LIKE '%60mh%' OR code LIKE '%80mh%' OR code LIKE '%100mh%' OR code LIKE '%110mh%' OR code LIKE '%200mh%'
),
womens_javelin_events AS (
  SELECT id FROM events WHERE code = 'spyd_600g'
),
eligible_results AS (
  SELECT r.*,
    CASE
      WHEN r.event_id IN (SELECT id FROM womens_javelin_events)
           AND r.gender = 'F'
           AND EXTRACT(YEAR FROM r.date) < 1999
      THEN 'old_spec'
      WHEN r.event_id IN (SELECT id FROM womens_javelin_events)
           AND r.gender = 'F'
           AND EXTRACT(YEAR FROM r.date) >= 1999
      THEN 'new_spec'
      ELSE 'standard'
    END as javelin_spec
  FROM results_full r
  WHERE r.status = 'OK'
    AND r.performance_value IS NOT NULL
    AND r.performance_value > 0
    AND (
      r.meet_indoor = true
      OR r.event_id NOT IN (SELECT id FROM wind_affected_events)
      OR (r.event_id IN (SELECT id FROM wind_affected_events)
          AND r.meet_indoor = false
          AND EXTRACT(YEAR FROM r.date) > 1990
          AND r.wind IS NOT NULL
          AND r.wind <= 2.0)
      OR (r.event_id IN (SELECT id FROM wind_affected_events)
          AND r.meet_indoor = false
          AND EXTRACT(YEAR FROM r.date) <= 1990
          AND (r.wind IS NULL OR r.wind <= 2.0))
    )
),
ranked_results AS (
  SELECT
    r.*,
    ROW_NUMBER() OVER (
      PARTITION BY r.athlete_id, r.event_id, r.javelin_spec
      ORDER BY
        CASE WHEN r.result_type = 'time' THEN r.performance_value ELSE -r.performance_value END ASC
    ) as rn
  FROM eligible_results r
)
SELECT
  athlete_id,
  event_id,
  id as result_id,
  performance,
  performance_value,
  date,
  wind,
  is_national_record,
  meet_id,
  meet_indoor as is_indoor,
  athlete_name,
  gender,
  event_code,
  event_name,
  result_type,
  (SELECT sort_order FROM events WHERE id = ranked_results.event_id) as event_sort_order,
  meet_name,
  meet_city,
  javelin_spec
FROM ranked_results
WHERE rn = 1;
"""

def main():
    print("Kjører migrasjon via Supabase SQL endpoint...")

    # Prøv SQL over HTTP endpoint (for pg_graphql eller lignende)
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json={'sql': migration_sql})

    if response.status_code == 200:
        print("Migrasjon fullført!")
    else:
        print(f"REST API feilet: {response.status_code}")
        print(response.text)
        print()
        print("=" * 60)
        print("Du må kjøre SQL-en manuelt i Supabase Dashboard:")
        print("1. Gå til https://supabase.com/dashboard")
        print("2. Velg prosjektet")
        print("3. Gå til SQL Editor")
        print("4. Lim inn og kjør innholdet fra:")
        print("   migrations/update_personal_bests_javelin_specs.sql")
        print("=" * 60)

if __name__ == '__main__':
    main()
