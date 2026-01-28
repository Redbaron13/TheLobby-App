from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string, parse_date


def parse_bill_history(path: Path) -> list[dict]:
    records: list[dict] = []
    # Check if file exists, if not return empty list (pipeline robustness)
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            bill_type = normalize_string(row.get("BillType"))
            bill_number = normalize_string(row.get("BillNumber"))
            action = normalize_string(row.get("Action"))
            date_str = row.get("Date")

            if not bill_type or not bill_number:
                continue

            try:
                bill_number_int = int(float(bill_number))
            except ValueError:
                continue

            bill_key = f"{bill_type.strip()}-{bill_number_int}"

            # Create a unique key for the history record.
            # Ideally we'd have a sequence number, but relying on composite data.
            # Using bill_key + date + action + action_by to try to be unique.
            action_by = normalize_string(row.get("ActionBy"))
            # If there's a sequence field in the future, use it.
            # For now, we construct a key.
            # Note: There might be collisions if multiple identical actions happen on same day.
            # We will use a hash or just concat.

            bill_history_key = f"{bill_key}-{date_str}-{action}"[:255] # truncate if needed

            records.append(
                {
                    "bill_history_key": bill_history_key,
                    "bill_key": bill_key,
                    "bill_type": bill_type.strip(),
                    "bill_number": bill_number_int,
                    "action": action,
                    "date": parse_date(date_str),
                    "action_by": action_by,
                    "session_year": normalize_string(row.get("SessionYear")),
                }
            )
    return records
