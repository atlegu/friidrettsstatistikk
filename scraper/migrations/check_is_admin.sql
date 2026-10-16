-- Middleware (web/src/middleware.ts) brukte profiles.is_admin, mens
-- administrasjonssidene og radnivåsikkerheten (is_admin()) bruker
-- user_profiles.role. En konto kunne derfor slippe forbi middleware uten å få
-- noe i admin. 16.10.2026: én regel, user_profiles.role.
create or replace function public.check_is_admin(check_user_id uuid)
returns boolean language plpgsql security definer set search_path to 'public'
as $function$
begin
  return exists (
    select 1 from public.user_profiles
    where user_id = check_user_id and role in ('admin', 'super_admin')
  );
end;
$function$;
