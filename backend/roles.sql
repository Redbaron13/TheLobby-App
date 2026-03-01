-- Roles for PostgREST (Local Dev mimic of Supabase)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'anon') THEN
    CREATE ROLE anon NOLOGIN;
    GRANT USAGE ON SCHEMA public TO anon;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO anon;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
  END IF;

  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authenticated') THEN
    CREATE ROLE authenticated NOLOGIN;
    GRANT USAGE ON SCHEMA public TO authenticated;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
    GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
  END IF;

  -- Grant usage to postgres user to be sure
  GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;

  -- Grant anon access to future tables too?
  -- Already handled by ALTER DEFAULT PRIVILEGES above but only for user creating them?
  -- If backend connects as 'postgres' and creates tables, then default privileges for 'postgres' apply.
  -- So we need to ensure 'postgres' grants to 'anon'.
  -- The above ALTER DEFAULT PRIVILEGES statement applies to the current user (postgres).
END
$$;
