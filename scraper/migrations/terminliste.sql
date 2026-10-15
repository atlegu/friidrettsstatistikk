-- Terminlistekontroll. 15.10.2026.
--
-- terminliste: arrangementene i terminlisten på friidrett.no (bygget fra
-- iSonen, pluss løp fra EQ Timing), hentet hver natt av hent_terminliste.py
-- og koblet mot stevnene (bane) eller løpene (gateløp) vi har resultater fra.
-- terminliste_oppfolging: purring, avlysning og «ingen resultater forventet»,
-- ført fra /admin/terminliste. Skriptet rører ikke denne tabellen.

create table if not exists public.terminliste (
  isonen_id          text primary key,
  tittel             text not null,
  krets              text,
  type               text,
  kategori           text not null check (kategori in ('bane', 'gate')),
  arrangor           text,
  sted               text,
  start_dato         date not null,
  slutt_dato         date not null,
  url                text,
  antall_ovelser     integer,
  meet_id            uuid references public.meets(id) on delete set null,
  lop_arrangement_id uuid references public.lop_arrangement(id) on delete set null,
  antall_resultater  integer not null default 0,
  liveres_id         integer,
  sist_sett          timestamptz not null default now(),
  oppdatert          timestamptz not null default now()
);
create index if not exists terminliste_dato on public.terminliste (kategori, slutt_dato desc);

create table if not exists public.terminliste_oppfolging (
  isonen_id     text primary key references public.terminliste(isonen_id) on delete cascade,
  status        text not null check (status in ('purret', 'avlyst', 'ingen_resultater')),
  purret_dato   date,
  purringer     integer not null default 0,
  kommentar     text,
  behandlet_av  uuid,
  behandlet_tid timestamptz not null default now()
);

alter table public.terminliste enable row level security;
alter table public.terminliste_oppfolging enable row level security;
drop policy if exists "Admin leser terminliste" on public.terminliste;
create policy "Admin leser terminliste" on public.terminliste for select to authenticated using (public.is_admin());
drop policy if exists "Admin leser oppfølging" on public.terminliste_oppfolging;
create policy "Admin leser oppfølging" on public.terminliste_oppfolging for select to authenticated using (public.is_admin());
drop policy if exists "Admin skriver oppfølging" on public.terminliste_oppfolging;
create policy "Admin skriver oppfølging" on public.terminliste_oppfolging for all to authenticated
  using (public.is_admin()) with check (public.is_admin());
revoke all on public.terminliste, public.terminliste_oppfolging from anon;
grant select on public.terminliste to authenticated;
grant select, insert, update, delete on public.terminliste_oppfolging to authenticated;

create or replace function public.terminliste_stevner(p_fra date, p_til date)
returns table (id uuid, name text, city text, start_date date, end_date date, resultater bigint)
language sql stable security definer set search_path = public
as $$
  select m.id, m.name, m.city, m.start_date, coalesce(m.end_date, m.start_date), count(r.id)
  from meets m left join results r on r.meet_id = m.id
  where m.start_date between p_fra and p_til
  group by m.id;
$$;
revoke all on function public.terminliste_stevner(date, date) from public, anon, authenticated;

-- lop_oversikt får kilde_id, så EQ Timing-arrangementer i terminlisten kan kobles på id
create or replace view public.lop_oversikt with (security_invoker = true) as
select a.id, a.navn, a.dato, a.sted, a.arrangor, a.gren, a.nivaa, a.kilde,
       count(r.id) as lopere,
       count(r.athlete_id) as koblet,
       min(l.kvalitetsnivaa) as beste_nivaa,
       array_agg(distinct l.distanse_m order by l.distanse_m) filter (where l.distanse_m > 0) as distanser,
       a.kilde_id
from lop_arrangement a
join lop_lop l on l.arrangement_id = a.id
left join lop_resultat r on r.lop_id = l.id
group by a.id;
