-- Migration to add Full Text Search to bills table
-- This file extends the base schema defined in backend/schema.sql

-- Add generated column for Full Text Search on FirstPrime
-- Using 'simple' dictionary to avoid stemming proper names (e.g. 'Baker' staying 'Baker')
ALTER TABLE public.bills
ADD COLUMN IF NOT EXISTS fts_first_prime tsvector
GENERATED ALWAYS AS (to_tsvector('simple', coalesce(first_prime, ''))) STORED;

-- Add GIN index for fast searching
CREATE INDEX IF NOT EXISTS idx_bills_fts_first_prime ON public.bills USING GIN (fts_first_prime);
