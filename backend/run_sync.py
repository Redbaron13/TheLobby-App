from __future__ import annotations

import argparse
import sys
from pathlib import Path
import shutil

from backend.config import load_config
from backend.pipeline import run_pipeline
from backend.schema import load_schema_sql


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync NJ Legislature data to Supabase.")
    parser.add_argument("--date", help="Override run date (YYYY-MM-DD).", default=None)
    parser.add_argument("--init-schema", action="store_true", help="Print schema SQL and exit.")
    parser.add_argument("--reset-data", action="store_true", help="Delete local pipeline data and exit.")
    args = parser.parse_args()

    config = load_config()

    if args.init_schema:
        print(load_schema_sql())
        return 0

    if args.reset_data:
        if config.data_dir.exists():
            shutil.rmtree(config.data_dir)
        print(f"Removed local data directory: {config.data_dir}")
        return 0

    result = run_pipeline(config, args.date)

    print("Sync complete.")
    print(f"Bills: {result.bills}")
    print(f"Legislators: {result.legislators}")
    print(f"Bill sponsors: {result.bill_sponsors}")
    print(f"Committee members: {result.committee_members}")
    print(f"Vote records: {result.vote_records}")
    print(f"Districts: {result.districts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
