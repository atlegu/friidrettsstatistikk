-- Kandidatpar for avkortede tider med presis tvilling. 17.10.2026.
--
-- Importen i januar 2026 lagret mange tider avkortet: «13:42» for 13:42.78,
-- «1.15» for 1:15.44 på 400 m, «1:20:00» for 1:20:52. Senere importer la inn
-- den presise tiden ved siden av uten å kjenne igjen den gamle raden.
-- Funksjonen gir alle par (avkortet rad, presis rad) for samme utøver og
-- øvelse (kappgang_3000_m og 3000mg regnes som samme øvelse) innen ti dager.
-- rydd_avkortede_tider.py velger ett presist motstykke per avkortet rad.

-- Ett JSON-svar: PostgREST gir ellers maks 1 000 rader per kall.
drop function if exists public.avkortede_dubletter();
create or replace function public.avkortede_dubletter()
returns jsonb
language sql stable security definer set search_path = public set statement_timeout = '300s'
as $$
  with fam as (
    select id, case when code ~ '^kappgang_\d+_m$' then regexp_replace(code, '^kappgang_(\d+)_m$', '\1mg') else code end fam
    from events where result_type = 'time'
  ), kort as (
    select r.id, r.athlete_id, r.date, r.performance, r.meet_id, r.created_at, f.fam
    from results r join fam f on f.id = r.event_id
    where r.performance ~ '^\d+:\d\d(:\d\d)?$' or r.performance ~ '^\d\.\d\d$'
  )
  select coalesce(jsonb_agg(jsonb_build_object(
           'kort_id', k.id, 'presis_id', p.id, 'athlete_id', k.athlete_id, 'fam', k.fam,
           'kort', k.performance, 'presis', p.performance, 'kort_dato', k.date, 'presis_dato', p.date,
           'kort_stevne', k.meet_id, 'presis_stevne', p.meet_id, 'kort_lagt', k.created_at)), '[]'::jsonb)
  from kort k
  join results p on p.athlete_id = k.athlete_id and p.id <> k.id and p.date between k.date - 10 and k.date + 10
  join fam fp on fp.id = p.event_id and fp.fam = k.fam
  where p.performance like k.performance || '.%'
     or (k.performance ~ '^\d\.\d\d$' and p.performance like replace(k.performance, '.', ':') || '.%')
     or (k.performance ~ ':00$' and p.performance ~ ':' and p.performance <> k.performance
         and left(p.performance, length(k.performance) - 2) = left(k.performance, length(k.performance) - 2))
$$;
revoke all on function public.avkortede_dubletter() from public, anon, authenticated;

create table if not exists public.opprydding_avkortede (
  result_id uuid primary key, rad jsonb not null, presis_id uuid, tid timestamptz default now());
alter table public.opprydding_avkortede enable row level security;
