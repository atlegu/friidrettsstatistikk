-- Identifiserer alle stevnerader som tilhører 13-14-årslekene 2012-2025
-- (NCC 2012, PEAB 2013-14, Bendit 2015, Ungdomslekene 2016, Lerøy 2017-25).
-- NB: basen har dubletter (aggregat + per arena/dag); dedupliser på
-- athlete_id x event_id x yr i uttrekket. Extralekene (Ålgård) er et annet stevne.

WITH serie AS (
  SELECT m.id AS meet_id, m.name, m.city, m.start_date,
         EXTRACT(YEAR FROM m.start_date)::int AS yr
  FROM meets m
  WHERE m.start_date BETWEEN '2012-01-01' AND '2025-12-31'
    AND (
      m.name ~* '(ncc|peab|bendit)[- ]?lek'
      OR (m.name ILIKE '%lerøy%'
          AND m.name NOT ILIKE '%stavstevne%'
          AND m.name NOT ILIKE '%kvalifisering%'
          AND m.name NOT ILIKE '%Oppkjøring%')
      OR (m.name ILIKE '%Ungdomslekene%'
          AND m.start_date BETWEEN '2016-08-26' AND '2016-08-29')
    )
    AND m.name NOT ILIKE '%Naperville%'
    AND m.name NOT ILIKE '%Nattstevne%'
),
resultater AS (
  SELECT DISTINCT ON (r.athlete_id, r.event_id, s.yr)
         s.yr, s.city AS arena, s.start_date,
         r.athlete_id, a.gender, a.birth_date, a.birth_year,
         s.yr - a.birth_year AS klasse,
         (s.start_date - a.birth_date) AS alder_dager,
         e.code AS ovelse, e.name AS ovelse_navn, e.result_type,
         r.performance, r.performance_value, r.wind, r.is_wind_legal,
         r.is_manual_time, r.hurdle_height_cm, r.implement_weight_kg
  FROM serie s
  JOIN results r  ON r.meet_id = s.meet_id
  JOIN athletes a ON a.id = r.athlete_id
  JOIN events e   ON e.id = r.event_id
  WHERE s.yr - a.birth_year IN (13, 14)
    AND r.performance_value IS NOT NULL
  ORDER BY r.athlete_id, r.event_id, s.yr,
           -- beste resultat først: lavest tid for løp, høyest verdi ellers
           CASE WHEN e.result_type = 'time' THEN r.performance_value END ASC,
           CASE WHEN e.result_type <> 'time' THEN r.performance_value END DESC
)
SELECT * FROM resultater;
