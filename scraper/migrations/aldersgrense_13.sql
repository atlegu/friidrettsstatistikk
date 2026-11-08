-- Offentlig statistikk fra 13 år. 08.11.2026.
--
-- Atles regel: resultatlistene har utøvere ned til 7 år, statistikken lagrer
-- fra 10 år, men bare statistikk for utøvere fra 13 år er offentlig. Hvordan
-- 7-12-åringer skal vises i resultatlistene (stevnesider, utøverprofiler),
-- avklares med NFIF og er ikke endret her.
--
-- Erstatter grensen «til og med 11 år» fra synlighet_barn.sql. To feil rettes:
--   1. 12-åringer var egen aldersgruppe («12») og kom med i lister uten
--      aldersfilter. 151 220 rader.
--   2. Aldersgruppen regnes bare fra full fødselsdato. Barn med bare
--      fødselsår fikk tom aldersgruppe og slapp gjennom filteret
--      «age_group is null or age_group <> 'Yngre'». 126 254 rader.
-- Tørrkjøring 08.11.2026: 277 474 rader skjules (4 544 i 2026), ingen fra
-- 13 år og eldre, og ingen som var skjult blir synlige.
--
-- Grensen står fortsatt ett sted, i skjult_alder(). results_full får kolonnen
-- skjult_barn, som sidene og funksjonene filtrerer på i stedet for
-- aldersgruppen.

create or replace function public.skjult_alder(p_fodt int, p_aar int) returns boolean
language sql immutable as $$
  select p_fodt is not null and p_aar is not null and p_aar - p_fodt <= 12
$$;

-- Samme kolonner som før, pluss skjult_barn til slutt (create or replace view
-- tillater bare nye kolonner bakerst, og personal_bests_detailed avhenger av viewet)
create or replace view public.results_full as
 SELECT r.id,
    r.performance,
    r.performance_value,
    r.date,
    r.wind,
    r.place,
    r.round,
    r.status,
    r.is_pb,
    r.is_sb,
    r.is_national_record,
    r.reaction_time,
    r.attempts,
    r.splits,
    r.verified,
    r.is_manual_time,
    r.is_wind_legal,
    a.id AS athlete_id,
    a.first_name,
    a.last_name,
    a.full_name AS athlete_name,
    a.gender,
    a.birth_date,
    get_age_group(a.birth_date, r.date) AS age_group,
    e.id AS event_id,
    e.code AS event_code,
    e.name AS event_name,
    e.category AS event_category,
    e.result_type,
    m.id AS meet_id,
    m.name AS meet_name,
    m.city AS meet_city,
    m.indoor AS meet_indoor,
    m.level AS meet_level,
    s.id AS season_id,
    s.year AS season_year,
    s.indoor AS season_indoor,
    s.name AS season_name,
    c.id AS club_id,
    c.name AS club_name,
    c.club_type,
    a.nationality AS athlete_nationality,
    skjult_alder(coalesce(extract(year from a.birth_date)::int, a.birth_year),
                 extract(year from r.date)::int) AS skjult_barn
   FROM results r
     JOIN athletes a ON r.athlete_id = a.id
     JOIN events e ON r.event_id = e.id
     JOIN meets m ON r.meet_id = m.id
     JOIN seasons s ON r.season_id = s.id
     LEFT JOIN clubs c ON r.club_id = c.id;

-- Funksjonene er endret flere ganger etter synlighet_barn.sql (blant annet
-- statsborgerskap for norgesrekorder og nasjonalitet i get_all_time_best), så
-- gjeldende definisjon hentes fra basen og bare aldersfilteret byttes:
--   get_all_time_best: aldersgruppen «Yngre» -> kolonnen skjult_barn
--   norgesrekorder, klubbrekorder: alderen regnes også fra fødselsår når full
--   fødselsdato mangler
do $$
declare
  f regprocedure;
  def text;
  ny text;
begin
  for f in select p.oid::regprocedure from pg_proc p join pg_namespace n on n.oid = p.pronamespace
           where n.nspname = 'public' and p.proname in ('klubbrekorder', 'norgesrekorder', 'get_all_time_best')
  loop
    def := pg_get_functiondef(f);
    ny := replace(def, 'skjult_alder(extract(year from a.birth_date)::int,',
                       'skjult_alder(coalesce(extract(year from a.birth_date)::int, a.birth_year),');
    ny := replace(ny, $r$and rf.age_group is distinct from 'Yngre'$r$, 'and rf.skjult_barn is not true');
    if ny = def then
      raise exception 'Fant ikke aldersfilteret i %', f;
    end if;
    execute ny;
  end loop;
end $$;
