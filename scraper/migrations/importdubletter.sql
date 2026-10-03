-- Dubletter fra importkjøringene 24.08–06.09.2026 (historiske sesonger hentet på nytt).
-- Se OPERATIONS_LOG 2026-10-03. Selve oppryddingen kjøres av scraper/rydd_importdubletter.py.
--
-- Funn: av 401 108 rader lagt inn i perioden hadde 292 460 en eldre tvilling. Flerdagsstevner
-- ligger i basen som én post per dag med riktig dato; importen ga alle kildens resultater
-- startdatoen og la dem i én post (posten med kildens stevne-id), og avstemmingen så bare den
-- posten. Resultatene fra dag 2, 3 ... ble derfor lagt inn på nytt, med feil dato. I tillegg
-- kom rader inn på nytt i samme post der plass eller vind var ulik (den unike indeksen
-- results_innhold_unik omfatter begge). Roten er rettet i update_results.py (søskenposter).
--
-- Regel: en rad N lagt inn i [p_fra, p_til) er en dublett når en ELDRE rad E fra en annen
-- importdag har samme utøver, øvelse og resultatverdi, dato innen ±5 dager og ligger i samme
-- stevne: samme post, samme navn (sted foran fjernet) eller samme sted. E beholdes (riktig
-- dato), N slettes. Én-til-én per importdag: hver eldre rad forklarer høyst én ny rad fra samme
-- kjøring, så forsøk og finale med lik tid blir stående, og par med hver sin kjente runde
-- røres ikke. Vind, runde og plass kopieres til E der de mangler. Slettede rader lagres i opprydding_importdubletter og kan legges tilbake.

-- «performance_value + 0» og datointervallet får planleggeren til å bruke indeksen på
-- (utøver, øvelse, resultat): med indeksen på (øvelse, resultat) hentet hver rad alle med samme
-- resultat i øvelsen (over 110 s per kvarter). idx_results_created_at velger vinduet.
create index if not exists idx_results_created_at on results (created_at);

create table if not exists opprydding_importdubletter (like results);
alter table opprydding_importdubletter add column if not exists beholdt_id uuid;
alter table opprydding_importdubletter add column if not exists importdag date;
alter table opprydding_importdubletter add column if not exists slettet_tid timestamptz default now();
create index if not exists opprydding_importdubletter_beholdt on opprydding_importdubletter (beholdt_id, importdag);
create index if not exists opprydding_importdubletter_meet on opprydding_importdubletter (meet_id);
alter table opprydding_importdubletter enable row level security;

create or replace function rydd_importdubletter(p_fra timestamptz, p_til timestamptz, p_dry boolean)
returns jsonb
language plpgsql
security definer
set statement_timeout = '110s'
set search_path = public
as $$
declare
  v_kandidater int; v_valgt int; v_oppdatert int := 0; v_feil int := 0; v_slettet int := 0;
  r record;
begin
  create temp table _par on commit drop as
  with n as (
    select x.id, x.athlete_id, x.event_id, x.performance_value, x.date, x.meet_id, x.created_at, x.round, x.place,
           x.created_at::date as importdag, m.name, m.city
    from results x join meets m on m.id = x.meet_id
    where x.created_at >= p_fra and x.created_at < p_til and x.status = 'OK' and x.performance_value is not null)
  select n.id as nid, n.importdag, n.created_at as ncreated, o.id as oid, o.created_at as ocreated,
         (o.meet_id = n.meet_id) as samme_post, abs(o.date - n.date) as dd,
         (o.place is not distinct from n.place) as samme_plass
  from n
  join results o on o.athlete_id = n.athlete_id and o.event_id = n.event_id
               and o.performance_value + 0 = n.performance_value and o.status = 'OK' and o.id <> n.id
               and o.created_at < n.created_at and o.created_at::date <> n.importdag
               and o.date between n.date - 5 and n.date + 5
               and (o.round is null or n.round is null or o.round = n.round)
  join meets mo on mo.id = o.meet_id
  where (o.meet_id = n.meet_id
         or lower(regexp_replace(mo.name, '^[^,]*,\s*', '')) = lower(regexp_replace(n.name, '^[^,]*,\s*', ''))
         or mo.city = n.city)
    and not exists (select 1 from opprydding_importdubletter b where b.beholdt_id = o.id and b.importdag = n.importdag);

  select count(distinct nid) into v_kandidater from _par;

  -- beste eldre rad per ny rad (samme plass, samme post, nærmeste dato, eldst), deretter én ny rad per
  -- eldre rad og importdag - helst den med samme plass: har importen både forsøket og finalen med lik
  -- tid og basen bare det ene, er det raden med samme plass som er kopien (03.10.2026: 34 par byttet)
  create temp table _valgt on commit drop as
  select distinct on (oid, importdag) nid, oid, importdag
  from (select distinct on (nid) nid, oid, importdag, ncreated, samme_plass
        from _par order by nid, samme_plass desc, samme_post desc, dd, ocreated) best
  order by oid, importdag, samme_plass desc, ncreated, nid;
  select count(*) into v_valgt from _valgt;

  if not p_dry then
    -- vind, runde og plass fra den nye raden der den beholdte mangler; hentes foer slettingen og
    -- skrives etterpaa (i samme post ville den beholdte raden ellers kollidere med den nye i
    -- results_innhold_unik)
    create temp table _kopi on commit drop as
    select v.oid, n.wind, n.round, n.heat_number, n.place
    from _valgt v join results n on n.id = v.nid join results o on o.id = v.oid
    where (n.wind is not null and o.wind is null) or (n.round is not null and o.round is null)
       or (n.place is not null and o.place is null);

    insert into opprydding_importdubletter
    select x.*, v.oid, v.importdag, now() from results x join _valgt v on v.nid = x.id;

    delete from results x using _valgt v where x.id = v.nid;
    get diagnostics v_slettet = row_count;

    for r in select * from _kopi loop
      begin
        update results set wind = coalesce(wind, r.wind), place = coalesce(place, r.place),
                           heat_number = case when round is null and r.round is not null then r.heat_number else heat_number end,
                           round = coalesce(round, r.round)
         where id = r.oid;
        v_oppdatert := v_oppdatert + 1;
      exception when unique_violation then
        v_feil := v_feil + 1;
      end;
    end loop;
  end if;

  return jsonb_build_object('kandidater', v_kandidater, 'valgt', v_valgt, 'slettet', v_slettet,
                            'vind_runde_plass_kopiert', v_oppdatert, 'kopiering_feilet', v_feil);
end;
$$;

-- Stevneposter som ble tomme av oppryddingen. Har posten kildens stevne-id, legges et alias til
-- søskenposten (samme navn, nærmeste startdato), slik at importen ikke oppretter den på nytt.
create or replace function rydd_tomme_importstevner(p_dry boolean)
returns jsonb
language plpgsql
security definer
set statement_timeout = '110s'
set search_path = public
as $$
declare
  v_tomme int := 0; v_alias int := 0; v_slettet int := 0; r record; v_sosken uuid;
begin
  for r in
    select m.id, m.name, m.start_date, m.external_id
    from meets m
    where m.id in (select distinct meet_id from opprydding_importdubletter)
      and not exists (select 1 from results x where x.meet_id = m.id)
  loop
    v_tomme := v_tomme + 1;
    if r.external_id is not null then
      select s.id into v_sosken from meets s
       where s.id <> r.id and lower(s.name) = lower(r.name) and abs(s.start_date - r.start_date) <= 6
         and exists (select 1 from results x where x.meet_id = s.id)
       order by abs(s.start_date - r.start_date), s.start_date limit 1;
      if v_sosken is not null then
        v_alias := v_alias + 1;
        if not p_dry then
          insert into stevne_alias (external_id, meet_id) values (r.external_id, v_sosken)
          on conflict (external_id) do nothing;
        end if;
      end if;
    end if;
    if not p_dry then
      delete from meets where id = r.id;
      v_slettet := v_slettet + 1;
    end if;
  end loop;
  return jsonb_build_object('tomme', v_tomme, 'alias', v_alias, 'slettet', v_slettet);
end;
$$;

-- Kontroll for test_fullstendighet.py: rader lagt inn etter p_fra som har en eldre tvilling
-- fra en annen importdag i samme stevne (samme regel som over). Skal være 0.
create or replace function test_importdubletter(p_fra timestamptz)
returns bigint
language sql
stable
security definer
set statement_timeout = '110s'
set search_path = public
as $$
  select count(distinct n.id)
  from results n
  join meets mn on mn.id = n.meet_id
  join results o on o.athlete_id = n.athlete_id and o.event_id = n.event_id
               and o.performance_value + 0 = n.performance_value and o.status = 'OK' and o.id <> n.id
               and o.created_at < n.created_at and o.created_at::date <> n.created_at::date
               and o.date between n.date - 5 and n.date + 5
               and (o.round is null or n.round is null or o.round = n.round)
  join meets mo on mo.id = o.meet_id
  where n.created_at >= p_fra and n.status = 'OK' and n.performance_value is not null
    and (o.meet_id = n.meet_id
         or lower(regexp_replace(mo.name, '^[^,]*,\s*', '')) = lower(regexp_replace(mn.name, '^[^,]*,\s*', ''))
         or mo.city = mn.city);
$$;

revoke all on function rydd_importdubletter(timestamptz, timestamptz, boolean) from public, anon, authenticated;
revoke all on function rydd_tomme_importstevner(boolean) from public, anon, authenticated;
revoke all on function test_importdubletter(timestamptz) from public, anon, authenticated;
grant execute on function rydd_importdubletter(timestamptz, timestamptz, boolean) to service_role;
grant execute on function rydd_tomme_importstevner(boolean) to service_role;
grant execute on function test_importdubletter(timestamptz) to service_role;


-- ------------------------------------------------------------------------------------------------
-- Kjørt 03.10.2026 i tillegg (engangs, via SQL; tallene i OPERATIONS_LOG):
--
-- 1. Bytte (34 par): første kjøring paret i noen tilfeller den nye raden med ANNEN plass med den
--    eldre raden (forsøk/finale med lik tid der basen bare hadde det ene), og lot kopien med samme
--    plass stå. De 34 radene ble lagt tilbake fra reserven, og kopiene med samme plass slettet
--    (med reserve). Funksjonen over foretrekker nå samme plass.
-- 2. Samme stevne under ulike navn (1 275 rader): samme utøver, øvelse, resultat, DATO og PLASS,
--    eldre rad i en post med annet navn i samme by (byen i det ene navnet = stedet i det andre,
--    eller det ene stedet begynner med det andre: «UKI-karusell 2013»/Jessheim og «Jessheim,
--    UKI-karusell 2013 Eliteheat»; «Vestfoldkarusellen»/Larvik og «Larvik, Åpningsstevne»).
--    Den eldre raden beholdt, én-til-én per importdag, reserve i opprydding_importdubletter.
