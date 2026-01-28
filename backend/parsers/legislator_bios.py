from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string


def parse_legislator_bios(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            roster_key = normalize_string(row.get("Roster Key"))
            if not roster_key:
                continue
            try:
                roster_key_int = int(float(roster_key))
            except ValueError:
                continue

            records.append(
                {
                    "roster_key": roster_key_int,
                    "bio_text": normalize_string(row.get("Bio")), # Assuming 'Bio' is the column
                    # Add other fields if present in LEGBIO
                }
            )
    return records
