-- Anvendt mot produksjon 15.09.2026.
--
-- refresh_plattform_statistikk() oppdaterte ogsaa klubb_bruk, som teller over
-- 1,95 millioner rader og tar to minutter. Supabase sin gateway avbryter alle
-- kall etter 120 s (504) uansett statement_timeout, saa importen fikk alltid
-- feil paa siste steg - selv om serveren fullfoerte.
--
-- Naa: importen oppdaterer bare forsidetallene (sekunder) og merker
-- klubbtallene som utdaterte. pg_cron sjekker hvert kvarter og oppdaterer
-- klubb_bruk i basen naar det trengs, uten noen forespoersel aa vente paa.

create extension if not exists pg_cron with schema pg_catalog;

create table if not exists vedlikehold (
  nokkel text primary key,
  utdatert_siden timestamptz,
  sist_oppdatert timestamptz
);
insert into vedlikehold (nokkel) values ('klubb_bruk') on conflict do nothing;

create or replace function refresh_plattform_statistikk()
returns void language plpgsql security definer
set search_path = public set statement_timeout = '100s' as $$
begin
  refresh materialized view concurrently plattform_statistikk;
  update vedlikehold set utdatert_siden = coalesce(utdatert_siden, now())
   where nokkel = 'klubb_bruk';
end;
$$;

create or replace function refresh_klubb_bruk_hvis_utdatert()
returns text language plpgsql security definer
set search_path = public set statement_timeout = '900s' as $$
declare siden timestamptz;
begin
  select utdatert_siden into siden from vedlikehold where nokkel = 'klubb_bruk';
  if siden is null then return 'ikke utdatert'; end if;
  refresh materialized view concurrently klubb_bruk;
  update vedlikehold set utdatert_siden = null, sist_oppdatert = now()
   where nokkel = 'klubb_bruk';
  return 'oppdatert';
end;
$$;

select cron.unschedule(jobid) from cron.job where jobname = 'refresh_klubb_bruk';
-- Tidsgrensen maa settes i selve jobb-kommandoen: pg_cron respekterer ikke
-- funksjonens egen «set statement_timeout», og jobben roek paa 2 minutter.
select cron.schedule('refresh_klubb_bruk', '*/15 * * * *',
  $$set statement_timeout = '900s'; select refresh_klubb_bruk_hvis_utdatert();$$);

-- Partiell indeks saa «verified = false» kan finnes og tilbakestilles uten
-- full skanning (en update paa kolonnen tidsavbroet via PostgREST uten den).
create index concurrently if not exists results_verified_false_idx on results (id) where verified = false;
