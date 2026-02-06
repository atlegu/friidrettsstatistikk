-- Migration: Update personal_bests_detailed view - require wind for post-1990 results
-- For outdoor wind-affected events after 1990, wind MUST be recorded (not NULL)
-- For results 1990 and earlier, wind can be NULL

DROP VIEW IF EXISTS personal_bests_detailed;

CREATE VIEW personal_bests_detailed AS
WITH wind_affected_events AS (
  -- Events where wind matters for records
  SELECT id FROM events
  WHERE code IN ('60m', '80m', '100m', '150m', '200m', 'lengde', 'tresteg')
     OR code LIKE '%60mh%' OR code LIKE '%80mh%' OR code LIKE '%100mh%' OR code LIKE '%110mh%' OR code LIKE '%200mh%'
),
eligible_results AS (
  -- Filter results based on wind rules
  SELECT r.*
  FROM results_full r
  WHERE r.status = 'OK'
    AND r.performance_value IS NOT NULL
    AND r.performance_value > 0
    AND (
      -- Indoor events: always include (no wind)
      r.meet_indoor = true
      -- Non-wind-affected events: always include
      OR r.event_id NOT IN (SELECT id FROM wind_affected_events)
      -- Wind-affected outdoor events, post-1990: wind MUST be recorded and <= 2.0
      OR (r.event_id IN (SELECT id FROM wind_affected_events)
          AND r.meet_indoor = false
          AND EXTRACT(YEAR FROM r.date) > 1990
          AND r.wind IS NOT NULL
          AND r.wind <= 2.0)
      -- Wind-affected outdoor events, 1990 and earlier: wind can be NULL or <= 2.0
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
