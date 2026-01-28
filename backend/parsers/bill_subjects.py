from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_csv_robust, convert_csv_issue


def parse_bill_subjects(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the BILLSUBJ.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "bill_subjects") for i in parse_result.issues]

    for row in parse_result.rows:
        bill_type = normalize_string(row.get("BillType"))
        bill_number = normalize_string(row.get("BillNumber"))
        subject_code = normalize_string(row.get("SubjectKey"))

        if not bill_type or not bill_number or not subject_code:
            issues.append({
                "table": "bill_subjects",
                "record_key": None,
                "issue": "missing_key_fields",
                "details": "Missing BillType, BillNumber, or SubjectKey",
                "raw_data": str(row)
            })
            continue

        try:
            bill_number_int = int(float(bill_number))
        except ValueError:
            issues.append({
                "table": "bill_subjects",
                "record_key": f"{bill_type}-{bill_number}-{subject_code}",
                "issue": "invalid_bill_number",
                "details": f"BillNumber '{bill_number}' is not numeric",
                "raw_data": str(row)
            })
            continue

        bill_key = f"{bill_type.strip()}-{bill_number_int}"
        bill_subject_key = f"{bill_key}-{subject_code}"

        records.append(
            {
                "bill_subject_key": bill_subject_key,
                "bill_key": bill_key,
                "subject_code": subject_code,
            }
        )
    return records, issues
