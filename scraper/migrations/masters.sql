-- Masters-statistikk i samme base som resten. 15.10.2026.
--
-- Masters er utøvere fra 35 år, i femårsklasser (V35, V40, ...), etter
-- kalenderårsprinsippet: klasse = konkurranseår − fødselsår. Redskap og
-- hekkehøyder ligger allerede i øvelseskoden (kule_5kg, 80mh_76_2cm osv.),
-- så en masters-rekord er beste resultat i klassen per øvelseskode.
--
-- masters_resultater er et materialisert utvalg (ca. 98 600 rader) som gjør
-- rekordsiden rask. Den bygges om hver mandag; ombyggingen leser hele
-- resultattabellen én gang (ca. 10 s).
--
-- Reglene er de samme som for norgesrekorder(): bare godkjente resultater,
-- ikke håndtid i sprint og hekk, og lovlig vind ute der vind teller.

drop materialized view if exists public.masters_resultater cascade;
create materialized view public.masters_resultater as
select r.id as result_id, r.athlete_id, r.event_id, r.meet_id, r.club_id, r.date,
       r.performance, r.performance_value, r.wind,
       a.gender, a.full_name, coalesce(a.birth_year, extract(year from a.birth_date)::int) as fodt,
       'V' || (((extract(year from r.date)::int
                 - coalesce(a.birth_year, extract(year from a.birth_date)::int)) / 5) * 5) as klasse,
       coalesce(m.indoor, false) as inne,
       e.result_type::text as result_type
from athletes a
join results r on r.athlete_id = a.id
join events e on e.id = r.event_id
join meets m on m.id = r.meet_id
where coalesce(a.birth_year, extract(year from a.birth_date)::int) <= extract(year from current_date)::int - 35
  and extract(year from r.date)::int - coalesce(a.birth_year, extract(year from a.birth_date)::int) >= 35
  and a.gender in ('M', 'F')
  and r.status = 'OK' and r.performance_value > 0
  and e.category <> 'relay'
  and not (e.category in ('sprint', 'hurdles') and r.is_manual_time is true)
  and not (er_vindpaavirket(e.code) and m.indoor is not true and r.is_wind_legal is not true);

create unique index masters_resultater_id on public.masters_resultater (result_id);
create index masters_resultater_klasse on public.masters_resultater (gender, klasse, inne, event_id, performance_value);

revoke all on public.masters_resultater from anon, authenticated;

drop function if exists public.masters_rekorder(text, text, boolean);
create function public.masters_rekorder(p_kjonn text, p_klasse text, p_inne boolean default false)
returns table (event_id uuid, event_name text, event_code text, sort_order int, result_type text,
               result_id uuid, performance text, performance_value int, wind numeric, athlete_id uuid,
               athlete_name text, fodt int, club_name text, meet_id uuid, meet_name text, meet_city text,
               date date, antall_utovere bigint)
language sql stable security definer set search_path = public
as $$
  with klasse as (
    select * from masters_resultater
    where gender = p_kjonn and klasse = p_klasse and inne = p_inne
  ), beste as (
    select distinct on (k.event_id) k.*
    from klasse k
    order by k.event_id,
             case when k.result_type = 'time' then k.performance_value else -k.performance_value end,
             k.date
  ), bredde as (
    select k.event_id, count(distinct k.athlete_id) n from klasse k group by 1
  )
  select b.event_id, e.name, e.code, e.sort_order, b.result_type, b.result_id, b.performance,
         b.performance_value, b.wind, b.athlete_id, b.full_name, b.fodt, c.name, b.meet_id, m.name,
         m.city, b.date, br.n
  from beste b
  join events e on e.id = b.event_id
  join meets m on m.id = b.meet_id
  join bredde br on br.event_id = b.event_id
  left join clubs c on c.id = b.club_id
  order by e.sort_order nulls last, e.name;
$$;

grant execute on function public.masters_rekorder(text, text, boolean) to anon, authenticated;

create or replace function public.masters_oversikt()
returns table (klasse text, gender text, resultater bigint, utovere bigint)
language sql stable security definer set search_path = public
as $$
  select klasse, gender, count(*), count(distinct athlete_id)
  from masters_resultater group by 1, 2;
$$;
grant execute on function public.masters_oversikt() to anon, authenticated;

-- Bygges om hver mandag kl. 03.00 UTC
select cron.schedule('masters_resultater', '0 3 * * 1',
  $$set statement_timeout = '600s'; refresh materialized view concurrently public.masters_resultater;$$);

