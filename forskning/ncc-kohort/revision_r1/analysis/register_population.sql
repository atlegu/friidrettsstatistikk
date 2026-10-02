-- Register population for reviewer comment 13 (Table S31, Supplementary Methods S-M11).
-- Run against Supabase project lwkykthpnthfcldifixg (2026-10-02) with the register state used for
-- the analysis data (rows created on or before 18 May 2026, results up to 31 Dec 2025, status OK).
-- Cohort membership uses the same venue-day definition as r1_00_corrected_data.py and reproduces
-- its 2,138 members. Volume = competition days (distinct dates) at ages 13-14; senior = >=2 results
-- in a calendar year at age 20 or later. Returns a frequency table (cohort x sex x volume x senior),
-- saved as revision_r1/data_private/register_population_freq.csv (columns cohort, gender, vol,
-- senior, n; not in git) and expanded to athlete rows in r1_03.

WITH lek_meets AS (
  SELECT id FROM meets
  WHERE start_date IN ('2011-09-03','2011-09-04','2012-09-08','2012-09-09','2013-08-31','2013-09-01',
                       '2014-09-13','2014-09-14','2015-09-05','2015-09-06','2016-08-27','2016-08-28')
    AND city IN ('Romerike Friidrettstadion','Lillestrøm','Jessheim Friidrettsstadion','Jessheim',
                 'Osterøy Stadion','Osterøy','Øverlands Minde','Stjørdal')
    AND name NOT ILIKE '%3xl%'
),
a AS (SELECT id, gender, birth_year FROM athletes WHERE birth_year BETWEEN 1998 AND 2002),
r AS (
  SELECT r.athlete_id, r.date, r.meet_id, EXTRACT(YEAR FROM r.date)::int - a.birth_year AS age
  FROM results r JOIN a ON a.id = r.athlete_id
  WHERE r.created_at <= '2026-05-18' AND r.date <= '2025-12-31' AND r.status = 'OK'
),
coh AS (SELECT DISTINCT athlete_id FROM r WHERE age IN (13, 14) AND meet_id IN (SELECT id FROM lek_meets)),
v AS (SELECT athlete_id, COUNT(DISTINCT date) AS vol FROM r WHERE age IN (13, 14) GROUP BY athlete_id),
s AS (SELECT athlete_id, 1 AS senior
      FROM (SELECT athlete_id FROM r WHERE age >= 20 GROUP BY athlete_id, EXTRACT(YEAR FROM date)
            HAVING COUNT(*) >= 2) x
      GROUP BY athlete_id),
f AS (
  SELECT (c.athlete_id IS NOT NULL)::int AS cohort, COALESCE(a.gender, 'U') AS gender, v.vol,
         COALESCE(s.senior, 0) AS senior, COUNT(*) AS n
  FROM v JOIN a ON a.id = v.athlete_id
  LEFT JOIN coh c ON c.athlete_id = v.athlete_id
  LEFT JOIN s ON s.athlete_id = v.athlete_id
  GROUP BY 1, 2, 3, 4
)
SELECT COUNT(*) AS cells, SUM(n) AS athletes, SUM(n) FILTER (WHERE cohort = 1) AS cohort_n,
       string_agg(cohort || ',' || gender || ',' || vol || ',' || senior || ',' || n, ';'
                  ORDER BY cohort, gender, vol, senior) AS freq
FROM f;
-- 2026-10-02: 364 cells, 7,266 athletes, 2,138 cohort members.
