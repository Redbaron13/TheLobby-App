from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_csv_robust, convert_csv_issue


HOUSE_MAP = {
    "S": "Senate",
    "A": "Assembly",
}


def parse_roster(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the ROSTER.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "legislators") for i in parse_result.issues]

    for row in parse_result.rows:
        roster_key = normalize_string(row.get("Roster Key"))
        if not roster_key:
            issues.append({
                "table": "legislators",
                "record_key": None,
                "issue": "missing_roster_key",
                "details": "Roster Key is missing",
                "raw_data": str(row)
            })
            continue
        try:
            roster_key_int = int(float(roster_key))
        except ValueError:
            issues.append({
                "table": "legislators",
                "record_key": roster_key,
                "issue": "invalid_roster_key",
                "details": f"Roster Key '{roster_key}' is not an integer",
                "raw_data": str(row)
            })
            continue

        district = normalize_string(row.get("District"))
        try:
            district_int = int(float(district)) if district else None
        except ValueError:
             issues.append({
                "table": "legislators",
                "record_key": str(roster_key_int),
                "issue": "invalid_district",
                "details": f"District '{district}' is not an integer",
                "raw_data": str(row)
            })
             continue

        house_raw = normalize_string(row.get("House"))
        house = HOUSE_MAP.get(house_raw or "", house_raw)

        records.append(
            {
                "roster_key": roster_key_int,
                "district": district_int,
                "house": house,
                "last_name": normalize_string(row.get("LastName")),
                "first_name": normalize_string(row.get("Firstname")),
                "mid_name": normalize_string(row.get("MidName")),
                "suffix": normalize_string(row.get("Suffix")),
                "sex": normalize_string(row.get("Sex")),
                "title": normalize_string(row.get("Title")),
                "leg_pos": normalize_string(row.get("LegPos")),
                "leg_status": normalize_string(row.get("LegStatus")),
                "party": normalize_string(row.get("Party")),
                "race": normalize_string(row.get("Race")),
                "address": normalize_string(row.get("Address")),
                "city": normalize_string(row.get("City")),
                "state": normalize_string(row.get("State")),
                "zipcode": normalize_string(row.get("Zipcode")),
                "phone": normalize_string(row.get("Phone")),
                "email": normalize_string(row.get("Email")),
            }
        )
    return records, issues
