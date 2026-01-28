from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string


def parse_committees(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            code = normalize_string(row.get("Code"))
            if not code:
                continue

            records.append(
                {
                    "committee_code": code,
                    "description": normalize_string(row.get("Description")),
                    "house": normalize_string(row.get("House")),
                }
            )
    return records
