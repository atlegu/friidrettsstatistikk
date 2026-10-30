-- Samme resultat under to øvelseskoder («kryss-kode-dubletter»). Se OPERATIONS_LOG 2026-10-30.
-- Selve oppryddingen kjøres av scraper/rydd_kryssdubletter.py.
--
-- Funn (dataauditen av A1/A3/A6 30.10.2026, kartlagt i basen samme dag): brettrader i lengde og
-- tresteg som er kopier av et sonehopp i lengde_sone_05m/tresteg_sone_05m (samme utøver,
-- resultatverdi og vind). Sonerakene kom inn i januar 2026 fra kildens utøversider
-- (complete_scraper.py laget koden av kildenavnet «Lengde (Sone 0,5m)»). Senere importer la det
-- samme hoppet under brettkoden: update_results.py 13.–14.02 og 24.08–06.09.2026 og
-- import_youth_stats.py 19.05.2026 (begge hadde 'Lengde (Sone 0,5m)': 'lengde'), og 117 rader fra
-- alle tiders-importen 14.02.2026. Dublettsjekkene sammenlignet bare innen samme kode, og det gjorde
-- ryddingen 03.10.2026 også. Kilden viser hoppene bare under sonen. Roten er rettet i importene
-- (scraper/kodegrupper.py).
--
-- To regler (p_regel), begge: K er en OK-rad under p_kopi, B en OK-rad under p_beholdt med samme
-- utøver, resultatverdi og vind (ingen vind = ingen vind), lagt inn før K. B beholdes, K slettes.
--   samme_dato      B har samme dato som K. Stevneposten teller ikke med: 8 % ligger i en annen
--                   post enn sonen (ungdomsimporten la dem i poster som «PEAB-lekene»/Osterøy).
--                   Dette er regelen i forskning/rens_felles.py.
--   flerdagsstevne  K har startdatoen til sin post, B ligger 1–6 dager senere i en søskenpost
--                   (samme navn med sted foran fjernet, eller samme sted), og ingen sonerad har
--                   samme dato som K. Augustimporten ga alle resultater i et flerdagsstevne
--                   startdatoen og la dem i posten med kildens stevne-id, mens sonehoppet ligger i
--                   dagsposten med riktig dato (samme mekanisme som i importdubletter.sql).
-- Plass kopieres til B der B mangler den og radene ligger i samme post. Slettede rader lagres i
-- opprydding_kryssdubletter og kan legges tilbake.
--
-- «performance_value + 0» som i importdubletter.sql: holder planleggeren på indeksen på
-- (utøver, øvelse, resultat) i stedet for (øvelse, resultat).

create table if not exists opprydding_kryssdubletter (like results);
alter table opprydding_kryssdubletter add column if not exists beholdt_id uuid;
alter table opprydding_kryssdubletter add column if not exists kodepar text;
alter table opprydding_kryssdubletter add column if not exists regel text;
alter table opprydding_kryssdubletter add column if not exists slettet_tid timestamptz default now();
create index if not exists opprydding_kryssdubletter_beholdt on opprydding_kryssdubletter (beholdt_id);
alter table opprydding_kryssdubletter enable row level security;

create table if not exists opprydding_kryssposter (like meets);
alter table opprydding_kryssposter add column if not exists alias_til uuid;
alter table opprydding_kryssposter add column if not exists slettet_tid timestamptz default now();
alter table opprydding_kryssposter enable row level security;

create or replace function rydd_kryssdubletter(p_kopi text, p_beholdt text, p_fra date, p_til date,
                                               p_regel text, p_dry boolean)
returns jsonb
language plpgsql
security definer
set statement_timeout = '110s'
set search_path = public
as $$
declare
  v_kopi uuid; v_beholdt uuid;
  v_par int; v_samme_post int; v_alder int; v_uten_aar int; v_flere int; v_annen_kilde int;
  v_poster jsonb := '[]';
  v_slettet int := 0; v_plass int := 0; v_feil int := 0;
  r record;
begin
  select id into v_kopi from events where code = p_kopi;
  select id into v_beholdt from events where code = p_beholdt;
  if v_kopi is null or v_beholdt is null then
    raise exception 'ukjent øvelseskode: % eller %', p_kopi, p_beholdt;
  end if;

  -- én beholdt rad per kopi (drop først: flere kall i samme transaksjon)
  drop table if exists _kryss;
  if p_regel = 'samme_dato' then
    -- helst i samme post, ellers den eldste
    create temp table _kryss on commit drop as
    select distinct on (k.id) k.id as kid, b.id as bid, k.meet_id as kmeet, (k.meet_id = b.meet_id) as samme_post,
           k.place as kplace, b.place as bplace, k.athlete_id, k.date,
           (k.source_id is not null or k.import_batch_id is not null) as annen_kilde
    from results k
    join results b on b.event_id = v_beholdt and b.athlete_id = k.athlete_id
                 and b.performance_value + 0 = k.performance_value and b.date = k.date
                 and b.wind is not distinct from k.wind and b.status = 'OK' and b.created_at < k.created_at
    where k.event_id = v_kopi and k.status = 'OK' and k.performance_value is not null
      and k.date between p_fra and p_til
    order by k.id, (k.meet_id = b.meet_id) desc, b.created_at, b.id;
  elsif p_regel = 'flerdagsstevne' then
    -- nærmeste dag etter startdatoen
    create temp table _kryss on commit drop as
    select distinct on (k.id) k.id as kid, b.id as bid, k.meet_id as kmeet, false as samme_post,
           k.place as kplace, b.place as bplace, k.athlete_id, k.date,
           (k.source_id is not null or k.import_batch_id is not null) as annen_kilde
    from results k
    join meets mk on mk.id = k.meet_id and mk.start_date = k.date
    join results b on b.event_id = v_beholdt and b.athlete_id = k.athlete_id
                 and b.performance_value + 0 = k.performance_value and b.date between k.date + 1 and k.date + 6
                 and b.wind is not distinct from k.wind and b.status = 'OK' and b.created_at < k.created_at
    join meets mb on mb.id = b.meet_id
    where k.event_id = v_kopi and k.status = 'OK' and k.performance_value is not null
      and k.date between p_fra and p_til
      and (lower(regexp_replace(mb.name, '^[^,]*,\s*', '')) = lower(regexp_replace(mk.name, '^[^,]*,\s*', ''))
           or mb.city = mk.city)
      and not exists (select 1 from results z
                       where z.event_id = v_beholdt and z.status = 'OK' and z.athlete_id = k.athlete_id
                         and z.performance_value + 0 = k.performance_value and z.date = k.date
                         and z.wind is not distinct from k.wind)
    order by k.id, b.date, b.created_at, b.id;
  else
    raise exception 'ukjent regel: % (samme_dato eller flerdagsstevne)', p_regel;
  end if;

  select count(*), count(*) filter (where samme_post), count(*) filter (where annen_kilde)
    into v_par, v_samme_post, v_annen_kilde from _kryss;
  select count(*) filter (where a.birth_year is not null and extract(year from x.date)::int - a.birth_year between 11 and 13),
         count(*) filter (where a.birth_year is null)
    into v_alder, v_uten_aar
    from _kryss x join athletes a on a.id = x.athlete_id;
  select count(*) into v_flere from (select bid from _kryss group by bid having count(*) > 1) f;

  if p_dry then
    -- per stevnepost: [post, kopier, rader i alt], så skriptet kan finne poster som blir tomme
    -- når alle kodepar og regler er talt sammen
    select coalesce(jsonb_agg(jsonb_build_array(kmeet, n, (select count(*) from results x where x.meet_id = kmeet))), '[]')
      into v_poster
      from (select kmeet, count(*) as n from _kryss group by kmeet) t;
  else
    insert into opprydding_kryssdubletter
    select x.*, k.bid, p_kopi || ' > ' || p_beholdt, p_regel, now() from results x join _kryss k on k.kid = x.id;

    delete from results x using _kryss k where x.id = k.kid;
    get diagnostics v_slettet = row_count;

    -- plassen fra kopien der sonen mangler den: kopien kom fra kildens resultatside for samme
    -- stevne, så plassen gjelder sonehoppet
    for r in select distinct on (bid) bid, kplace from _kryss
              where samme_post and bplace is null and kplace is not null order by bid, kid loop
      begin
        update results set place = r.kplace where id = r.bid and place is null;
        v_plass := v_plass + 1;
      exception when unique_violation then
        v_feil := v_feil + 1;
      end;
    end loop;
  end if;

  return jsonb_build_object('par', v_par, 'samme_post', v_samme_post, 'alder_11_13', v_alder,
                            'uten_fodselsaar', v_uten_aar, 'fra_annen_kilde', v_annen_kilde,
                            'beholdt_med_flere_kopier', v_flere, 'slettet', v_slettet,
                            'plass_kopiert', v_plass, 'plass_feilet', v_feil, 'poster', v_poster);
end;
$$;

-- Stevneposter som ble tomme av oppryddingen (poster i reserven uten resultater igjen; 78 etter
-- tørrkjøringen 30.10.2026, mest små poster fra ungdomsimporten 19.05 og alle tiders-importen
-- 14.02). De lagres i opprydding_kryssposter og slettes. Har posten kildens stevne-id, får posten
-- der de beholdte radene ligger et alias i stevne_alias, så importen ikke oppretter posten på nytt
-- og legger hoppene inn der.
create or replace function rydd_tomme_kryssposter(p_dry boolean)
returns jsonb
language plpgsql
security definer
set statement_timeout = '110s'
set search_path = public
as $$
declare
  v_tomme int := 0; v_alias int := 0; v_slettet int := 0; r record; v_post uuid;
begin
  for r in
    select m.id, m.external_id from meets m
    where m.id in (select distinct meet_id from opprydding_kryssdubletter)
      and not exists (select 1 from results x where x.meet_id = m.id)
  loop
    v_tomme := v_tomme + 1;
    v_post := null;
    select b.meet_id into v_post
      from opprydding_kryssdubletter k join results b on b.id = k.beholdt_id
     where k.meet_id = r.id
     group by b.meet_id order by count(*) desc, b.meet_id limit 1;
    if r.external_id is not null and v_post is not null then
      v_alias := v_alias + 1;
      if not p_dry then
        insert into stevne_alias (external_id, meet_id) values (r.external_id, v_post)
        on conflict (external_id) do nothing;
      end if;
    end if;
    if not p_dry then
      insert into opprydding_kryssposter select m.*, v_post, now() from meets m where m.id = r.id;
      delete from meets where id = r.id;
      v_slettet := v_slettet + 1;
    end if;
  end loop;
  return jsonb_build_object('tomme', v_tomme, 'alias', v_alias, 'slettet', v_slettet);
end;
$$;

-- Kartlegging for tørrkjøringsrapporten: alle kodepar med samme resultattype der to OK-rader har
-- samme utøver, dato, resultatverdi og vind. kode_a < kode_b; a_nyest = paret der raden under
-- kode_a ble lagt inn sist. Treffer også tilfeldig like resultater (60 m 11,00 og høyde 1,10 har
-- samme verdi), så par med få rader er ikke nødvendigvis kopier.
create or replace function kartlegg_kryssdubletter(p_fra date, p_til date)
returns table (kode_a text, kode_b text, antall bigint, a_nyest bigint)
language sql
stable
security definer
set statement_timeout = '110s'
set search_path = public
as $$
  select ea.code, eb.code, count(*), count(*) filter (where x.created_at > y.created_at)
  from results x
  join events ea on ea.id = x.event_id
  join results y on y.athlete_id = x.athlete_id and y.date = x.date and y.performance_value = x.performance_value
                and y.wind is not distinct from x.wind and y.status = 'OK' and y.event_id <> x.event_id
  join events eb on eb.id = y.event_id and eb.code > ea.code and eb.result_type = ea.result_type
  where x.status = 'OK' and x.performance_value is not null and x.date between p_fra and p_til
  group by 1, 2;
$$;

-- Kontroll for test_fullstendighet.py (1): brettrader med en sonetvilling i hele basen, etter de to
-- reglene over. Skal være 0 etter oppryddingen. Kodeparene er skrevet inn her med vilje,
-- uavhengig av importkoden.
create or replace function test_kryssdubletter()
returns table (kopi text, beholdt text, regel text, antall bigint)
language sql
stable
security definer
set statement_timeout = '110s'
set search_path = public
as $$
  with par(kopi, beholdt) as (values ('lengde', 'lengde_sone_05m'), ('tresteg', 'tresteg_sone_05m'))
  select p.kopi, p.beholdt, 'samme_dato',
         (select count(*) from results k
           where k.event_id = ek.id and k.status = 'OK'
             and exists (select 1 from results b
                          where b.event_id = eb.id and b.status = 'OK' and b.athlete_id = k.athlete_id
                            and b.performance_value + 0 = k.performance_value and b.date = k.date
                            and b.wind is not distinct from k.wind))
  from par p join events ek on ek.code = p.kopi join events eb on eb.code = p.beholdt
  union all
  select p.kopi, p.beholdt, 'flerdagsstevne',
         (select count(*) from results k join meets mk on mk.id = k.meet_id and mk.start_date = k.date
           where k.event_id = ek.id and k.status = 'OK'
             and exists (select 1 from results b join meets mb on mb.id = b.meet_id
                          where b.event_id = eb.id and b.status = 'OK' and b.athlete_id = k.athlete_id
                            and b.performance_value + 0 = k.performance_value
                            and b.date between k.date + 1 and k.date + 6 and b.wind is not distinct from k.wind
                            and (lower(regexp_replace(mb.name, '^[^,]*,\s*', '')) = lower(regexp_replace(mk.name, '^[^,]*,\s*', ''))
                                 or mb.city = mk.city))
             and not exists (select 1 from results z
                              where z.event_id = eb.id and z.status = 'OK' and z.athlete_id = k.athlete_id
                                and z.performance_value + 0 = k.performance_value and z.date = k.date
                                and z.wind is not distinct from k.wind))
  from par p join events ek on ek.code = p.kopi join events eb on eb.code = p.beholdt;
$$;

-- Kontroll for test_fullstendighet.py (2): rader lagt inn etter p_fra som har en tvilling under en
-- annen kode med samme resultattype (samme utøver, dato, resultatverdi og vind). Fanger en ny
-- importvei eller en ny kodeoversettelse som legger samme resultat inn under feil kode.
create or replace function test_kryssdubletter_nye(p_fra timestamptz)
returns table (ny text, eldre text, antall bigint)
language sql
stable
security definer
set statement_timeout = '110s'
set search_path = public
as $$
  select en.code, eo.code, count(distinct n.id)
  from results n
  join events en on en.id = n.event_id
  join results o on o.athlete_id = n.athlete_id and o.date = n.date and o.performance_value + 0 = n.performance_value
                and o.wind is not distinct from n.wind and o.event_id <> n.event_id and o.status = 'OK'
  join events eo on eo.id = o.event_id and eo.result_type = en.result_type
  where n.created_at >= p_fra and n.status = 'OK' and n.performance_value is not null
  group by 1, 2;
$$;

revoke all on function rydd_kryssdubletter(text, text, date, date, text, boolean) from public, anon, authenticated;
revoke all on function rydd_tomme_kryssposter(boolean) from public, anon, authenticated;
revoke all on function kartlegg_kryssdubletter(date, date) from public, anon, authenticated;
revoke all on function test_kryssdubletter() from public, anon, authenticated;
revoke all on function test_kryssdubletter_nye(timestamptz) from public, anon, authenticated;
grant execute on function rydd_kryssdubletter(text, text, date, date, text, boolean) to service_role;
grant execute on function rydd_tomme_kryssposter(boolean) to service_role;
grant execute on function kartlegg_kryssdubletter(date, date) to service_role;
grant execute on function test_kryssdubletter() to service_role;
grant execute on function test_kryssdubletter_nye(timestamptz) to service_role;
