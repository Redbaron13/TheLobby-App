-- Core NJ Legislature tables for Supabase
create extension if not exists pgcrypto;
create extension if not exists postgis;

create table if not exists public.legislators (
  roster_key integer primary key,
  district integer,
  house text,
  last_name text,
  first_name text,
  mid_name text,
  suffix text,
  sex text,
  title text,
  leg_pos text,
  leg_status text,
  party text,
  race text,
  address text,
  city text,
  state text,
  zipcode text,
  phone text,
  email text,
  updated_at timestamptz default now()
);

create table if not exists public.former_legislators (
  roster_key integer primary key,
  district integer,
  house text,
  last_name text,
  first_name text,
  mid_name text,
  suffix text,
  sex text,
  title text,
  leg_pos text,
  leg_status text,
  party text,
  race text,
  address text,
  city text,
  state text,
  zipcode text,
  phone text,
  email text,
  updated_at timestamptz default now()
);

create table if not exists public.bills (
  bill_key text primary key,
  bill_type text,
  bill_number integer,
  actual_bill_number text,
  current_status text,
  intro_date date,
  ldoa date,
  synopsis text,
  abstract text,
  first_prime text,
  second_prime text,
  third_prime text,
  identical_bill_number text,
  last_session_full_bill_number text,
  old_bill_number text,
  proposed_date date,
  mod_date date,
  fn_certified text,
  updated_at timestamptz default now()
);

create table if not exists public.bill_sponsors (
  bill_sponsor_key text primary key,
  bill_key text references public.bills(bill_key),
  bill_type text,
  bill_number integer,
  sequence integer,
  sponsor text,
  sponsor_type text,
  status text,
  spon_date date,
  with_date date,
  mod_date date,
  updated_at timestamptz default now()
);

create table if not exists public.committee_members (
  committee_member_key text primary key,
  committee_code text,
  member text,
  position_on_committee text,
  assignment_to_committee text,
  mod_date date,
  updated_at timestamptz default now()
);

create table if not exists public.vote_records (
  vote_record_key text primary key,
  source_file text,
  data jsonb,
  updated_at timestamptz default now()
);

create table if not exists public.districts (
  district_key text primary key,
  district_number integer,
  name text,
  properties jsonb,
  geometry_json jsonb,
  updated_at timestamptz default now()
);

create table if not exists public.legislative_districts (
  id uuid primary key default gen_random_uuid(),
  chamber text not null check (chamber in ('A','S')),
  district_number int not null,
  geom geometry(MultiPolygon, 4326) not null,
  source_sr int not null,
  source_objectid int not null,
  valid_from date not null default current_date,
  valid_to date,
  created_at timestamptz not null default now(),
  unique (chamber, district_number, valid_to)
);

create table if not exists public.data_validation_issues (
  issue_id uuid primary key default gen_random_uuid(),
  run_date date,
  table_name text,
  record_key text,
  issue text,
  details text,
  created_at timestamptz default now()
);

create table if not exists public.draft_legislators (
  roster_key integer primary key,
  district integer,
  house text,
  last_name text,
  first_name text,
  mid_name text,
  suffix text,
  sex text,
  title text,
  leg_pos text,
  leg_status text,
  party text,
  race text,
  address text,
  city text,
  state text,
  zipcode text,
  phone text,
  email text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_bills (
  bill_key text primary key,
  bill_type text,
  bill_number integer,
  actual_bill_number text,
  current_status text,
  intro_date date,
  ldoa date,
  synopsis text,
  abstract text,
  first_prime text,
  second_prime text,
  third_prime text,
  identical_bill_number text,
  last_session_full_bill_number text,
  old_bill_number text,
  proposed_date date,
  mod_date date,
  fn_certified text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_bill_sponsors (
  bill_sponsor_key text primary key,
  bill_key text,
  bill_type text,
  bill_number integer,
  sequence integer,
  sponsor text,
  sponsor_type text,
  status text,
  spon_date date,
  with_date date,
  mod_date date,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_committee_members (
  committee_member_key text primary key,
  committee_code text,
  member text,
  position_on_committee text,
  assignment_to_committee text,
  mod_date date,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_vote_records (
  vote_record_key text primary key,
  source_file text,
  data jsonb,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_districts (
  district_key text primary key,
  district_number integer,
  name text,
  properties jsonb,
  geometry_json jsonb,
  run_date date,
  ingested_at timestamptz default now()
);

create index if not exists idx_bills_bill_number on public.bills(bill_number);
create index if not exists idx_legislators_district on public.legislators(district);
create index if not exists idx_former_legislators_district on public.former_legislators(district);
create index if not exists idx_bill_sponsors_bill_key on public.bill_sponsors(bill_key);
create index if not exists idx_vote_records_source_file on public.vote_records(source_file);
create index if not exists idx_districts_number on public.districts(district_number);
