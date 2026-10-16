-- Utenlandske utøvere i norsk statistikk. 16.10.2026.
--
-- Regel (Atle): utenlandske utøvere står i norske statistikker bare når de
-- representerer en norsk klubb, og da merket med *.
--
-- * Bane: kilden er norsk klubbstatistikk, så utenlandske utøvere der
--   representerer norske klubber. results_full, get_all_time_best() og
--   norgesrekorder() returnerer nå athlete_nationality, og listene viser *.
-- * Gateløp: lop_arsbeste() tar med nasjon NOR, eller utenlandske når
--   lop_norsk_klubb() er sann (klubbnavnet i klubbregisteret, eller koblet
--   til utøver med norsk klubb). Parameteren p_bare_norske er fjernet.
--
-- Fullstendige definisjoner ligger i migreringene results_full_nasjonalitet,
-- nasjonalitet_i_lister og gatelop_norsk_klubb i Supabase.
create index if not exists clubs_lower_name on public.clubs (lower(name));
create or replace function public.lop_norsk_klubb(p_klubb text, p_athlete_id uuid) returns boolean
language sql stable set search_path = public as $$
  select exists (select 1 from clubs c where lower(c.name) = lower(trim(p_klubb)))
      or exists (select 1 from athletes a where a.id = p_athlete_id and a.current_club_id is not null)
$$;
