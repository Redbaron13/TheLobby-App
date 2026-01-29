from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_csv_robust, convert_csv_issue


def parse_legislator_bios(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the LEGBIO.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "legislator_bios") for i in parse_result.issues]

    for row in parse_result.rows:
        roster_key = normalize_string(row.get("Roster Key"))
        if not roster_key:
            issues.append({
                "table": "legislator_bios",
                "record_key": None,
                "issue": "missing_roster_key",
                "details": "Missing Roster Key",
                "raw_data": str(row)
            })
            continue
        try:
            roster_key_int = int(float(roster_key))
        except ValueError:
            issues.append({
                "table": "legislator_bios",
                "record_key": roster_key,
                "issue": "invalid_roster_key",
                "details": f"Roster Key '{roster_key}' is not numeric",
                "raw_data": str(row)
            })
            continue

        records.append(
            {
                "roster_key": roster_key_int,
                "bio_text": normalize_string(row.get("Bio")),
            }
        )
    return records, issues
