-- Nasjonal kontroll: sesongbeste for ALLE norske 13-14-åringer (ikke bare lekene)
-- i kast, lengde og høyde, per år, kjønn og klasse. Brukes til å sjekke om trendene
-- på lekene skyldes seleksjon inn i stevnet. Kjøres mot Supabase (prosjekt lwkykthpnthfcldifixg);
-- resultatet lagres som tables/nasjonal_13_14_per_aar.csv og sammenlignes i tables/nasjonal_kontroll.csv.
-- NB: performance_value er i cm for hopp/kast; bare relative trender brukes.
WITH r AS (
  SELECT a.id AS athlete_id, e.code, EXTRACT(YEAR FROM r.date)::int AS yr,
         EXTRACT(YEAR FROM r.date)::int - a.birth_year AS klasse, a.gender,
         MAX(r.performance_value) AS best
  FROM results r
  JOIN events e ON e.id = r.event_id
  JOIN athletes a ON a.id = r.athlete_id
  WHERE e.code IN ('spyd_400g','spyd_600g','kule_2kg','kule_3kg','kule_4kg',
                   'diskos_600g','diskos_750g','diskos_1kg','lengde','hoyde')
    AND r.date >= '2012-01-01'
    AND r.performance_value IS NOT NULL AND r.performance_value > 0
    AND a.birth_year IS NOT NULL AND a.gender IN ('M','F')
    AND EXTRACT(YEAR FROM r.date)::int - a.birth_year IN (13, 14)
  GROUP BY 1, 2, 3, 4, 5
)
SELECT code, gender, klasse, yr, COUNT(*) AS n,
       ROUND(percentile_cont(0.5) WITHIN GROUP (ORDER BY best)::numeric, 1) AS med,
       ROUND(percentile_cont(0.9) WITHIN GROUP (ORDER BY best)::numeric, 1) AS p90
FROM r
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2, 3, 4;
