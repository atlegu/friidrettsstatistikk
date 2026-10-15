-- Gateløp: prototype for løp utenfor bane. 15.10.2026.
--
-- Egen modell ved siden av baneresultatene, fordi løp utenfor bane har
-- egenskaper banen ikke har: løype og løypemåling, distanse som ikke er en
-- øvelseskode, tidtaker som kilde, og mange deltakere uten lisens.
--
--   lop_arrangement  ett arrangement (stevne) hos en tidtaker
--   lop_lop          én konkurranse i arrangementet, med distanse og løypegrad
--   lop_resultat     én løper i én konkurranse, koblet til utøverregisteret
--                    når navn, kjønn og fødselsår gir ett entydig treff
--
-- Kvalitetsnivå (kravspekken §6), avledet maskinelt:
--   A  sertifisert målt løype (A- eller B-måling) og offisiell distanse
--   B  sertifisert målt løype (C-måling), eller offisiell distanse i et løp
--      på terminlisten
--   C  øvrige: ikke målt løype eller distanse som ikke er standard

create table if not exists public.lop_arrangement (
  id          uuid primary key default gen_random_uuid(),
  kilde       text not null,
  kilde_id    bigint not null,
  navn        text not null,
  dato        date not null,
  sted        text,
  arrangor    text,
  gren        text,
  nivaa       text,
  forbund     text,
  hentet      timestamptz not null default now(),
  unique (kilde, kilde_id)
);

create table if not exists public.lop_lop (
  id              uuid primary key default gen_random_uuid(),
  arrangement_id  uuid not null references public.lop_arrangement(id) on delete cascade,
  kilde_id        bigint not null,
  navn            text,
  distanse_m      integer,
  loypegrad       text,
  ranking         boolean not null default false,
  kvalitetsnivaa  char(1) not null default 'C' check (kvalitetsnivaa in ('A', 'B', 'C')),
  unique (arrangement_id, kilde_id, distanse_m)
);

create table if not exists public.lop_resultat (
  id          uuid primary key default gen_random_uuid(),
  lop_id      uuid not null references public.lop_lop(id) on delete cascade,
  kilde_id    bigint not null,
  plass       integer,
  navn        text not null,
  kjonn       char(1),
  fodt        integer,
  klubb       text,
  klasse      text,
  tid_ms      integer,
  status      text not null default 'OK',
  athlete_id  uuid references public.athletes(id) on delete set null,
  unique (lop_id, kilde_id)
);

create index if not exists lop_arrangement_dato on public.lop_arrangement (dato desc);
create index if not exists lop_lop_arr on public.lop_lop (arrangement_id);
create index if not exists lop_lop_dist on public.lop_lop (distanse_m, kvalitetsnivaa);
create index if not exists lop_resultat_lop on public.lop_resultat (lop_id, plass);
create index if not exists lop_resultat_athlete on public.lop_resultat (athlete_id);
create index if not exists lop_resultat_tid on public.lop_resultat (lop_id, kjonn, tid_ms);

alter table public.lop_arrangement enable row level security;
alter table public.lop_lop enable row level security;
alter table public.lop_resultat enable row level security;
drop policy if exists "Løp er offentlige" on public.lop_arrangement;
create policy "Løp er offentlige" on public.lop_arrangement for select using (true);
drop policy if exists "Løp er offentlige" on public.lop_lop;
create policy "Løp er offentlige" on public.lop_lop for select using (true);
drop policy if exists "Løp er offentlige" on public.lop_resultat;
create policy "Løp er offentlige" on public.lop_resultat for select using (true);
grant select on public.lop_arrangement, public.lop_lop, public.lop_resultat to anon, authenticated;

-- Oversikt over arrangementene med antall løpere og beste kvalitetsnivå
create or replace view public.lop_oversikt with (security_invoker = true) as
select a.id, a.navn, a.dato, a.sted, a.arrangor, a.gren, a.nivaa, a.kilde,
       count(r.id) as lopere,
       count(r.athlete_id) as koblet,
       min(l.kvalitetsnivaa) as beste_nivaa,
       array_agg(distinct l.distanse_m order by l.distanse_m) filter (where l.distanse_m > 0) as distanser
from lop_arrangement a
join lop_lop l on l.arrangement_id = a.id
left join lop_resultat r on r.lop_id = l.id
group by a.id;
grant select on public.lop_oversikt to anon, authenticated;

-- Årsbeste per distanse, én rad per løper, innenfor valgte kvalitetsnivåer
create or replace function public.lop_arsbeste(p_aar int, p_distanse int, p_kjonn text,
                                               p_nivaa text[] default array['A', 'B'],
                                               p_antall int default 100)
returns table (plass bigint, resultat_id uuid, navn text, fodt int, klubb text, tid_ms int,
               athlete_id uuid, lop_navn text, arrangement_id uuid, dato date, sted text,
               kvalitetsnivaa char(1))
language sql stable set search_path = public
as $$
  with beste as (
    select distinct on (coalesce(r.athlete_id::text, lower(r.navn) || coalesce(r.fodt::text, '')))
           r.id, r.navn, r.fodt, r.klubb, r.tid_ms, r.athlete_id, l.navn lop_navn,
           a.id arr_id, a.navn arr_navn, a.dato, a.sted, l.kvalitetsnivaa
    from lop_resultat r
    join lop_lop l on l.id = r.lop_id
    join lop_arrangement a on a.id = l.arrangement_id
    where l.distanse_m = p_distanse and l.kvalitetsnivaa = any (p_nivaa)
      and extract(year from a.dato) = p_aar
      and r.kjonn = p_kjonn and r.status = 'OK' and r.tid_ms > 0
    order by coalesce(r.athlete_id::text, lower(r.navn) || coalesce(r.fodt::text, '')), r.tid_ms
  )
  select row_number() over (order by tid_ms), id, navn, fodt, klubb, tid_ms, athlete_id,
         arr_navn, arr_id, dato, sted, kvalitetsnivaa
  from beste order by tid_ms limit p_antall;
$$;
grant execute on function public.lop_arsbeste(int, int, text, text[], int) to anon, authenticated;

-- Tillegg samme dag:
-- Merknad på løp der distansen må kontrolleres (vinnertid raskere enn
-- verdensrekordfart, 120 ms per meter).
alter table public.lop_lop add column if not exists merknad text;
-- Unik også når distansen er ukjent, så en ny import ikke dupliserer løpet.
alter table public.lop_lop drop constraint if exists lop_lop_arrangement_id_kilde_id_distanse_m_key;
alter table public.lop_lop add constraint lop_lop_unik unique nulls not distinct (arrangement_id, kilde_id, distanse_m);
-- Bare gateløp og «Annet» rangeres på distanse. Terreng-, motbakke-, fjell-
-- og ultraløp er registrert aktivitet (nivå C).
update public.lop_lop l set kvalitetsnivaa = 'C'
from public.lop_arrangement a
where a.id = l.arrangement_id and l.kvalitetsnivaa <> 'C'
  and coalesce(a.gren, '') not in ('Gateløp', 'Annet', 'Annet/Kombinert');
