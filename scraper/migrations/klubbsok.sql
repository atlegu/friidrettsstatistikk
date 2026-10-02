-- Klubbsøk som tåler forkortelser.
--
-- Bakgrunn: klubbnavnene er lagret utskrevet («Ås Idrettslag»,
-- «Sportsklubben Vidar», «Idrettsklubben Grane»), mens folk skriver dem
-- forkortet («Ås IL», «SK Vidar», «IK Grane»). short_name er tom for
-- samtlige 2 430 klubber med resultater, så det finnes ikke noe kortnavn å
-- søke i. Løsningen er å føre begge skrivemåtene tilbake til samme form før
-- de sammenliknes.
--
-- Anvendt mot produksjon 14.09.2026.
--
-- Vil du legge til en forkortelse senere: sett inn en rad i klubb_ordformer
-- og kjør refresh_plattform_statistikk(). Ingen kodeendring trengs.

-- 1 ---------------------------------------------------------------- ordformer

create table if not exists klubb_ordformer (
  form     text primary key,
  kanonisk text not null
);

insert into klubb_ordformer (form, kanonisk) values
  ('il', 'il'), ('idrettslag', 'il'), ('idrettslaget', 'il'),
  ('if', 'if'), ('idrettsforening', 'if'), ('idrettsforeningen', 'if'),
  ('ik', 'ik'), ('idrettsklubb', 'ik'), ('idrettsklubben', 'ik'),
  ('sk', 'sk'), ('sportsklubb', 'sk'), ('sportsklubben', 'sk'),
  ('fik', 'fik'), ('friidrettsklubb', 'fik'), ('friidrettsklubben', 'fik'),
  ('fil', 'fil'), ('friidrettslag', 'fil'), ('friidrettslaget', 'fil'),
  ('ff', 'ff'), ('friidrettsforening', 'ff'), ('friidrettsforeningen', 'ff'),
  ('lk', 'lk'), ('lopeklubb', 'lk'), ('lopeklubben', 'lk'), ('lopsklubb', 'lk'),
  ('skk', 'skk'), ('skiklubb', 'skk'), ('skiklubben', 'skk'),
  ('skl', 'skl'), ('skilag', 'skl'), ('skilaget', 'skl'),
  ('tf', 'tf'), ('turnforening', 'tf'), ('turnforeningen', 'tf'),
  ('ul', 'ul'), ('ungdomslag', 'ul'), ('ungdomslaget', 'ul'),
  ('bil', 'bil'), ('bedriftsidrettslag', 'bil'), ('bedriftsidrettslaget', 'bil'),
  ('ak', 'ak'), ('atletklubb', 'ak'), ('atletklubben', 'ak'),
  ('fk', 'fk'), ('fotballklubb', 'fk'), ('fotballklubben', 'fk'),
  ('friidrett', 'friidrett'), ('friidretten', 'friidrett'),
  ('friidrettsgruppa', 'friidrett'), ('friidrettsgruppe', 'friidrett'),
  ('friidrettsgruppen', 'friidrett'),
  ('og', 'og'), ('omegn', 'omegn')
on conflict (form) do update set kanonisk = excluded.kanonisk;

grant select on klubb_ordformer to anon, authenticated;

-- 2 --------------------------------------------------------------- søkenøkkel

-- Små bokstaver, norske tegn foldet (aa/å → a, æ → a, ø → o), tegnsetting
-- bort, og hvert ord erstattet med fellesformen sin. «Ås Idrettslag» og
-- «Ås IL» gir begge « as il ». Nøkkelen er omgitt av mellomrom slik at et
-- helt ord kan treffes med like '% ord %'.
create or replace function klubb_sokenokkel(p_navn text)
returns text
language sql
stable
set search_path = public
as $$
  with foldet as (
    -- aa før å-foldingen ville gjort «Aas» til «aas»; begge skal bli «as».
    select replace(translate(lower(coalesce(p_navn, '')), 'åæø', 'aao'), 'aa', 'a') as s
  ),
  renset as (
    select regexp_replace(s, '[^a-z0-9]+', ' ', 'g') as s from foldet
  ),
  ord as (
    select u.t, u.nr
    from renset,
         unnest(regexp_split_to_array(trim(renset.s), '\s+')) with ordinality as u(t, nr)
    where u.t <> ''
  )
  select coalesce(
    ' ' || string_agg(coalesce(f.kanonisk, o.t), ' ' order by o.nr) || ' ',
    ' '
  )
  from ord o
  left join klubb_ordformer f on f.form = o.t;
$$;

-- 3 ----------------------------------------------------------- klubb_bruk

-- Nøkkelen beregnes én gang per import, ikke per søk.
drop materialized view if exists klubb_bruk;

create materialized view klubb_bruk as
select
  c.id,
  c.name,
  c.short_name,
  c.city,
  c.club_type,
  klubb_sokenokkel(c.name) as sokenokkel,
  count(r.id) as resultater,
  count(distinct r.athlete_id) as utovere,
  min(extract(year from r.date))::integer as fra_ar,
  max(extract(year from r.date))::integer as til_ar
from clubs c
left join results r on r.club_id = c.id
group by c.id, c.name, c.short_name, c.city, c.club_type;

-- Unik indeks kreves for «refresh ... concurrently».
create unique index klubb_bruk_id_idx on klubb_bruk (id);
create index klubb_bruk_navn_idx on klubb_bruk (name);
create index klubb_bruk_resultater_idx on klubb_bruk (resultater desc);

grant select on klubb_bruk to anon, authenticated;

-- 4 ------------------------------------------------------------- søkefunksjon

-- Alle søkeordene må finnes, men rekkefølgen spiller ingen rolle:
-- «Idrettslaget Skjalg» heter «Skjalg IL» til daglig, og begge skal treffe.
-- Treff på helt ord teller mer enn treff på ordstart, slik at «Ås IL» setter
-- Ås Idrettslag foran Askim IL. Deretter størrelse.
--
-- Tomt søk gir hele lista sortert etter størrelse, så listesiden og søket
-- bruker samme kodevei.
create or replace function sok_klubber(
  p_sok    text default null,
  p_type   text default null,
  p_antall integer default 120
)
returns table (
  id         uuid,
  name       text,
  short_name text,
  city       text,
  club_type  club_type,
  resultater bigint,
  utovere    bigint,
  totalt     bigint
)
language sql
stable
set search_path = public
as $$
  with q as (
    select
      array(
        select t
        from unnest(regexp_split_to_array(trim(klubb_sokenokkel(p_sok)), '\s+')) as t
        where t <> ''
      ) as ord,
      trim(klubb_sokenokkel(p_sok)) as hele
  ),
  treff as (
    select
      k.id, k.name, k.short_name, k.city, k.club_type,
      k.resultater, k.utovere, k.sokenokkel,
      (select count(*) from unnest(q.ord) t where k.sokenokkel like '% ' || t || ' %') as helord,
      (select count(*) from unnest(q.ord) t where k.sokenokkel like '% ' || t || '%')  as ordstart,
      q.hele
    from klubb_bruk k
    cross join q
    where k.resultater > 0
      and (p_type is null or k.club_type = p_type::club_type)
      and not exists (
        select 1 from unnest(q.ord) t
        where k.sokenokkel not like '% ' || t || '%'
      )
  )
  select
    t.id, t.name, t.short_name, t.city, t.club_type,
    t.resultater, t.utovere,
    count(*) over () as totalt
  from treff t
  order by
    (t.helord * 3 + t.ordstart) desc,
    (t.sokenokkel like ' ' || t.hele || '%') desc,
    t.resultater desc,
    t.name asc
  limit greatest(p_antall, 1);
$$;

grant execute on function sok_klubber(text, text, integer) to anon, authenticated;

-- 5 -------------------------------------------------------------- oppdatering

-- Importen kaller denne. Klubbtallene og søkenøklene er like ferske som
-- forsidetallene og hører til samme oppdatering.
create or replace function refresh_plattform_statistikk()
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  refresh materialized view concurrently plattform_statistikk;
  refresh materialized view concurrently klubb_bruk;
end;
$$;

-- 15.09.2026: funksjonen fikk egen statement_timeout. Med klubb_bruk i
-- samme kall tok den rundt to minutter, og gjennom PostgREST gjaldt rollens
-- grense - importen fikk 57014 hver gang.
create or replace function refresh_plattform_statistikk()
returns void
language plpgsql
security definer
set search_path = public
set statement_timeout = '900s'
as $$
begin
  refresh materialized view concurrently plattform_statistikk;
  refresh materialized view concurrently klubb_bruk;
end;
$$;
