from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_csv_robust, convert_csv_issue


def parse_committees(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the COMMITTEE.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "committees") for i in parse_result.issues]

    for row in parse_result.rows:
        code = normalize_string(row.get("Code"))
        if not code:
            issues.append({
                "table": "committees",
                "record_key": None,
                "issue": "missing_committee_code",
                "details": "Missing Code",
                "raw_data": str(row)
            })
            continue

        records.append(
            {
                "committee_code": code,
                "description": normalize_string(row.get("Description")),
                "house": normalize_string(row.get("House")),
            }
        )
    return records, issues
