-- Radnivåsikkerhet på user_profiles uten evig løkke. 16.10.2026.
--
-- Policyene slo opp i user_profiles for å avgjøre om man fikk lese
-- user_profiles, og Postgres meldte «infinite recursion detected in policy».
-- Oppslaget går nå gjennom security definer-funksjoner, som leser tabellen
-- uten å utløse policyene på nytt.

create or replace function public.is_super_admin()
returns boolean language sql stable security definer set search_path = public
as $$
  select exists (
    select 1 from public.user_profiles
    where user_id = auth.uid() and role = 'super_admin'
  );
$$;
revoke all on function public.is_super_admin() from public, anon;
grant execute on function public.is_super_admin() to authenticated;

drop policy if exists "Users can read own or admin can read all" on public.user_profiles;
create policy "Users can read own or admin can read all" on public.user_profiles
  for select using (user_id = (select auth.uid()) or (select public.is_admin()));

drop policy if exists "Super admins can update profiles" on public.user_profiles;
create policy "Super admins can update profiles" on public.user_profiles
  for update using ((select public.is_super_admin()));
