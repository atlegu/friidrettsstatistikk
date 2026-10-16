-- Offisielle norske mastersrekorder. 16.10.2026.
--
-- Rekordlistene (Stein Fossen; kappgang Erling Andersen) er kontrollert mot
-- basen og manglende rekorder lagt inn (masters_rekorder_fra_liste.py).
-- Denne tabellen sier hvilke resultater som er godkjente rekorder.
--
-- Mastersvisningen holder ellers utenfor resultater uten vindmåling i
-- vindøvelser og manuelle tider i sprint og hekk. Godkjente rekorder tas
-- alltid med: mange eldre rekorder har ingen vind oppgitt, og noen klasser
-- har bare en manuell rekord (K100 100 m: 76.6).

create table if not exists public.masters_offisielle_rekorder (
  result_id          uuid primary key references public.results(id) on delete cascade,
  liste              text not null,          -- mvu, kvu, mvi, kvi
  klasse             text not null,          -- M35-39, K80-84 ...
  offisielt_resultat text not null,
  lagt_til           timestamptz not null default now()
);
alter table public.masters_offisielle_rekorder enable row level security;
drop policy if exists "Offisielle rekorder er offentlige" on public.masters_offisielle_rekorder;
create policy "Offisielle rekorder er offentlige" on public.masters_offisielle_rekorder for select using (true);
grant select on public.masters_offisielle_rekorder to anon, authenticated;

drop materialized view if exists public.masters_resultater;
create materialized view public.masters_resultater as
select r.id as result_id, r.athlete_id, r.event_id, r.meet_id, r.club_id, r.date, r.performance,
       r.performance_value, r.wind, a.gender, a.full_name,
       coalesce(a.birth_year, extract(year from a.birth_date)::int) as fodt,
       'V' || (((extract(year from r.date)::int - coalesce(a.birth_year, extract(year from a.birth_date)::int)) / 5) * 5) as klasse,
       -- Kastene på innendørsmesterskap for masters foregår ute (Toruń):
       -- spyd, diskos og slegge regnes alltid som ute, og en godkjent rekord
       -- står i den lista rekordkomiteen har ført den i.
       case when o.liste is not null then o.liste in ('mvi', 'kvi')
            when e.code ~ '^(spyd|diskos|slegge)' then false
            else coalesce(m.indoor, false) end as inne,
       e.result_type::text as result_type,
       (o.result_id is not null) as offisiell
from athletes a
join results r on r.athlete_id = a.id
join events e on e.id = r.event_id
join meets m on m.id = r.meet_id
left join masters_offisielle_rekorder o on o.result_id = r.id
where coalesce(a.birth_year, extract(year from a.birth_date)::int) <= extract(year from current_date)::int - 35
  and extract(year from r.date)::int - coalesce(a.birth_year, extract(year from a.birth_date)::int) >= 35
  and a.gender in ('M', 'F')
  and r.status = 'OK' and r.performance_value > 0
  and e.category <> 'relay'
  and (o.result_id is not null or not (e.category in ('sprint', 'hurdles') and r.is_manual_time is true))
  and (o.result_id is not null or not (er_vindpaavirket(e.code) and m.indoor is not true and r.is_wind_legal is not true));

create unique index masters_resultater_id on public.masters_resultater (result_id);
create index masters_resultater_klasse on public.masters_resultater (gender, klasse, inne, event_id, performance_value);
