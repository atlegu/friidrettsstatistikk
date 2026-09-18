-- Anvendt mot produksjon 18.09.2026. Se OPERATIONS_LOG 2026-09-18.
--
-- 1) norgesrekorder: beste resultat per øvelse over hele basen i ett kall.
--    /statistikk/rekorder kjørte én spørring per øvelse (60–100) og en
--    øvelse som feilet forsvant stille. Sortering direkte på
--    performance_value så idx_results_event_perf brukes (CASE i ORDER BY
--    ga 60 s).
-- 2) tell_kvalifiserte: antall kvalifiserte per NM-krav i ett kall.
--    /mesterskap/[id] hentet alle kvalifiserte rader per krav for å telle.
--    Indeks idx_results_event_date_perf (event_id, date, performance_value)
--    lagt til for kvalifiseringsvinduet.
-- 3) rett_minuttider + test_urimelige_tider: «2.25» på 800 m er 2:25.

create index if not exists idx_results_event_date_perf on results (event_id, date, performance_value) where status = 'OK';

create or replace function norgesrekorder(
  p_event_ids uuid[], p_kjonn text,
  p_aldersgrupper text[] default null, p_inne boolean default null, p_min_dato jsonb default null)
returns table (
  event_id uuid, result_id uuid, performance text, performance_value integer, wind numeric,
  athlete_id uuid, athlete_name text, birth_date date, club_name text, meet_id uuid, meet_city text,
  meet_name text, date date, result_type text
)
language sql stable security definer set statement_timeout = '60s' set search_path = public
as $$
  with ev as (
    select e.id, e.code, e.category, e.result_type from unnest(p_event_ids) as x(id) join events e on e.id = x.id
  )
  select ev.id, b.id, b.performance, b.performance_value, b.wind,
         b.athlete_id, a.full_name, a.birth_date, c.name, b.meet_id, m.city, m.name,
         b.date, ev.result_type::text
  from ev
  cross join lateral (
    (select r.id, r.performance, r.performance_value, r.wind, r.athlete_id, r.club_id, r.meet_id, r.date
     from results r join athletes a on a.id = r.athlete_id join meets m on m.id = r.meet_id
     where ev.result_type = 'time'
       and r.event_id = ev.id and r.status = 'OK' and r.performance_value > 0
       and a.gender = p_kjonn
       and (p_inne is null or m.indoor = p_inne)
       and not (ev.category in ('sprint', 'hurdles') and r.is_manual_time is true)
       and not (er_vindpaavirket(ev.code) and m.indoor is not true and r.is_wind_legal is not true)
       and (p_min_dato is null or p_min_dato ->> ev.code is null or r.date >= (p_min_dato ->> ev.code)::date)
       and (p_aldersgrupper is null or get_age_group(a.birth_date, r.date) = any (p_aldersgrupper))
     order by r.performance_value asc, r.date asc limit 1)
    union all
    (select r.id, r.performance, r.performance_value, r.wind, r.athlete_id, r.club_id, r.meet_id, r.date
     from results r join athletes a on a.id = r.athlete_id join meets m on m.id = r.meet_id
     where ev.result_type <> 'time'
       and r.event_id = ev.id and r.status = 'OK' and r.performance_value > 0
       and a.gender = p_kjonn
       and (p_inne is null or m.indoor = p_inne)
       and not (ev.category in ('sprint', 'hurdles') and r.is_manual_time is true)
       and not (er_vindpaavirket(ev.code) and m.indoor is not true and r.is_wind_legal is not true)
       and (p_min_dato is null or p_min_dato ->> ev.code is null or r.date >= (p_min_dato ->> ev.code)::date)
       and (p_aldersgrupper is null or get_age_group(a.birth_date, r.date) = any (p_aldersgrupper))
     order by r.performance_value desc, r.date asc limit 1)
  ) b
  join athletes a on a.id = b.athlete_id
  join meets m on m.id = b.meet_id
  left join clubs c on c.id = b.club_id;
$$;
grant execute on function norgesrekorder(uuid[], text, text[], boolean, jsonb) to anon, authenticated, service_role;

-- Løkke i plpgsql: øvelses-id-ene slås opp først, så planleggeren ser
-- konkrete verdier og bruker idx_results_event_date_perf. Som ren SQL
-- gjennom jsonb tok fire krav 3 s.
create or replace function tell_kvalifiserte(p_standarder jsonb, p_kjonn text)
returns jsonb
language plpgsql stable security definer set statement_timeout = '60s' set search_path = public
as $$
declare
  st jsonb; v jsonb; ut jsonb := '{}'::jsonb; n bigint; ids uuid[];
  fra date; til date; lavere boolean; inne boolean; klubb uuid;
  terskel int; manuell boolean; vind boolean; min_aar int;
  utovere uuid[];
begin
  for st in select * from jsonb_array_elements(p_standarder) loop
    fra := (st ->> 'fra')::date; til := (st ->> 'til')::date;
    lavere := (st ->> 'lavere')::boolean; inne := (st ->> 'inne_teller')::boolean;
    klubb := (st ->> 'klubb')::uuid;
    utovere := '{}';
    for v in select * from jsonb_array_elements(st -> 'varianter') loop
      select array_agg(e.id) into ids from events e
       where e.code = any (array(select jsonb_array_elements_text(v -> 'koder')));
      terskel := (v ->> 'terskel')::int; manuell := (v ->> 'manuell')::boolean;
      vind := (v ->> 'vind')::boolean; min_aar := (v ->> 'min_fodselsaar')::int;
      if ids is null then continue; end if;
      utovere := utovere || array(
        select distinct r.athlete_id
        from results r join athletes a on a.id = r.athlete_id join meets m on m.id = r.meet_id
        where r.event_id = any (ids)
          and r.date between fra and til
          and r.status = 'OK' and r.performance_value > 0
          and (case when lavere then r.performance_value <= terskel else r.performance_value >= terskel end)
          and a.gender = p_kjonn
          and (inne or m.indoor is not true)
          and not (manuell and r.is_manual_time is true)
          and not (vind and m.indoor is not true and r.is_wind_legal is not true)
          and (klubb is null or r.club_id = klubb)
          and (min_aar is null or a.birth_date >= make_date(min_aar, 1, 1)));
    end loop;
    select count(distinct x) into n from unnest(utovere) x;
    ut := ut || jsonb_build_object(st ->> 'id', n);
  end loop;
  return ut;
end;
$$;
grant execute on function tell_kvalifiserte(jsonb, text) to anon, authenticated, service_role;

create or replace function er_langt_loep(p_code text)
returns boolean language sql immutable as $$
  select p_code is not null and (
    p_code ~ '^(800|1000|1500|2000|3000|5000|10000)m'
    or p_code ~ '^(kappgang|gange)'
    or p_code ~ '(hinder|mile|miles|mg$|_gange|maraton|halvmaraton|timesloep)'
  );
$$;

create or replace function rett_minuttider(p_dry boolean default true)
returns jsonb
language plpgsql security definer set statement_timeout = '110s' set search_path = public
as $$
declare
  rad record; v_rettet int := 0; v_slettet int := 0; v_feil int := 0; v_funnet int := 0;
begin
  for rad in
    select res.id, res.performance
    from results res join events e on e.id = res.event_id
    where e.result_type = 'time' and er_langt_loep(e.code)
      and res.performance ~ '^\d{1,2}\.\d{2}$'
      and split_part(res.performance, '.', 2)::int < 60
  loop
    v_funnet := v_funnet + 1;
    if p_dry then continue; end if;
    begin
      update results set performance = replace(rad.performance, '.', ':') where id = rad.id;
      v_rettet := v_rettet + 1;
    exception when unique_violation then
      delete from results where id = rad.id;
      v_slettet := v_slettet + 1;
    when others then
      v_feil := v_feil + 1;
    end;
  end loop;
  return jsonb_build_object('funnet', v_funnet, 'rettet', v_rettet, 'slettet_dublett', v_slettet, 'feil', v_feil);
end;
$$;
revoke all on function rett_minuttider(boolean) from public, anon, authenticated;

create or replace function test_urimelige_tider()
returns bigint language sql stable security definer set statement_timeout = '110s' set search_path = public as $$
  select count(*) from results r join events e on e.id = r.event_id
  where e.result_type = 'time' and er_langt_loep(e.code) and r.status = 'OK'
    and r.performance_value > 0 and r.performance_value < 6000;
$$;
grant execute on function test_urimelige_tider() to service_role;
