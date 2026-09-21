-- Anvendt mot produksjon 21.09.2026. Kildens stevne-id-er som peker på et
-- stevne vi har slått sammen med et annet; rydd_stevnepar fyller tabellen
-- når en post slettes, og importen (get_or_create_meet) slår opp her etter
-- external_id. Uten dette opprettet importen den slettede posten på nytt
-- neste natt. Funksjonen rydd_stevnepar er oppdatert tilsvarende (se
-- stevnedubletter.sql for resten av den).
create table if not exists stevne_alias (
  external_id text primary key,
  meet_id uuid not null references meets(id) on delete cascade,
  created_at timestamptz default now()
);
grant select on stevne_alias to anon, authenticated, service_role;
grant insert, update, delete on stevne_alias to service_role;
