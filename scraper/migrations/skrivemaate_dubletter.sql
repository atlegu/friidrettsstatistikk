-- Samme resultat skrevet på to måter. 17.10.2026.
--
-- To importer i januar 2026 la inn samme løp med ulik skrivemåte: «61.4» og
-- «1:01.40» (samme verdi 6140), ofte med ulikt håndtidsflagg. Funksjonen gir
-- grupper med samme utøver, øvelse, dato og verdi der skrivemåten varierer.
-- rydd_skrivemaate_dubletter.py velger hvilken rad som beholdes.

create or replace function public.skrivemaate_dubletter()
returns jsonb
language sql stable security definer set search_path = public set statement_timeout = '200s'
as $$
  with g as (
    select r.athlete_id, r.event_id, r.date, r.performance_value
    from results r join events e on e.id = r.event_id
    where e.result_type = 'time' and r.performance_value > 0
    group by 1, 2, 3, 4
    having count(*) > 1 and count(distinct r.performance) > 1
  )
  select coalesce(jsonb_agg(jsonb_build_object(
           'id', r.id, 'athlete_id', r.athlete_id, 'event_id', r.event_id, 'date', r.date, 'pv', r.performance_value,
           'performance', r.performance, 'manuell', r.is_manual_time, 'wind', r.wind, 'place', r.place,
           'round', r.round, 'meet_id', r.meet_id, 'lagt', r.created_at, 'kode', e.code)), '[]'::jsonb)
  from g join results r using (athlete_id, event_id, date, performance_value)
  join events e on e.id = r.event_id
$$;
revoke all on function public.skrivemaate_dubletter() from public, anon, authenticated;
