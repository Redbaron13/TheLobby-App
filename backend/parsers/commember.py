from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_date, parse_csv_robust, convert_csv_issue


def parse_committee_members(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the COMEMBER.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "committee_members") for i in parse_result.issues]

    for row in parse_result.rows:
        code = normalize_string(row.get("Code"))
        member = normalize_string(row.get("Member"))
        assignment = normalize_string(row.get("Assignment_to_Committee"))

        if not code or not member or not assignment:
             issues.append({
                "table": "committee_members",
                "record_key": f"{code}-{member}",
                "issue": "missing_key_fields",
                "details": "Missing Code, Member, or Assignment_to_Committee",
                "raw_data": str(row)
            })
             continue

        committee_member_key = f"{code}-{member}-{assignment}"

        records.append(
            {
                "committee_member_key": committee_member_key,
                "committee_code": code,
                "member": member,
                "position_on_committee": normalize_string(row.get("Position_on_Committee")),
                "assignment_to_committee": assignment,
                "mod_date": parse_date(row.get("ModDate")),
            }
        )
    return records, issues
