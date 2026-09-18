-- Grunnlaget for klubbens statistikkside (/klubber/[id]/statistikk) i ett
-- kall: aktivitet per år, sesongen i år og de mest aktive utøverne i år.
-- Anvendt mot produksjon 18.09.2026. Radene for klubben hentes én gang
-- (materialized): uten det brettet planleggeren uttrykket inn tre ganger
-- og brukte 14 s, med tar det 0,2 s.
create or replace function klubb_statistikk(p_klubb uuid)
returns jsonb
language sql
stable
security definer
set statement_timeout = '60s'
set search_path = public
as $$
  with r as materialized (
    select r.id, r.athlete_id, r.meet_id, r.date, extract(year from r.date)::int as aar
    from results r where r.club_id = p_klubb and r.status = 'OK'
  ),
  per_aar as (
    select aar, count(*) as resultater, count(distinct athlete_id) as utovere, count(distinct meet_id) as stevner
    from r where aar >= extract(year from current_date)::int - 12 group by aar order by aar
  ),
  i_aar as (
    select count(*) as resultater, count(distinct athlete_id) as utovere, count(distinct meet_id) as stevner
    from r where aar = extract(year from current_date)::int
  ),
  topp as (
    select a.id, a.full_name, a.birth_year, count(*) as resultater, count(distinct r.meet_id) as stevner
    from r join athletes a on a.id = r.athlete_id
    where r.aar = extract(year from current_date)::int
    group by a.id, a.full_name, a.birth_year
    order by count(*) desc, count(distinct r.meet_id) desc limit 10
  )
  select jsonb_build_object(
    'per_aar', (select coalesce(jsonb_agg(to_jsonb(per_aar)), '[]'::jsonb) from per_aar),
    'i_aar', (select to_jsonb(i_aar) from i_aar),
    'topp', (select coalesce(jsonb_agg(to_jsonb(topp)), '[]'::jsonb) from topp)
  );
$$;
grant execute on function klubb_statistikk(uuid) to anon, authenticated, service_role;
