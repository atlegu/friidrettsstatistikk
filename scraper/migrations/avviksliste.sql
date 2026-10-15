-- Avviksliste: automatiske kontroller som legger funn i en arbeidsliste
-- for administrator. 15.10.2026.
--
-- Hver natt etter importen kjører finn_avvik() kontrollene under på
-- resultater fra de siste 14 dagene, og på resultater lagt inn de siste to
-- døgnene uansett dato. Funn som alt står i listen, legges ikke inn på nytt
-- (nokkel er unik), så et behandlet avvik dukker ikke opp igjen.
--
-- Kontroller:
--   mulig_rekord     resultatet er nå beste norske resultat i øvelsen (ute/inne)
--   stor_forbedring  mer enn 10 % (tid), 15 % (lengde/høyde) eller 20 % (poeng)
--                    bedre enn utøverens beste de siste 18 månedene, fra 16 år
--   urimelig_tid     tid under det som er mulig på distansen (minste_hundredeler)
--   mangler_vind     vindavhengig øvelse ute uten vindmåling, én post per
--                    stevne og øvelse
--   mangler_kjonn    utøver med resultater i perioden uten kjønn
--   mangler_alder    utøver med resultater i perioden uten fødselsår
--
-- IO: alle kontroller går via indekser. mulig_rekord kjøres bare for øvelser
-- med resultater i perioden.

create table if not exists public.avvik (
  id            bigserial primary key,
  type          text not null,
  nokkel        text not null unique,
  alvorlighet   smallint not null default 2 check (alvorlighet between 1 and 3),
  result_id     uuid references public.results(id) on delete cascade,
  athlete_id    uuid references public.athletes(id) on delete cascade,
  meet_id       uuid references public.meets(id) on delete cascade,
  event_id      uuid references public.events(id) on delete set null,
  dato          date,
  detaljer      jsonb not null default '{}'::jsonb,
  oppdaget      timestamptz not null default now(),
  status        text not null default 'aapen'
                check (status in ('aapen', 'godkjent', 'rettet', 'underkjent')),
  behandlet_av  uuid,
  behandlet_tid timestamptz,
  kommentar     text
);

create index if not exists avvik_status_idx on public.avvik (status, alvorlighet, dato desc);
create index if not exists avvik_result_idx on public.avvik (result_id);
create index if not exists avvik_athlete_idx on public.avvik (athlete_id);
create index if not exists avvik_meet_idx on public.avvik (meet_id);

alter table public.avvik enable row level security;
drop policy if exists "Admin leser avvik" on public.avvik;
create policy "Admin leser avvik" on public.avvik for select to authenticated using (public.is_admin());
drop policy if exists "Admin behandler avvik" on public.avvik;
create policy "Admin behandler avvik" on public.avvik for update to authenticated
  using (public.is_admin()) with check (public.is_admin());
revoke all on public.avvik from anon;
grant select, update on public.avvik to authenticated;


create or replace function public.finn_avvik(
  p_fra date default (current_date - 14),
  p_til date default current_date,
  p_nylig interval default interval '2 days'
) returns jsonb
language plpgsql
security definer
set search_path = public
set statement_timeout = '600s'
as $$
declare
  ut jsonb := '{}'::jsonb;
  n int;
  ev uuid[];
begin
  -- Resultatene som kontrolleres: konkurransedato i perioden, eller lagt inn nylig.
  drop table if exists _avvik_r;
  create temp table _avvik_r on commit drop as
    with utvalg as (
      select id from results where date between p_fra and p_til
      union
      select id from results where created_at >= now() - p_nylig
    )
    select r.id, r.athlete_id, r.event_id, r.meet_id, r.date, r.performance_value pv,
           r.wind, e.code, e.category, e.result_type::text rt,
           m.indoor, a.gender, a.birth_date, a.birth_year,
           coalesce(extract(year from r.date)::int
                    - coalesce(a.birth_year, extract(year from a.birth_date)::int) >= 16, false) fra16
    from utvalg u
    join results r on r.id = u.id
    join events e on e.id = r.event_id
    join meets m on m.id = r.meet_id
    join athletes a on a.id = r.athlete_id
    where r.status = 'OK' and r.performance_value > 0 and e.category <> 'relay';

  -- 1. Mulig ny norsk rekord / bestenotering
  select array_agg(distinct event_id) into ev from _avvik_r;
  if ev is not null then
    with rek as (
      select k.kjonn, i.inne, nr.*
      from (values ('M'), ('F')) k(kjonn)
      cross join (values (false), (true)) i(inne)
      cross join lateral norgesrekorder(ev, k.kjonn, null, i.inne) nr
    ), ny as (
      insert into avvik (type, nokkel, alvorlighet, result_id, athlete_id, meet_id, event_id, dato, detaljer)
      select 'mulig_rekord', 'mulig_rekord:' || rek.result_id, 1, rek.result_id, rek.athlete_id,
             rek.meet_id, rek.event_id, rek.date, jsonb_build_object('inne', rek.inne)
      from rek join _avvik_r r on r.id = rek.result_id
      on conflict (nokkel) do nothing
      returning 1)
    select count(*) into n from ny;
    ut := ut || jsonb_build_object('mulig_rekord', n);
  end if;

  -- 2. Stor forbedring av personlig rekord
  with c as (
    select r.*, pb.forrige, pb.forrige_dato
    from _avvik_r r
    cross join lateral (
      select r2.performance_value forrige, r2.date forrige_dato
      from results r2
      where r2.athlete_id = r.athlete_id and r2.event_id = r.event_id
        and r2.status = 'OK' and r2.performance_value > 0 and r2.date < r.date
        and r2.date >= r.date - interval '18 months'
      order by case when r.rt = 'time' then r2.performance_value else -r2.performance_value end
      limit 1
    ) pb
    where r.fra16
  ), ny as (
    insert into avvik (type, nokkel, alvorlighet, result_id, athlete_id, meet_id, event_id, dato, detaljer)
    select 'stor_forbedring', 'stor_forbedring:' || c.id, 2, c.id, c.athlete_id, c.meet_id, c.event_id, c.date,
           jsonb_build_object('forrige', c.forrige, 'forrige_dato', c.forrige_dato,
             'endring_pst', round(100 * abs(c.pv - c.forrige)::numeric / c.forrige, 1))
    from c
    where (c.rt = 'time' and c.forrige::numeric / c.pv > 1.10)
       or (c.rt in ('distance', 'height') and c.pv::numeric / c.forrige > 1.15)
       or (c.rt = 'points' and c.pv::numeric / c.forrige > 1.20)
    on conflict (nokkel) do nothing
    returning 1)
  select count(*) into n from ny;
  ut := ut || jsonb_build_object('stor_forbedring', n);

  -- 3. Urimelig tid
  with ny as (
    insert into avvik (type, nokkel, alvorlighet, result_id, athlete_id, meet_id, event_id, dato, detaljer)
    select 'urimelig_tid', 'urimelig_tid:' || r.id, 1, r.id, r.athlete_id, r.meet_id, r.event_id, r.date,
           jsonb_build_object('minste', minste_hundredeler(r.code))
    from _avvik_r r
    where r.rt = 'time' and r.pv < minste_hundredeler(r.code)
    on conflict (nokkel) do nothing
    returning 1)
  select count(*) into n from ny;
  ut := ut || jsonb_build_object('urimelig_tid', n);

  -- 4. Mangler vind, én post per stevne og øvelse
  with g as (
    select r.meet_id, r.event_id, min(r.date) dato, count(*) antall
    from _avvik_r r
    where er_vindpaavirket(r.code) and r.indoor is not true and r.wind is null
    group by 1, 2
  ), ny as (
    insert into avvik (type, nokkel, alvorlighet, meet_id, event_id, dato, detaljer)
    select 'mangler_vind', 'mangler_vind:' || g.meet_id || ':' || g.event_id, 3, g.meet_id, g.event_id,
           g.dato, jsonb_build_object('antall', g.antall)
    from g
    on conflict (nokkel) do nothing
    returning 1)
  select count(*) into n from ny;
  ut := ut || jsonb_build_object('mangler_vind', n);

  -- 5 og 6. Utøvere uten kjønn eller fødselsår
  with g as (
    select r.athlete_id, max(r.date) dato, count(*) antall,
           bool_or(r.gender is null) uten_kjonn,
           bool_or(r.birth_date is null and r.birth_year is null) uten_alder
    from _avvik_r r
    group by 1
  ), ny as (
    insert into avvik (type, nokkel, alvorlighet, athlete_id, dato, detaljer)
    select t.type, t.type || ':' || g.athlete_id, 2, g.athlete_id, g.dato,
           jsonb_build_object('antall', g.antall)
    from g
    cross join lateral (values ('mangler_kjonn', g.uten_kjonn), ('mangler_alder', g.uten_alder)) t(type, gjelder)
    where t.gjelder
    on conflict (nokkel) do nothing
    returning 1)
  select count(*) into n from ny;
  ut := ut || jsonb_build_object('mangler_kjonn_eller_alder', n);

  return ut || jsonb_build_object('kontrollert', (select count(*) from _avvik_r), 'fra', p_fra, 'til', p_til);
end;
$$;

revoke all on function public.finn_avvik(date, date, interval) from public, anon, authenticated;

-- Hver natt kl. 04.30 norsk sommertid, etter importen (01.37 UTC)
select cron.schedule('finn_avvik', '30 2 * * *', $$set statement_timeout = '600s'; select public.finn_avvik();$$);

-- Første fylling 15.10.2026, ett kvartal om gangen:
--   select finn_avvik('2026-01-01','2026-03-31', interval '0 seconds');
--   select finn_avvik('2026-04-01','2026-06-30', interval '0 seconds');
--   select finn_avvik('2026-07-01','2026-10-15');
-- Ga 301 avvik for 54 198 resultater.
