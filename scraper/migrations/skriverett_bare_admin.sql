-- Skriverett på statistikktabellene bare for administratorer. 16.10.2026.
--
-- Policyene krevde bare innlogging (auth.uid() IS NOT NULL), så enhver
-- registrert bruker kunne endre og legge inn resultater, utøvere og stevner.
-- Nå kreves is_admin(). Importen bruker service-nøkkelen og påvirkes ikke.

drop policy if exists "Autentiserte kan oppdatere resultater" on public.results;
drop policy if exists "Autentiserte kan opprette resultater" on public.results;
create policy "Admin oppdaterer resultater" on public.results for update using ((select public.is_admin()));
create policy "Admin oppretter resultater" on public.results for insert with check ((select public.is_admin()));

drop policy if exists "Autentiserte kan oppdatere utøvere" on public.athletes;
drop policy if exists "Autentiserte kan opprette utøvere" on public.athletes;
create policy "Admin oppdaterer utøvere" on public.athletes for update using ((select public.is_admin()));
create policy "Admin oppretter utøvere" on public.athletes for insert with check ((select public.is_admin()));

drop policy if exists "Autentiserte kan oppdatere stevner" on public.meets;
drop policy if exists "Autentiserte kan opprette stevner" on public.meets;
create policy "Admin oppdaterer stevner" on public.meets for update using ((select public.is_admin()));
create policy "Admin oppretter stevner" on public.meets for insert with check ((select public.is_admin()));

drop policy if exists "Autentiserte kan opprette klubber" on public.clubs;
create policy "Admin oppretter klubber" on public.clubs for insert with check ((select public.is_admin()));

drop policy if exists "Autentiserte kan opprette kilder" on public.sources;
create policy "Admin oppretter kilder" on public.sources for insert with check ((select public.is_admin()));
