-- Migration: Fix SECURITY DEFINER issue on views
-- Date: 2026-01-27
--
-- This migration recreates views with security_invoker = true
-- to ensure they respect Row Level Security policies.
--
-- Apply this in Supabase SQL Editor.

-- 1. Fix results_full view
CREATE OR REPLACE VIEW results_full
WITH (security_invoker = true)
AS
SELECT
    r.id,
    r.athlete_id,
    a.first_name || ' ' || a.last_name as athlete_name,
    a.first_name as athlete_first_name,
    a.last_name as athlete_last_name,
    a.birth_date,
    a.birth_year,
    a.gender,
    r.event_id,
    e.name as event_name,
    e.code as event_code,
    e.category as event_category,
    e.result_type,
    e.sort_order as event_sort_order,
    r.club_id,
    c.name as club_name,
    r.meet_id,
    m.name as meet_name,
    m.city as meet_city,
    m.country as meet_country,
    m.indoor as meet_indoor,
    r.season_id,
    s.year as season_year,
    s.indoor as season_indoor,
    r.performance,
    r.performance_value,
    r.wind,
    r.place,
    r.status,
    r.is_manual_time,
    r.is_wind_legal,
    r.is_national_record,
    r.age_group,
    r.date,
    r.created_at,
    r.updated_at
FROM results r
LEFT JOIN athletes a ON r.athlete_id = a.id
LEFT JOIN events e ON r.event_id = e.id
LEFT JOIN clubs c ON r.club_id = c.id
LEFT JOIN meets m ON r.meet_id = m.id
LEFT JOIN seasons s ON r.season_id = s.id;

-- 2. Fix personal_bests view
CREATE OR REPLACE VIEW personal_bests
WITH (security_invoker = true)
AS
SELECT DISTINCT ON (athlete_id, event_id)
    r.id as result_id,
    r.athlete_id,
    r.event_id,
    r.performance,
    r.performance_value,
    r.date,
    r.wind,
    r.meet_id,
    r.is_national_record
FROM results r
WHERE r.status = 'OK'
  AND r.performance_value IS NOT NULL
  AND r.performance_value > 0
ORDER BY
    r.athlete_id,
    r.event_id,
    CASE
        WHEN (SELECT result_type FROM events WHERE id = r.event_id) = 'time'
        THEN r.performance_value
        ELSE -r.performance_value
    END ASC;

-- 3. Fix season_bests view
CREATE OR REPLACE VIEW season_bests
WITH (security_invoker = true)
AS
SELECT DISTINCT ON (athlete_id, event_id, season_id)
    r.id as result_id,
    r.athlete_id,
    r.event_id,
    r.season_id,
    r.performance,
    r.performance_value,
    r.date,
    r.wind,
    r.meet_id
FROM results r
WHERE r.status = 'OK'
  AND r.performance_value IS NOT NULL
  AND r.performance_value > 0
ORDER BY
    r.athlete_id,
    r.event_id,
    r.season_id,
    CASE
        WHEN (SELECT result_type FROM events WHERE id = r.event_id) = 'time'
        THEN r.performance_value
        ELSE -r.performance_value
    END ASC;

-- 4. Fix personal_bests_detailed view (uses CTE for wind filtering)
DROP VIEW IF EXISTS personal_bests_detailed;

CREATE VIEW personal_bests_detailed
WITH (security_invoker = true)
AS
WITH wind_affected_events AS (
  SELECT id FROM events
  WHERE code IN ('60m', '80m', '100m', '150m', '200m', 'lengde', 'tresteg')
     OR code LIKE '%60mh%' OR code LIKE '%80mh%' OR code LIKE '%100mh%' OR code LIKE '%110mh%' OR code LIKE '%200mh%'
),
eligible_results AS (
  SELECT r.*
  FROM results_full r
  WHERE r.status = 'OK'
    AND r.performance_value IS NOT NULL
    AND r.performance_value > 0
    AND (
      r.meet_indoor = true
      OR r.event_id NOT IN (SELECT id FROM wind_affected_events)
      OR (r.event_id IN (SELECT id FROM wind_affected_events)
          AND r.meet_indoor = false
          AND (r.wind IS NULL OR r.wind <= 2.0))
    )
),
ranked_results AS (
  SELECT
    r.*,
    ROW_NUMBER() OVER (
      PARTITION BY r.athlete_id, r.event_id
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
  meet_city
FROM ranked_results
WHERE rn = 1;
