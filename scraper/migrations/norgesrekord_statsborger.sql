-- Norske rekorder bare for norske statsborgere. 16.10.2026.
--
-- Utenlandske statsborgere i norsk klubb står i års- og alle-tiders-lister
-- (merket *), men kan ikke ta norsk rekord. norgesrekorder() brukes også av
-- finn_avvik(), så kontrollen «mulig rekord» følger samme regel.
-- Ukjent nasjonalitet (NULL) regnes som norsk, slik som ellers i basen.

create or replace function public.norgesrekorder(p_event_ids uuid[], p_kjonn text, p_aldersgrupper text[] default null::text[], p_inne boolean default null::boolean, p_min_dato jsonb default null::jsonb)
 returns table(event_id uuid, result_id uuid, performance text, performance_value integer, wind numeric, athlete_id uuid, athlete_name text, birth_date date, club_name text, meet_id uuid, meet_city text, meet_name text, date date, result_type text, athlete_nationality text)
 language sql
 stable
 set statement_timeout to '60s'
 set search_path to 'public'
as $function$
  with ev as (
    select e.id, e.code, e.category, e.result_type from unnest(p_event_ids) as x(id) join events e on e.id = x.id
  )
  select ev.id, b.id, b.performance, b.performance_value, b.wind,
         b.athlete_id, a.full_name, a.birth_date, c.name, b.meet_id, m.city, m.name,
         b.date, ev.result_type::text, a.nationality
  from ev
  cross join lateral (
    (select r.id, r.performance, r.performance_value, r.wind, r.athlete_id, r.club_id, r.meet_id, r.date
     from results r
     join athletes a on a.id = r.athlete_id
     join meets m on m.id = r.meet_id
     where ev.result_type = 'time'
       and r.event_id = ev.id and r.status = 'OK' and r.performance_value > 0
       and a.gender = p_kjonn
       and coalesce(a.nationality, 'NOR') = 'NOR'
       and not skjult_alder(extract(year from a.birth_date)::int, extract(year from r.date)::int)
       and (p_inne is null or m.indoor = p_inne)
       and not (ev.category in ('sprint', 'hurdles') and r.is_manual_time is true)
       and not (er_vindpaavirket(ev.code) and m.indoor is not true and r.is_wind_legal is not true)
       and (p_min_dato is null or p_min_dato ->> ev.code is null or r.date >= (p_min_dato ->> ev.code)::date)
       and (p_aldersgrupper is null or get_age_group(a.birth_date, r.date) = any (p_aldersgrupper))
     order by r.performance_value asc, r.date asc
     limit 1)
    union all
    (select r.id, r.performance, r.performance_value, r.wind, r.athlete_id, r.club_id, r.meet_id, r.date
     from results r
     join athletes a on a.id = r.athlete_id
     join meets m on m.id = r.meet_id
     where ev.result_type <> 'time'
       and r.event_id = ev.id and r.status = 'OK' and r.performance_value > 0
       and a.gender = p_kjonn
       and coalesce(a.nationality, 'NOR') = 'NOR'
       and not skjult_alder(extract(year from a.birth_date)::int, extract(year from r.date)::int)
       and (p_inne is null or m.indoor = p_inne)
       and not (ev.category in ('sprint', 'hurdles') and r.is_manual_time is true)
       and not (er_vindpaavirket(ev.code) and m.indoor is not true and r.is_wind_legal is not true)
       and (p_min_dato is null or p_min_dato ->> ev.code is null or r.date >= (p_min_dato ->> ev.code)::date)
       and (p_aldersgrupper is null or get_age_group(a.birth_date, r.date) = any (p_aldersgrupper))
     order by r.performance_value desc, r.date asc
     limit 1)
  ) b
  join athletes a on a.id = b.athlete_id
  join meets m on m.id = b.meet_id
  left join clubs c on c.id = b.club_id;
$function$;
