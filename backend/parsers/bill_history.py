from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_date, parse_csv_robust, convert_csv_issue


def parse_bill_history(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the BILLHIST.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "bill_history") for i in parse_result.issues]

    for row in parse_result.rows:
        bill_type = normalize_string(row.get("BillType"))
        bill_number = normalize_string(row.get("BillNumber"))
        action = normalize_string(row.get("Action"))
        date_str = row.get("Date")

        if not bill_type or not bill_number:
            issues.append({
                "table": "bill_history",
                "record_key": None,
                "issue": "missing_key_fields",
                "details": "Missing BillType or BillNumber",
                "raw_data": str(row)
            })
            continue

        try:
            bill_number_int = int(float(bill_number))
        except ValueError:
            issues.append({
                "table": "bill_history",
                "record_key": f"{bill_type}-{bill_number}",
                "issue": "invalid_bill_number",
                "details": f"BillNumber '{bill_number}' is not numeric",
                "raw_data": str(row)
            })
            continue

        bill_key = f"{bill_type.strip()}-{bill_number_int}"

        action_by = normalize_string(row.get("ActionBy"))

        # Unique key construction
        bill_history_key = f"{bill_key}-{date_str}-{action}-{action_by}"[:255]

        records.append(
            {
                "bill_history_key": bill_history_key,
                "bill_key": bill_key,
                "bill_type": bill_type.strip(),
                "bill_number": bill_number_int,
                "action": action,
                "date": parse_date(date_str),
                "action_by": action_by,
                "session_year": normalize_string(row.get("SessionYear")),
            }
        )
    return records, issues
