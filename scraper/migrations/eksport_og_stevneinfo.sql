-- Eksport for administratorer, og arrangør/type/krets på stevnesidene. 17.10.2026.
--
-- Eksport (kravspekken §18): bare innloggede administratorer, og hver
-- nedlasting logges (hvem, hva, når, antall rader). Lister med navn og
-- fødselsår er personopplysninger; loggen dokumenterer bruken.
--
-- Stevnesider (§11): arrangør, arrangementstype og krets. Kilden er
-- terminlisten (iSonen-data via friidrett.no), som hent_terminliste.py henter
-- hver natt og kobler til stevnet (terminliste.meet_id). Terminlisten dekker
-- arrangementer fra 2026; eldre stevner har ingen slik kilde.

create table if not exists public.eksport_logg (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users(id),
  epost       text,
  type        text not null,
  parametre   jsonb not null default '{}'::jsonb,
  rader       integer not null default 0,
  tid         timestamptz not null default now()
);
alter table public.eksport_logg enable row level security;
drop policy if exists "Admin leser eksportlogg" on public.eksport_logg;
create policy "Admin leser eksportlogg" on public.eksport_logg for select using ((select public.is_admin()));
drop policy if exists "Admin skriver eksportlogg" on public.eksport_logg;
create policy "Admin skriver eksportlogg" on public.eksport_logg for insert
  with check ((select public.is_admin()) and user_id = (select auth.uid()));
grant select, insert on public.eksport_logg to authenticated;

alter table public.meets add column if not exists arrangementstype text;
alter table public.meets add column if not exists krets text;

-- Arrangør, type, krets og iSonen-lenke fra terminlisten til de koblede
-- stevnene. Overskriver ikke en arrangør som er satt for hånd i admin.
create or replace function public.stevneinfo_fra_terminliste()
returns integer
language sql security definer set search_path = public
as $$
  with oppd as (
    update meets m
    set organizer_name = coalesce(m.organizer_name, t.arrangor),
        arrangementstype = t.type,
        krets = t.krets,
        website = coalesce(m.website, t.url)
    from terminliste t
    where t.meet_id = m.id
      and (m.organizer_name is null or m.arrangementstype is distinct from t.type
           or m.krets is distinct from t.krets or (m.website is null and t.url is not null))
    returning 1
  )
  select count(*)::int from oppd;
$$;
revoke all on function public.stevneinfo_fra_terminliste() from public, anon, authenticated;
