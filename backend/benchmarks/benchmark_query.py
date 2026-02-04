import os
import time
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

def run_benchmark():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not set. Cannot run benchmark against live DB.")
        print("This script is designed to run in an environment with access to the Supabase Postgres instance.")
        return

    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Helper to run explain analyze
    def explain(query, params):
        cur.execute(f"EXPLAIN (ANALYZE, FORMAT JSON) {query}", params)
        return cur.fetchone()[0][0]

    sponsor_name = "Smith"  # Common name for testing

    print(f"\n--- Benchmarking Search for '{sponsor_name}' ---\n")

    # 1. Baseline: ILIKE with leading wildcard
    # Note: Using "FirstPrime" as per schema (the column name in code was 'FirstPrime' but in schema.sql it is 'first_prime')
    # The schema.sql uses snake_case, but the frontend code uses PascalCase in select?
    # Checking schema.sql, columns are snake_case (first_prime).
    # Supabase might auto-map or the frontend might be using an alias, or the schema in memory was snake_case.
    # Frontend code: .ilike('FirstPrime', ...)
    # Schema.sql: first_prime text
    # Postgres is case insensitive for unquoted identifiers, but 'FirstPrime' in ILIKE would match the column if it exists.
    # However, if the column is 'first_prime', quoting 'FirstPrime' in code might be an issue or handled by Supabase JS client.
    # For raw SQL, we use the actual column name 'first_prime'.

    query_baseline = """
        SELECT bill_key, actual_bill_number, synopsis, current_status
        FROM bills
        WHERE first_prime ILIKE %s
        ORDER BY intro_date DESC
        LIMIT 5
    """

    print("Running Baseline (ILIKE '%...%')...")
    try:
        plan_baseline = explain(query_baseline, (f"%{sponsor_name}%",))
        time_baseline = plan_baseline['Execution Time']
        print(f"Baseline Execution Time: {time_baseline:.3f} ms")
        print(f"Baseline Plan Node: {plan_baseline['Plan']['Node Type']}")
    except Exception as e:
        print(f"Baseline failed: {e}")

    # 2. Optimization: FTS
    # Using 'simple' config as defined in migration
    query_optimized = """
        SELECT bill_key, actual_bill_number, synopsis, current_status
        FROM bills
        WHERE fts_first_prime @@ to_tsquery('simple', %s)
        ORDER BY intro_date DESC
        LIMIT 5
    """

    # Text search query formatting: 'Smith' -> 'Smith' (prefix matching with :* is optional but usually good for autocomplete,
    # but here we are replacing contains so maybe just the word)
    search_term = f"{sponsor_name}:*"

    print("\nRunning Optimized (FTS)...")
    try:
        plan_optimized = explain(query_optimized, (search_term,))
        time_optimized = plan_optimized['Execution Time']
        print(f"Optimized Execution Time: {time_optimized:.3f} ms")
        print(f"Optimized Plan Node: {plan_optimized['Plan']['Node Type']}")

        if 'time_baseline' in locals():
            improvement = time_baseline / time_optimized
            print(f"\nSpeedup Factor: {improvement:.2f}x")
    except Exception as e:
        print(f"Optimized failed: {e}")
        print("Did you run the migration 'backend/migrations/001_add_fts_to_bills.sql'?")

    conn.close()

if __name__ == "__main__":
    run_benchmark()
