-- Register population for reviewer comment 13 (Table S31, Supplementary Methods S-M11).
-- Run against Supabase project lwkykthpnthfcldifixg (2026-10-01). The two result sets are
-- joined on id in Python and saved as revision_r1/data_private/register_population_1998_2002.csv
-- (columns athlete_id, gender, birth_year, vol_13_14, res_13_14, senior; not in git, GDPR).

-- 1) Distinct meets and results at ages 13-14, every athlete born 1998-2002 with >=1 result at 13-14
WITH a AS (
  SELECT id, gender, birth_year FROM athletes WHERE birth_year BETWEEN 1998 AND 2002
),
r AS (
  SELECT r.athlete_id, (EXTRACT(YEAR FROM r.date)::int - a.birth_year) AS age, r.meet_id
  FROM results r JOIN a ON a.id = r.athlete_id
  WHERE r.date >= '2011-01-01' AND r.date < '2017-01-01'
),
pa AS (
  SELECT athlete_id, age, COUNT(*) AS n_res, COUNT(DISTINCT meet_id) AS n_meets
  FROM r WHERE age IN (13, 14) GROUP BY athlete_id, age
)
SELECT pa.athlete_id AS id, a.gender AS g, a.birth_year AS by,
       SUM(n_meets) AS v, SUM(n_res) AS r
FROM pa JOIN a ON a.id = pa.athlete_id
GROUP BY pa.athlete_id, a.gender, a.birth_year;

-- 2) Senior status: >=2 results in a calendar year at age 20 or later (sa = latest such age)
WITH a AS (
  SELECT id, birth_year FROM athletes WHERE birth_year BETWEEN 1998 AND 2002
),
r AS (
  SELECT r.athlete_id, (EXTRACT(YEAR FROM r.date)::int - a.birth_year) AS age
  FROM results r JOIN a ON a.id = r.athlete_id
  WHERE r.date >= '2018-01-01'
),
pa AS (
  SELECT athlete_id, age, COUNT(*) AS n_res FROM r WHERE age >= 20 GROUP BY athlete_id, age
)
SELECT athlete_id AS id, MAX(age) FILTER (WHERE n_res >= 2) AS sa
FROM pa GROUP BY athlete_id HAVING MAX(n_res) >= 2;
