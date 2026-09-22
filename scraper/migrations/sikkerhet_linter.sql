-- Rettelser etter Supabase sin sikkerhetslinter. Anvendt mot produksjon
-- 22.09.2026.
--
-- 1) Visninger bruker leserens rettigheter (security_invoker). Alle
--    underliggende tabeller er lesbare for anon, så ingen side mister data.
alter view public.klubber_med_statistikk set (security_invoker = on);
alter view public.personal_bests_detailed set (security_invoker = on);

-- 2) Radsikkerhet på hjelpetabellene. vedlikehold og klubb_ordformer leses
--    av nettstedet (anon); stevne_alias og opprydding_stevnepar bare av
--    importen (service_role, som går utenom RLS).
alter table public.vedlikehold enable row level security;
alter table public.klubb_ordformer enable row level security;
alter table public.stevne_alias enable row level security;
alter table public.opprydding_stevnepar enable row level security;
create policy "les vedlikehold" on public.vedlikehold for select to anon, authenticated using (true);
create policy "les klubb_ordformer" on public.klubb_ordformer for select to anon, authenticated using (true);

-- 3) Lesefunksjonene nettstedet kaller: SECURITY INVOKER, dataene er offentlige.
alter function public.klubb_statistikk(uuid) security invoker;
alter function public.klubbrekorder(uuid, text, text[], boolean) security invoker;
alter function public.norgesrekorder(uuid[], text, text[], boolean, jsonb) security invoker;
alter function public.tell_kvalifiserte(jsonb, text) security invoker;

-- 4) Vedlikeholds- og testfunksjoner bare for service_role. execute_readonly_query
--    kjører vilkårlig SELECT som eier og brukes ikke av nettstedet.
revoke execute on function public.execute_readonly_query(text) from public, anon, authenticated;
revoke execute on function public.test_innholdsdubletter(uuid) from public, anon, authenticated;
revoke execute on function public.test_stevnedubletter(date) from public, anon, authenticated;
revoke execute on function public.test_urimelige_tider() from public, anon, authenticated;
revoke execute on function public.test_utoveravdrift(uuid) from public, anon, authenticated;
revoke execute on function public.rett_vindflagg(uuid) from public, anon, authenticated;
revoke execute on function public.refresh_klubb_bruk_hvis_utdatert() from public, anon, authenticated;
revoke execute on function public.refresh_plattform_statistikk() from public, anon, authenticated;
revoke execute on function public.handle_new_user() from public, anon, authenticated;

-- 5) Fast search_path på funksjoner som manglet det.
alter function public.er_vindpaavirket(text) set search_path = public;
alter function public.er_langt_loep(text) set search_path = public;
alter function public.minste_hundredeler(text) set search_path = public;
alter function public.sett_vindflagg() set search_path = public;
alter function public.set_meet_external_ids(jsonb) set search_path = public;
alter function public.get_all_time_best(uuid, text, text[], boolean, boolean, boolean, boolean, boolean, integer, integer) set search_path = public;
alter function public.analyse_active_athletes(integer, integer) set search_path = public;
alter function public.analyse_active_by_age(integer, integer) set search_path = public;
alter function public.analyse_debut(integer, integer) set search_path = public;
alter function public.analyse_event_trend(text, integer, integer, boolean, integer, integer, integer, integer, boolean) set search_path = public;
alter function public.analyse_survival(integer, integer, integer, integer) set search_path = public;
