from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_date, parse_csv_robust, convert_csv_issue


def parse_bill_sponsors(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the BILLSPON.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "bill_sponsors") for i in parse_result.issues]

    for row in parse_result.rows:
        bill_type = normalize_string(row.get("BillType"))
        bill_number = normalize_string(row.get("BillNumber"))
        sequence = normalize_string(row.get("Sequence"))

        if not bill_type or not bill_number or not sequence:
            issues.append({
                "table": "bill_sponsors",
                "record_key": None,
                "issue": "missing_key_fields",
                "details": "Missing BillType, BillNumber, or Sequence",
                "raw_data": str(row)
            })
            continue

        try:
            bill_number_int = int(float(bill_number))
            sequence_int = int(float(sequence))
        except ValueError:
            issues.append({
                "table": "bill_sponsors",
                "record_key": f"{bill_type}-{bill_number}-{sequence}",
                "issue": "invalid_numeric_field",
                "details": f"BillNumber '{bill_number}' or Sequence '{sequence}' is not numeric",
                "raw_data": str(row)
            })
            continue

        bill_key = f"{bill_type.strip()}-{bill_number_int}"
        sponsor = normalize_string(row.get("Sponsor"))
        bill_sponsor_key = f"{bill_key}-{sequence_int}"

        records.append(
            {
                "bill_sponsor_key": bill_sponsor_key,
                "bill_key": bill_key,
                "bill_type": bill_type.strip(),
                "bill_number": bill_number_int,
                "sequence": sequence_int,
                "sponsor": sponsor,
                "sponsor_type": normalize_string(row.get("Type")),
                "status": normalize_string(row.get("Status")),
                "spon_date": parse_date(row.get("SponDate")),
                "with_date": parse_date(row.get("WithDate")),
                "mod_date": parse_date(row.get("ModDate")),
            }
        )
    return records, issues
