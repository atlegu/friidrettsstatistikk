-- Anvendt mot produksjon 23.09.2026.
--
-- 1) parse_performance godtok ikke «M:SS» uten hundredeler (2:25, 24:29).
--    Radene rett_minuttider rettet 18.–21.09 fikk derfor performance_value
--    NULL og falt ut av alle lister: 7 280 rader. Nå tolkes M:SS, og radene
--    er regnet ut på nytt. (Heltall i felt og høyde tolkes fortsatt ikke:
--    de er mangekamppoeng under øvelser typet som distance, og høyde i cm.)
-- 2) Landevei (3/5/10/100 km) manglet gulv i minste_hundredeler, så «43.34»
--    på 10 km ble 43 sekunder. Gulv 150 s per km. Todelt tid på distanser med
--    gulv over 50 min er timer:minutter («1:26» på 20 km kappgang).
-- 3) Rester som ikke lar seg tolke trygt er satt til status NM.

create or replace function public.parse_performance(perf text, res_type result_type)
returns integer language plpgsql immutable set search_path to 'public'
as $function$
declare
    parts text[];
    total integer;
begin
    if perf is null or perf = '' or perf = 'x' or perf = '-' then
        return null;
    end if;
    case res_type
        when 'time' then
            if perf ~ '^\d+:\d+:\d+' then
                parts := regexp_split_to_array(perf, ':');
                total := (parts[1]::integer * 3600 + parts[2]::integer * 60 + parts[3]::numeric) * 100;
            elsif perf ~ '^\d+:\d+\.\d+' then
                parts := regexp_split_to_array(perf, '[:.]');
                total := (parts[1]::integer * 60 * 100) + (parts[2]::integer * 100) +
                         (case when length(parts[3]) = 1 then parts[3]::integer * 10 else parts[3]::integer end);
            elsif perf ~ '^\d+:\d+$' then
                parts := regexp_split_to_array(perf, ':');
                total := (parts[1]::integer * 60 + parts[2]::integer) * 100;
            elsif perf ~ '^\d+\.\d+' then
                total := (perf::numeric * 100)::integer;
            else
                return null;
            end if;
            return total;
        when 'distance' then
            if perf ~ '^\d+\.\d+' then return (perf::numeric * 1000)::integer; else return null; end if;
        when 'height' then
            if perf ~ '^\d+\.\d+' then return (perf::numeric * 1000)::integer; else return null; end if;
        when 'points' then
            if perf ~ '^\d+' then return perf::integer; else return null; end if;
    end case;
    return null;
end;
$function$;

create or replace function minste_hundredeler(p_code text)
returns integer language sql immutable set search_path = public as $$
  select case
    when p_code ilike '%halvmaraton%' then 330000
    when p_code ilike '%maraton%' then 700000
    when p_code ~ '^\d+km$' then (regexp_match(p_code, '^(\d+)km$'))[1]::int * 15000
    when p_code ~ '^kappgang_\d+_km' then (regexp_match(p_code, '^kappgang_(\d+)_km'))[1]::int * 15000
    when p_code ~ '^(kappgang_)?\d+_?m' then (regexp_match(p_code, '^(?:kappgang_)?(\d+)_?m'))[1]::int * 10
    else 0 end;
$$;

-- Engangsretting (kjørt):
-- update results r set performance = r.performance from events e
--  where e.id = r.event_id and e.result_type = 'time' and r.performance_value is null
--    and r.performance ~ '^\d+:\d{2}$';
-- update results r set performance = r.performance || ':00' from events e
--  where e.id = r.event_id and e.result_type = 'time' and r.status = 'OK'
--    and r.performance ~ '^\d{1,2}:\d{2}$' and r.performance_value < minste_hundredeler(e.code)
--    and r.performance_value * 60 between minste_hundredeler(e.code) and minste_hundredeler(e.code) * 4;
-- update results r set status = 'NM' from events e
--  where e.id = r.event_id and e.result_type = 'time' and r.status = 'OK' and r.performance_value > 0
--    and r.performance_value < greatest(minste_hundredeler(e.code), case when er_langt_loep(e.code) then 6000 else 0 end);
