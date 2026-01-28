from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string


def parse_subject_headings(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Based on README: SubjHeadings SubjAbbrev
            subj_abbrev = normalize_string(row.get("SubjAbbrev"))
            if not subj_abbrev:
                continue

            records.append(
                {
                    "subject_code": subj_abbrev,
                    "description": normalize_string(row.get("SubjectHeading")), # Guessing column name
                }
            )
    return records
