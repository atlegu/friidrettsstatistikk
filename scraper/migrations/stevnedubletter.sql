-- Opprydding av stevneposter som er samme stevne. Anvendt mot produksjon
-- 18.09.2026 (funksjonene; selve oppryddingen kjøres av
-- scraper/rydd_stevnedubletter.py). Se OPERATIONS_LOG 2026-09-18.
--
-- Grunnlaget, tabellen opprydding_stevnepar, ble bygget slik:
--   par av stevner med minst ett felles resultat (samme utøver, øvelse,
--   dato og resultatverdi), pluss par samme dag der det ene navnet er det
--   andre med sted foran. Kolonnene behold/fjern/vedtak/utfort/resultat
--   fylles av skriptet.

create or replace function rydd_stevnepar(p_behold uuid, p_fjern uuid, p_flytt boolean, p_dry boolean)
returns jsonb
language plpgsql
security definer
set statement_timeout = '110s'
set search_path = public
as $$
declare
  v_vind int := 0; v_vind_feil int := 0; v_slettet int := 0; v_flyttet int := 0;
  v_ikke_flyttet int := 0; v_igjen int := 0; v_stevne_slettet boolean := false;
  r record;
begin
  if p_behold = p_fjern then raise exception 'samme stevne'; end if;

  -- 1) vind til raden som beholdes, der den mangler
  for r in
    select b.id as bid, f.wind as fw
    from results f
    join results b on b.meet_id = p_behold and b.athlete_id = f.athlete_id and b.event_id = f.event_id
                  and b.date = f.date and b.performance_value = f.performance_value
    where f.meet_id = p_fjern and f.wind is not null and b.wind is null
  loop
    if p_dry then
      v_vind := v_vind + 1;
    else
      begin
        update results set wind = r.fw where id = r.bid;
        v_vind := v_vind + 1;
      exception when unique_violation then
        v_vind_feil := v_vind_feil + 1;
      end;
    end if;
  end loop;

  -- 2) tvillingene i p_fjern
  select count(*) into v_slettet from results f
   where f.meet_id = p_fjern
     and exists (select 1 from results b where b.meet_id = p_behold and b.athlete_id = f.athlete_id
                   and b.event_id = f.event_id and b.date = f.date and b.performance_value = f.performance_value);
  if not p_dry then
    delete from results f
     where f.meet_id = p_fjern
       and exists (select 1 from results b where b.meet_id = p_behold and b.athlete_id = f.athlete_id
                     and b.event_id = f.event_id and b.date = f.date and b.performance_value = f.performance_value);
  end if;

  -- 3) resten flyttes
  if p_flytt then
    for r in select id from results where meet_id = p_fjern loop
      if p_dry then
        v_flyttet := v_flyttet + 1;
      else
        begin
          update results set meet_id = p_behold where id = r.id;
          v_flyttet := v_flyttet + 1;
        exception when unique_violation then
          v_ikke_flyttet := v_ikke_flyttet + 1;
        end;
      end if;
    end loop;
  end if;

  select count(*) into v_igjen from results where meet_id = p_fjern;
  if p_dry then
    v_igjen := v_igjen - v_slettet - v_flyttet;
  end if;

  if not p_dry then
    update meets b set city = f.city
      from meets f
     where b.id = p_behold and f.id = p_fjern and coalesce(b.city, '') = '' and coalesce(f.city, '') <> '';
    if p_flytt and v_igjen = 0 then
      delete from meets where id = p_fjern;
      v_stevne_slettet := true;
    end if;
  end if;

  return jsonb_build_object(
    'vind_kopiert', v_vind, 'vind_feil', v_vind_feil, 'slettet', v_slettet,
    'flyttet', v_flyttet, 'ikke_flyttet', v_ikke_flyttet, 'igjen', v_igjen,
    'stevne_slettet', v_stevne_slettet);
end;
$$;

revoke all on function rydd_stevnepar(uuid, uuid, boolean, boolean) from public, anon, authenticated;
grant execute on function rydd_stevnepar(uuid, uuid, boolean, boolean) to service_role;

-- Kontroll for test_fullstendighet.py: samme resultat i to stevner, siste år.
create or replace function test_stevnedubletter(p_fra date)
returns table (par bigint, rader bigint)
language sql
stable
security definer
set statement_timeout = '110s'
set search_path = public
as $$
  select count(distinct (r1.meet_id::text || r2.meet_id::text)), count(*)
  from results r1 join results r2
    on r2.athlete_id = r1.athlete_id and r2.event_id = r1.event_id and r2.date = r1.date
   and r2.performance_value = r1.performance_value and r2.meet_id > r1.meet_id
  where r1.date >= p_fra and r2.date >= p_fra;
$$;
grant execute on function test_stevnedubletter(date) to service_role;
