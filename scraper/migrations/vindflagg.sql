-- is_wind_legal: én regel, anvendt av en trigger for alle importveier.
-- Anvendt mot produksjon 15.09.2026. Se OPERATIONS_LOG.md for reparasjonen.
--
-- Bakgrunn: kolonnen hadde standardverdi true, og importene satte bare false
-- ved vind over 2,0. Alt annet sto som «lovlig», ogsaa 34 166 utendoers-
-- resultater uten vindmaaling. 2 842 loep i medvind over 2,0 sto som lovlig,
-- og 44 169 med maalt, lovlig vind sto som NULL og falt ut av aarslistene.
--
-- Regel:  vindpaavirket oevelse: wind <= 2,0 -> true, > 2,0 -> false, umaalt -> NULL
--         andre oevelser:        NULL
-- Vindpaavirket = sprint t.o.m. 200 m, hekk t.o.m. 200 m, lengde og tresteg
-- med tilloep (WA 17.9). Ikke mangekamp, ikke hopp uten tilloep.
-- Samme regel ligger i web/src/lib/vind.ts. Endres den ene, endres den andre.

create or replace function er_vindpaavirket(p_code text)
returns boolean language sql immutable as $$
  select p_code is not null and (
    p_code in ('60m','80m','100m','150m','200m')
    or ((p_code like 'lengde%' or p_code like 'tresteg%') and p_code not like '%\_ut')
    or p_code ~ '^(30|40|55|60|80|100|110|200)(mh|_m_h)'
  );
$$;

create or replace function vindflagg(p_event_id uuid, p_wind numeric)
returns boolean language sql stable set search_path = public as $$
  select case
    when not er_vindpaavirket((select code from events where id = p_event_id)) then null
    when p_wind is null then null
    when p_wind <= 2.0 then true
    else false
  end;
$$;

create or replace function sett_vindflagg()
returns trigger language plpgsql as $$
begin
  new.is_wind_legal := vindflagg(new.event_id, new.wind);
  return new;
end;
$$;

drop trigger if exists trg_sett_vindflagg on results;
create trigger trg_sett_vindflagg
  before insert or update of wind, event_id on results
  for each row execute function sett_vindflagg();

alter table results alter column is_wind_legal drop default;

-- Reparasjon, én oevelse om gangen (indeks paa event_id, innenfor tidsgrensen).
create or replace function rett_vindflagg(p_event_id uuid)
returns integer language plpgsql security definer
set search_path = public set statement_timeout = '300s' as $$
declare
  n integer;
  paavirket boolean := er_vindpaavirket((select code from events where id = p_event_id));
begin
  if paavirket then
    update results
       set is_wind_legal = case when wind is null then null when wind <= 2.0 then true else false end
     where event_id = p_event_id
       and is_wind_legal is distinct from
           (case when wind is null then null when wind <= 2.0 then true else false end);
  else
    update results set is_wind_legal = null
     where event_id = p_event_id and is_wind_legal is not null;
  end if;
  get diagnostics n = row_count;
  return n;
end;
$$;

grant execute on function rett_vindflagg(uuid) to service_role;
grant execute on function er_vindpaavirket(text) to anon, authenticated, service_role;
