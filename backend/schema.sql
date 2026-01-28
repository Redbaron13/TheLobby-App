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

-- New Tables

create table if not exists public.bill_history (
  bill_history_key text primary key,
  bill_key text references public.bills(bill_key),
  bill_type text,
  bill_number integer,
  action text,
  date date,
  action_by text,
  session_year text,
  updated_at timestamptz default now()
);

create table if not exists public.bill_subjects (
  bill_subject_key text primary key,
  bill_key text references public.bills(bill_key),
  subject_code text,
  updated_at timestamptz default now()
);

create table if not exists public.bill_documents (
  bill_document_key text primary key,
  bill_key text references public.bills(bill_key),
  document_type text,
  description text,
  year text,
  updated_at timestamptz default now()
);

create table if not exists public.committees (
  committee_code text primary key,
  description text,
  house text,
  updated_at timestamptz default now()
);

create table if not exists public.agendas (
  agenda_key text primary key,
  committee_code text,
  house text,
  date date,
  time text,
  agenda_type text,
  location text,
  description text,
  updated_at timestamptz default now()
);

create table if not exists public.agenda_bills (
  agenda_bill_key text primary key,
  agenda_key text references public.agendas(agenda_key),
  bill_key text references public.bills(bill_key),
  updated_at timestamptz default now()
);

create table if not exists public.agenda_nominees (
  agenda_nominee_key text primary key,
  agenda_key text references public.agendas(agenda_key),
  nominee_name text,
  position text,
  updated_at timestamptz default now()
);

create table if not exists public.legislator_bios (
  roster_key integer primary key references public.legislators(roster_key),
  bio_text text,
  updated_at timestamptz default now()
);

create table if not exists public.subject_headings (
  subject_code text primary key,
  description text,
  updated_at timestamptz default now()
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

-- Draft Tables (Staging)

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

create table if not exists public.draft_bill_history (
  bill_history_key text primary key,
  bill_key text,
  bill_type text,
  bill_number integer,
  action text,
  date date,
  action_by text,
  session_year text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_bill_subjects (
  bill_subject_key text primary key,
  bill_key text,
  subject_code text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_bill_documents (
  bill_document_key text primary key,
  bill_key text,
  document_type text,
  description text,
  year text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_committees (
  committee_code text primary key,
  description text,
  house text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_agendas (
  agenda_key text primary key,
  committee_code text,
  house text,
  date date,
  time text,
  agenda_type text,
  location text,
  description text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_agenda_bills (
  agenda_bill_key text primary key,
  agenda_key text,
  bill_key text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_agenda_nominees (
  agenda_nominee_key text primary key,
  agenda_key text,
  nominee_name text,
  position text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_legislator_bios (
  roster_key integer primary key,
  bio_text text,
  run_date date,
  ingested_at timestamptz default now()
);

create table if not exists public.draft_subject_headings (
  subject_code text primary key,
  description text,
  run_date date,
  ingested_at timestamptz default now()
);

-- Indexes

create index if not exists idx_bills_bill_number on public.bills(bill_number);
create index if not exists idx_legislators_district on public.legislators(district);
create index if not exists idx_former_legislators_district on public.former_legislators(district);
create index if not exists idx_bill_sponsors_bill_key on public.bill_sponsors(bill_key);
create index if not exists idx_vote_records_source_file on public.vote_records(source_file);
create index if not exists idx_districts_number on public.districts(district_number);

-- New Indexes
create index if not exists idx_bill_history_bill_key on public.bill_history(bill_key);
create index if not exists idx_bill_subjects_bill_key on public.bill_subjects(bill_key);
create index if not exists idx_bill_documents_bill_key on public.bill_documents(bill_key);
create index if not exists idx_agenda_bills_agenda_key on public.agenda_bills(agenda_key);
create index if not exists idx_agenda_bills_bill_key on public.agenda_bills(bill_key);
create index if not exists idx_agenda_nominees_agenda_key on public.agenda_nominees(agenda_key);
create index if not exists idx_agendas_committee_code on public.agendas(committee_code);
create index if not exists idx_committee_members_committee_code on public.committee_members(committee_code);
