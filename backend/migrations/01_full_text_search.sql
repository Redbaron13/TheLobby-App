-- Add a tsvector column for full-text search
ALTER TABLE public.bills ADD COLUMN IF NOT EXISTS fts tsvector;

-- Create an index on the tsvector column using the 'simple' dictionary (as per memory)
CREATE INDEX IF NOT EXISTS idx_bills_fts ON public.bills USING GIN(fts);

-- Function to update the fts column
CREATE OR REPLACE FUNCTION update_bills_fts() RETURNS trigger AS $$
BEGIN
  -- We use the 'simple' dictionary as per instructions to prevent stemming proper nouns
  new.fts :=
    setweight(to_tsvector('simple', coalesce(new.synopsis, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(new.abstract, '')), 'B');
  RETURN new;
END
$$ LANGUAGE plpgsql;

-- Trigger to call the update function before insert or update
DROP TRIGGER IF EXISTS trg_bills_fts ON public.bills;
CREATE TRIGGER trg_bills_fts
BEFORE INSERT OR UPDATE OF synopsis, abstract ON public.bills
FOR EACH ROW EXECUTE FUNCTION update_bills_fts();

-- Backfill the fts column for existing records
UPDATE public.bills SET fts =
  setweight(to_tsvector('simple', coalesce(synopsis, '')), 'A') ||
  setweight(to_tsvector('simple', coalesce(abstract, '')), 'B')
WHERE fts IS NULL;

-- Function to search bills
CREATE OR REPLACE FUNCTION search_bills(query_text text)
RETURNS SETOF public.bills AS $$
DECLARE
  search_query tsquery;
BEGIN
  -- Convert query_text to a tsquery using plainto_tsquery (simple dictionary)
  -- plainto_tsquery is good for raw user input as it handles punctuation
  search_query := plainto_tsquery('simple', query_text);

  RETURN QUERY
  SELECT *
  FROM public.bills
  WHERE
    -- Match exact/partial bill number or sponsor name
    actual_bill_number ILIKE '%' || query_text || '%'
    OR first_prime ILIKE '%' || query_text || '%'
    -- Match full text search (only if query_text is valid tsquery)
    OR (search_query @@ fts AND search_query::text != '')
  ORDER BY
    -- Order by match on exact bill number first, then sponsor name, then full-text rank
    CASE WHEN actual_bill_number ILIKE query_text THEN 0 ELSE 1 END,
    CASE WHEN first_prime ILIKE query_text THEN 0 ELSE 1 END,
    COALESCE(ts_rank(fts, search_query), 0) DESC,
    bill_number DESC
  LIMIT 50;
END;
$$ LANGUAGE plpgsql STABLE;
