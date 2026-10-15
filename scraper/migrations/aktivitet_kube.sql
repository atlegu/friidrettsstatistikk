-- Aktivitetssiden: ferdig utregnede tall. 15.10.2026.
--
-- aktivitet_per_aar() og aktivitet_alder() talte unike utøvere direkte i
-- aktivitet_grunnlag (1,2 mill. rader). Med kald hurtigbuffer tok det 6,8 s,
-- over grensen på 3 s for anonyme kall, og siden viste «Ingen aktivitet i
-- utvalget». aktivitet_kube har tallene for alle kombinasjoner av kjønn,
-- alder og øvelsesgruppe per år (CUBE), og funksjonene leser derfra (1,5 ms).
-- Kontrollert mot de gamle funksjonene: 56 av 56 rader like.
--
-- Bygges om sammen med aktivitet_grunnlag i refresh_klubb_bruk_hvis_utdatert().

set statement_timeout = '600s';
set work_mem = '128MB';
create materialized view if not exists public.aktivitet_kube as
select aar, kjonn, alder, kategori,
       grouping(kjonn) as gk, grouping(alder) as ga, grouping(kategori) as gc,
       concat_ws('|', aar, grouping(kjonn), grouping(alder), grouping(kategori),
                 coalesce(kjonn, '~'), coalesce(alder, '~'), coalesce(kategori, '~')) as nokkel,
       count(distinct meet_id) as stevner,
       sum(starter) as starter,
       count(distinct athlete_id) as unike,
       count(distinct athlete_id) filter (where alder = '13-19') as unike_ungdom,
       count(distinct athlete_id) filter (where kjonn = 'M') as menn,
       count(distinct athlete_id) filter (where kjonn = 'F') as kvinner
from public.aktivitet_grunnlag
group by aar, cube (kjonn, alder, kategori);
create unique index if not exists aktivitet_kube_nokkel on public.aktivitet_kube (nokkel);
create index if not exists aktivitet_kube_oppslag on public.aktivitet_kube (gk, ga, gc, aar);
grant select on public.aktivitet_kube to anon, authenticated;

create or replace function public.aktivitet_per_aar(p_fra integer, p_til integer, p_kjonn text default null, p_alder text default null, p_kategori text default null)
returns table(aar integer, stevner bigint, starter bigint, unike bigint, unike_ungdom bigint, menn bigint, kvinner bigint)
language sql stable set search_path to 'public'
as $$
  select q.aar, q.stevner, q.starter, q.unike, q.unike_ungdom, q.menn, q.kvinner
  from aktivitet_kube q
  where q.aar between p_fra and p_til
    and q.gk = (p_kjonn is null)::int and q.ga = (p_alder is null)::int and q.gc = (p_kategori is null)::int
    and (p_kjonn is null or q.kjonn = p_kjonn)
    and (p_alder is null or q.alder = p_alder)
    and (p_kategori is null or q.kategori = p_kategori)
  order by q.aar;
$$;

create or replace function public.aktivitet_alder(p_aar integer, p_kjonn text default null, p_kategori text default null)
returns table(alder text, unike bigint)
language sql stable set search_path to 'public'
as $$
  select q.alder, q.unike
  from aktivitet_kube q
  where q.aar = p_aar and q.ga = 0
    and q.gk = (p_kjonn is null)::int and q.gc = (p_kategori is null)::int
    and (p_kjonn is null or q.kjonn = p_kjonn)
    and (p_kategori is null or q.kategori = p_kategori);
$$;

create or replace function public.refresh_klubb_bruk_hvis_utdatert()
returns text language plpgsql security definer set search_path to 'public' set statement_timeout to '900s'
as $$
declare siden timestamptz;
begin
  select utdatert_siden into siden from vedlikehold where nokkel = 'klubb_bruk';
  if siden is null then return 'ikke utdatert'; end if;
  refresh materialized view concurrently klubb_bruk;
  refresh materialized view concurrently aktivitet_grunnlag;
  refresh materialized view concurrently aktivitet_klubb;
  refresh materialized view concurrently aktivitet_kube;
  update vedlikehold set utdatert_siden = null, sist_oppdatert = now()
   where nokkel = 'klubb_bruk';
  return 'oppdatert';
end;
$$;
