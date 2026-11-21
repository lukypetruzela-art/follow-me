-- =====================================================================
-- FOLLOW-ME — databáze kalendáře akcí (Supabase)
--
-- Spusťte celý skript jednou v Supabase: SQL Editor → New query → vložit → Run.
-- Skript se dá spustit i opakovaně, nic nezdvojí ani nesmaže.
--
-- Co vytvoří:
--   events  – akce v kalendáři; číst je smí kdokoli (web), měnit jen správci
--   admins  – e-maily správců, kteří smí kalendář upravovat
-- =====================================================================

-- ---------- tabulka akcí ----------
create table if not exists public.events (
  id         uuid primary key default gen_random_uuid(),
  date       date not null,
  date_to    date,
  name       text not null check (char_length(name) between 1 and 120),
  location   text check (char_length(location) <= 120),
  icao       text check (icao ~ '^[A-Z]{4}$'),
  status     text not null default 'confirmed' check (status in ('confirmed', 'tbc', 'cancelled')),
  link       text check (link ~ '^https://' and char_length(link) <= 300),
  note       text check (char_length(note) <= 200),
  lat        double precision check (lat between 35 and 65),
  lng        double precision check (lng between -15 and 40),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint date_to_after_date check (date_to is null or date_to >= date),
  constraint coords_together check ((lat is null) = (lng is null))
);

create index if not exists events_date_idx on public.events (date);

-- automaticky aktualizovat čas poslední úpravy
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists events_touch on public.events;
create trigger events_touch before update on public.events
  for each row execute function public.touch_updated_at();

-- ---------- správci ----------
create table if not exists public.admins (
  email text primary key check (email = lower(email))
);

-- Je přihlášený uživatel správce? (security definer: smí nahlédnout do tabulky admins,
-- kterou jinak nikdo zvenku číst nemůže)
create or replace function public.is_admin()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.admins
    where email = lower(coalesce(auth.jwt() ->> 'email', ''))
  );
$$;

-- ---------- pravidla přístupu (Row Level Security) ----------
alter table public.events enable row level security;
alter table public.admins enable row level security;   -- bez pravidel = zvenku nepřístupná

drop policy if exists "akce cte kazdy"        on public.events;
drop policy if exists "akce pridava spravce"  on public.events;
drop policy if exists "akce upravuje spravce" on public.events;
drop policy if exists "akce maze spravce"     on public.events;

create policy "akce cte kazdy"        on public.events for select to anon, authenticated using (true);
create policy "akce pridava spravce"  on public.events for insert to authenticated with check (public.is_admin());
create policy "akce upravuje spravce" on public.events for update to authenticated using (public.is_admin()) with check (public.is_admin());
create policy "akce maze spravce"     on public.events for delete to authenticated using (public.is_admin());

grant select on public.events to anon, authenticated;
grant insert, update, delete on public.events to authenticated;
revoke all on public.admins from anon, authenticated;
grant execute on function public.is_admin() to anon, authenticated;

-- živé aktualizace webu (nová akce se ukáže i bez obnovení stránky)
do $$
begin
  alter publication supabase_realtime add table public.events;
exception when duplicate_object then null;
end $$;

-- ---------- současné akce z data/events.json ----------
insert into public.events (date, date_to, name, location, icao, status, lat, lng)
select * from (values
  (date '2027-11-11', date '2027-11-12', 'Letecký den',       'Hradec Králové (LKHK)', 'LKHK', 'confirmed', 50.2533, 15.8453),
  (date '2027-11-14', null::date,        'Letecký den Plzeň', 'Plzeň (LKLN)',          'LKLN', 'confirmed', 49.6753, 13.2744)
) as v(date, date_to, name, location, icao, status, lat, lng)
where not exists (select 1 from public.events);

-- =====================================================================
-- SPRÁVCI: e-maily lidí, kteří smí upravovat kalendář.
-- Napište sem skutečné e-maily (malými písmeny) a spusťte znovu jen tento řádek.
-- Stejné e-maily pak založte v Authentication → Users → Add user.
-- =====================================================================
-- insert into public.admins (email) values ('jmeno@example.com') on conflict do nothing;
