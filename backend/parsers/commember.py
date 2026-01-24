from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string, parse_date


def parse_committee_members(path: Path, session_year: int | None = None) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            code = normalize_string(row.get("Code"))
            member = normalize_string(row.get("Member"))
            assignment = normalize_string(row.get("Assignment_to_Committee"))
            if not code or not member or not assignment:
                continue

            session_prefix = f"{session_year}-" if session_year else ""
            committee_member_key = f"{session_prefix}{code}-{member}-{assignment}"

            records.append(
                {
                    "committee_member_key": committee_member_key,
                    "session_year": session_year,
                    "committee_code": code,
                    "member": member,
                    "position_on_committee": normalize_string(row.get("Position_on_Committee")),
                    "assignment_to_committee": assignment,
                    "mod_date": parse_date(row.get("ModDate")),
                }
            )
    return records
