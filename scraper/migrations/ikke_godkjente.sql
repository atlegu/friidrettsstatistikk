-- Ikke godkjente resultater. 17.10.2026.
--
-- Kilden (minfriidrettsstatistikk.info) viser på utøversiden en egen tabell
-- «Ikke godkjente resultater» med årsak: kort bane, ikke medlem av NFIF,
-- feilkoblet startutstyr, for stor innendørsbane, ekstraløp, suspensjon ...
-- Importen leste tabellen, men basen hadde ikke noe sted for årsaken, så
-- resultatene ble lagt inn som godkjente (Kåre Strande 200 m 23.24, kort bane).
--
--   ikke_godkjent_aarsak  kildens årsak, ordrett. NULL = godkjent.
--   status IKKE_GODKJENT  settes for alle årsaker unntatt ren vind («For mye
--                         vind», «Manglende informasjon om vind»), som
--                         vindregelen allerede håndterer (is_wind_legal).
-- Alle lister som krever status = 'OK' holder dermed disse utenfor.
--
--   kilde_utover_kontroll  hvilke utøversider som er gjennomgått, så
--                          hent_ikke_godkjente.py kan fortsette der den slapp.

alter type public.result_status add value if not exists 'IKKE_GODKJENT';

alter table public.results add column if not exists ikke_godkjent_aarsak text;
create index if not exists results_ikke_godkjent on public.results (athlete_id) where ikke_godkjent_aarsak is not null;

create table if not exists public.kilde_utover_kontroll (
  athlete_id       uuid primary key references public.athletes(id) on delete cascade,
  kontrollert      timestamptz not null default now(),
  ikke_godkjente   integer not null default 0,
  merket           integer not null default 0,
  ikke_funnet      integer not null default 0,
  feil             text
);
alter table public.kilde_utover_kontroll enable row level security;

-- Neste utøvere som skal kontrolleres: har kilde-id og resultater, ikke
-- kontrollert (eller kontrollert før p_eldre_enn). Nyest aktive først.
create or replace function public.utovere_til_kontroll(p_antall int default 1000, p_eldre_enn interval default null)
returns jsonb
language sql stable security definer set search_path = public set statement_timeout = '120s'
as $$
  select coalesce(jsonb_agg(jsonb_build_object('id', x.id, 'external_id', x.external_id, 'navn', x.full_name)), '[]'::jsonb)
  from (
    select a.id, a.external_id, a.full_name, max(r.date) siste
    from athletes a join results r on r.athlete_id = a.id
    left join kilde_utover_kontroll k on k.athlete_id = a.id
    where a.external_id is not null
      and (k.athlete_id is null or (p_eldre_enn is not null and k.kontrollert < now() - p_eldre_enn))
    group by a.id
    order by max(r.date) desc
    limit p_antall
  ) x
$$;
revoke all on function public.utovere_til_kontroll(int, interval) from public, anon, authenticated;

-- Logg over rader hent_ikke_godkjente.py har merket (for å kunne rulle tilbake)
create table if not exists public.opprydding_ikke_godkjente (
  id bigint generated always as identity primary key,
  result_id uuid not null, gammel_status text, aarsak text, tid timestamptz default now());
alter table public.opprydding_ikke_godkjente enable row level security;
