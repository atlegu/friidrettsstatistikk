-- Hjelpefunksjoner for test_fullstendighet.py. Brukes ikke av nettstedet.
-- Anvendt mot produksjon 14.09.2026.
--
-- Testen skal finne de STØRSTE stevnene og utøverne, for det er bare der
-- tusenradstaket i PostgREST slår inn. Opptellingen går over alle 1,95
-- millioner resultatrader og tar rundt ti sekunder, så statement_timeout
-- heves for akkurat disse kallene. Funksjonene leser bare.

create or replace function test_storste_stevner(p_antall integer default 5)
returns table (id uuid, name text, resultater bigint)
language sql
stable
set statement_timeout = '120s'
set search_path = public
as $$
  select m.id, m.name, s.n
  from (select meet_id, count(*) as n
        from results group by meet_id
        order by count(*) desc limit p_antall) s
  join meets m on m.id = s.meet_id
  order by s.n desc;
$$;

create or replace function test_storste_utovere(p_antall integer default 5)
returns table (id uuid, full_name text, resultater bigint)
language sql
stable
set statement_timeout = '120s'
set search_path = public
as $$
  select a.id, a.full_name, s.n
  from (select athlete_id, count(*) as n
        from results where athlete_id is not null
        group by athlete_id
        order by count(*) desc limit p_antall) s
  join athletes a on a.id = s.athlete_id
  order by s.n desc;
$$;

-- Fasit for én klubb. De største har 68 000 resultater, og å bla gjennom
-- dem over REST tar for lang tid. Her er det én indeksert opptelling.
create or replace function test_klubb_fasit(p_klubb uuid)
returns table (resultater bigint, utovere bigint)
language sql
stable
set statement_timeout = '120s'
set search_path = public
as $$
  select count(*), count(distinct athlete_id)
  from results where club_id = p_klubb;
$$;

grant execute on function test_storste_stevner(integer) to service_role;
grant execute on function test_storste_utovere(integer) to service_role;
grant execute on function test_klubb_fasit(uuid) to service_role;

-- Er is_wind_legal i takt med regelen i vindflagg.sql? Alle fire skal vaere 0.
create or replace function test_vindflagg_avvik()
returns table (
  maalt_men_flagg_null bigint,
  umaalt_men_flagg_satt bigint,
  over_2_men_true bigint,
  ikke_vindpaavirket_men_flagg bigint
)
language sql
stable
set statement_timeout = '120s'
set search_path = public
as $$
  select
    count(*) filter (where v and r.wind is not null and r.is_wind_legal is null),
    count(*) filter (where v and r.wind is null and r.is_wind_legal is not null),
    count(*) filter (where v and r.wind > 2.0 and r.is_wind_legal = true),
    count(*) filter (where not v and r.is_wind_legal is not null)
  from results r
  join lateral (select er_vindpaavirket((select code from events e where e.id = r.event_id)) as v) x on true;
$$;

grant execute on function test_vindflagg_avvik() to service_role;
