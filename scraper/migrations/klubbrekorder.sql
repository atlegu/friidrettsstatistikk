-- Klubbrekorder i én spørring. Anvendt mot produksjon 18.09.2026.
-- Siden /klubber/[id]/statistikk/rekorder kjørte én spørring per øvelse
-- (rundt 300) og brukte 12 s; via results_full tok én spørring 7 s, rett
-- mot basistabellene 0,3–0,6 s. Samme regler som siden hadde: håndtid ute
-- i sprint og hekk, bare lovlig vind der vind teller (er_vindpaavirket),
-- aldersgrupper (get_age_group) og bane som filter.
create or replace function klubbrekorder(p_klubb uuid, p_kjonn text, p_aldersgrupper text[] default null, p_inne boolean default null)
returns table (
  event_id uuid, result_id uuid, performance text, performance_value integer, wind numeric,
  athlete_id uuid, athlete_name text, birth_date date, meet_id uuid, meet_city text, meet_name text,
  date date, result_type text
)
language sql
stable
security definer
set statement_timeout = '60s'
set search_path = public
as $$
  select distinct on (r.event_id)
         r.event_id, r.id, r.performance, r.performance_value, r.wind,
         r.athlete_id, a.full_name, a.birth_date, r.meet_id, m.city, m.name,
         r.date, e.result_type::text
  from results r
  join athletes a on a.id = r.athlete_id
  join meets m on m.id = r.meet_id
  join events e on e.id = r.event_id
  where r.club_id = p_klubb
    and a.gender = p_kjonn
    and r.status = 'OK'
    and r.performance_value > 0
    and (p_inne is null or m.indoor = p_inne)
    and not (e.category in ('sprint', 'hurdles') and r.is_manual_time is true)
    and not (er_vindpaavirket(e.code) and m.indoor is not true and r.is_wind_legal is not true)
    and (p_aldersgrupper is null or get_age_group(a.birth_date, r.date) = any (p_aldersgrupper))
  order by r.event_id,
           case when e.result_type = 'time' then r.performance_value else -r.performance_value end,
           r.date;
$$;
grant execute on function klubbrekorder(uuid, text, text[], boolean) to anon, authenticated, service_role;
