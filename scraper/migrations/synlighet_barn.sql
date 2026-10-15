-- Statistikk for barn til og med 11 år vises ikke offentlig. 15.10.2026.
--
-- Resultatene ligger i basen som før, men holdes utenfor alle offentlige
-- lister: årslister, alle-tiders-lister, rekorder, klubbstatistikk og
-- gateløp. Alderen regnes etter kalenderåret (konkurranseår − fødselsår).
-- Grensen står ett sted, i skjult_alder(), så den kan endres uten kodeendring.
--
-- get_age_group() skiller nå 12-åringer ut i egen gruppe («12»), og «Yngre»
-- betyr til og med 11 år.

create or replace function public.skjult_alder(p_fodt int, p_aar int) returns boolean
language sql immutable as $$
  select p_fodt is not null and p_aar is not null and p_aar - p_fodt <= 11
$$;

create or replace function public.get_age_group(birth_date date, competition_date date)
returns text language plpgsql immutable set search_path to 'public'
as $function$
declare athlete_age integer;
begin
  if birth_date is null then return null; end if;
  -- Kalenderåret: konkurranseår minus fødselsår
  athlete_age := extract(year from competition_date) - extract(year from birth_date);
  if athlete_age >= 35 then return 'V' || ((athlete_age / 5) * 5);
  elsif athlete_age >= 23 then return 'Senior';
  elsif athlete_age >= 20 then return '20-22';
  elsif athlete_age >= 18 then return '18-19';
  elsif athlete_age = 17 then return '17';
  elsif athlete_age = 16 then return '16';
  elsif athlete_age = 15 then return '15';
  elsif athlete_age = 14 then return '14';
  elsif athlete_age = 13 then return '13';
  elsif athlete_age = 12 then return '12';
  else return 'Yngre';  -- til og med 11 år: vises ikke offentlig
  end if;
end;
$function$;

create or replace function public.get_all_time_best(p_event_id uuid, p_gender text, p_age_groups text[] default null, p_indoor boolean default null, p_ascending boolean default true, p_exclude_manual boolean default false, p_exclude_wind_illegal boolean default false, p_only_manual boolean default false, p_limit integer default 100, p_offset integer default 0)
returns table(id uuid, athlete_id uuid, athlete_name text, performance text, performance_value integer, result_type text, wind numeric, is_national_record boolean, date date, birth_date date, club_name text, meet_id uuid, meet_name text, total_count bigint)
language plpgsql stable set search_path to 'public'
as $function$
begin
  return query
  with best as (
    select distinct on (rf.athlete_id)
      rf.id, rf.athlete_id, rf.athlete_name, rf.performance, rf.performance_value,
      rf.result_type::text, rf.wind, rf.is_national_record, rf.date, rf.birth_date,
      rf.club_name, rf.meet_id, rf.meet_name
    from results_full rf
    where rf.event_id = p_event_id
      and rf.gender = p_gender
      and rf.status = 'OK'
      and rf.performance_value is not null
      and rf.performance_value > 0
      and rf.age_group is distinct from 'Yngre'          -- barn til og med 11 år vises ikke
      and (p_age_groups is null or rf.age_group = any(p_age_groups))
      and (p_indoor is null or rf.meet_indoor = p_indoor)
      and (not p_exclude_manual or rf.is_manual_time is not true)
      and (not p_only_manual or rf.is_manual_time = true)
      and (not p_exclude_wind_illegal or rf.is_wind_legal is not false)
    order by rf.athlete_id,
      case when p_ascending then rf.performance_value end asc,
      case when not p_ascending then rf.performance_value end desc
  ),
  counted as (select count(*) as cnt from best)
  select b.id, b.athlete_id, b.athlete_name, b.performance, b.performance_value,
         b.result_type, b.wind, b.is_national_record, b.date, b.birth_date,
         b.club_name, b.meet_id, b.meet_name, c.cnt as total_count
  from best b, counted c
  order by
    case when p_ascending then b.performance_value end asc,
    case when not p_ascending then b.performance_value end desc
  limit p_limit offset p_offset;
end;
$function$;

create or replace function public.klubbrekorder(p_klubb uuid, p_kjonn text, p_aldersgrupper text[] default null, p_inne boolean default null)
returns table(event_id uuid, result_id uuid, performance text, performance_value integer, wind numeric, athlete_id uuid, athlete_name text, birth_date date, meet_id uuid, meet_city text, meet_name text, date date, result_type text)
language sql stable set statement_timeout to '60s' set search_path to 'public'
as $function$
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
    and not skjult_alder(extract(year from a.birth_date)::int, extract(year from r.date)::int)
    and (p_inne is null or m.indoor = p_inne)
    and not (e.category in ('sprint', 'hurdles') and r.is_manual_time is true)
    and not (er_vindpaavirket(e.code) and m.indoor is not true and r.is_wind_legal is not true)
    and (p_aldersgrupper is null or get_age_group(a.birth_date, r.date) = any (p_aldersgrupper))
  order by r.event_id,
           case when e.result_type = 'time' then r.performance_value else -r.performance_value end,
           r.date;
$function$;

create or replace function public.norgesrekorder(p_event_ids uuid[], p_kjonn text, p_aldersgrupper text[] default null, p_inne boolean default null, p_min_dato jsonb default null)
returns table(event_id uuid, result_id uuid, performance text, performance_value integer, wind numeric, athlete_id uuid, athlete_name text, birth_date date, club_name text, meet_id uuid, meet_city text, meet_name text, date date, result_type text)
language sql stable set statement_timeout to '60s' set search_path to 'public'
as $function$
  with ev as (
    select e.id, e.code, e.category, e.result_type from unnest(p_event_ids) as x(id) join events e on e.id = x.id
  )
  select ev.id, b.id, b.performance, b.performance_value, b.wind,
         b.athlete_id, a.full_name, a.birth_date, c.name, b.meet_id, m.city, m.name,
         b.date, ev.result_type::text
  from ev
  cross join lateral (
    (select r.id, r.performance, r.performance_value, r.wind, r.athlete_id, r.club_id, r.meet_id, r.date
     from results r
     join athletes a on a.id = r.athlete_id
     join meets m on m.id = r.meet_id
     where ev.result_type = 'time'
       and r.event_id = ev.id and r.status = 'OK' and r.performance_value > 0
       and a.gender = p_kjonn
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

create or replace function public.klubb_statistikk(p_klubb uuid)
returns jsonb language sql stable set statement_timeout to '60s' set search_path to 'public'
as $function$
  with r as materialized (
    select r.id, r.athlete_id, r.meet_id, r.date, extract(year from r.date)::int as aar
    from results r where r.club_id = p_klubb and r.status = 'OK'
  ),
  per_aar as (
    select aar, count(*) as resultater, count(distinct athlete_id) as utovere, count(distinct meet_id) as stevner
    from r where aar >= extract(year from current_date)::int - 12 group by aar order by aar
  ),
  i_aar as (
    select count(*) as resultater, count(distinct athlete_id) as utovere, count(distinct meet_id) as stevner
    from r where aar = extract(year from current_date)::int
  ),
  topp as (
    -- Navngitte utøvere: barn til og med 11 år vises ikke
    select a.id, a.full_name, a.birth_year, count(*) as resultater, count(distinct r.meet_id) as stevner
    from r join athletes a on a.id = r.athlete_id
    where r.aar = extract(year from current_date)::int
      and not skjult_alder(coalesce(a.birth_year, extract(year from a.birth_date)::int), r.aar)
    group by a.id, a.full_name, a.birth_year
    order by count(*) desc, count(distinct r.meet_id) desc limit 10
  )
  select jsonb_build_object(
    'per_aar', (select coalesce(jsonb_agg(to_jsonb(per_aar)), '[]'::jsonb) from per_aar),
    'i_aar', (select to_jsonb(i_aar) from i_aar),
    'topp', (select coalesce(jsonb_agg(to_jsonb(topp)), '[]'::jsonb) from topp)
  );
$function$;

-- Gateløp: årsbeste og løpssider (lop_arsbeste) holder barn utenfor
create or replace function public.lop_arsbeste(p_aar int, p_distanse int, p_kjonn text,
                                    p_nivaa text[] default array['A', 'B'],
                                    p_antall int default 100,
                                    p_bare_norske boolean default true,
                                    p_alder_fra int default null,
                                    p_alder_til int default null)
returns table (plass bigint, resultat_id uuid, navn text, fodt int, klubb text, tid_ms int,
               athlete_id uuid, lop_navn text, arrangement_id uuid, dato date, sted text,
               kvalitetsnivaa char(1), nasjon text)
language sql stable set search_path = public
as $$
  with beste as (
    select distinct on (coalesce(r.athlete_id::text, lower(r.navn) || coalesce(r.fodt::text, '')))
           r.id, r.navn, r.fodt, r.klubb, r.tid_ms, r.athlete_id, r.nasjon,
           a.id arr_id, a.navn arr_navn, coalesce(l.dato, a.dato) dato, a.sted, l.kvalitetsnivaa
    from lop_resultat r
    join lop_lop l on l.id = r.lop_id
    join lop_arrangement a on a.id = l.arrangement_id
    where l.distanse_m = p_distanse and l.kvalitetsnivaa = any (p_nivaa)
      and extract(year from coalesce(l.dato, a.dato)) = p_aar
      and r.kjonn = p_kjonn and r.status = 'OK' and r.tid_ms > 0
      and not skjult_alder(r.fodt, p_aar)
      and (not p_bare_norske or r.nasjon = 'NOR')
      and (p_alder_fra is null or p_aar - r.fodt >= p_alder_fra)
      and (p_alder_til is null or p_aar - r.fodt <= p_alder_til)
    order by coalesce(r.athlete_id::text, lower(r.navn) || coalesce(r.fodt::text, '')), r.tid_ms
  )
  select rank() over (order by ceil(tid_ms / 1000.0)), id, navn, fodt, klubb, tid_ms, athlete_id,
         arr_navn, arr_id, dato, sted, kvalitetsnivaa, nasjon
  from beste order by tid_ms limit p_antall;
$$;
