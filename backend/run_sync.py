from __future__ import annotations

import argparse
import sys

from backend.config import load_config
from backend.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync NJ Legislature data to Supabase.")
    parser.add_argument("--date", help="Override run date (YYYY-MM-DD).", default=None)
    args = parser.parse_args()

    config = load_config()
    result = run_pipeline(config, args.date)

    print("Sync complete.")
    print(f"Bills: {result.bills}")
    print(f"Legislators: {result.legislators}")
    print(f"Former legislators: {result.former_legislators}")
    print(f"Bill sponsors: {result.bill_sponsors}")
    print(f"Committee members: {result.committee_members}")
    print(f"Vote records: {result.vote_records}")
    print(f"Districts: {result.districts}")
    print(f"Validation issues: {result.validation_issues}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
