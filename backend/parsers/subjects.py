from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_csv_robust, convert_csv_issue


def parse_subject_headings(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the SUBJHEADINGS.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "subject_headings") for i in parse_result.issues]

    for row in parse_result.rows:
        subj_abbrev = normalize_string(row.get("SubjAbbrev"))
        if not subj_abbrev:
            issues.append({
                "table": "subject_headings",
                "record_key": None,
                "issue": "missing_subject_code",
                "details": "Missing SubjAbbrev",
                "raw_data": str(row)
            })
            continue

        records.append(
            {
                "subject_code": subj_abbrev,
                "description": normalize_string(row.get("Description")),
            }
        )
    return records, issues
