from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_date, parse_csv_robust, convert_csv_issue


def parse_mainbill(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the MAINBILL.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "bills") for i in parse_result.issues]

    # 2. Process rows
    for row in parse_result.rows:
        bill_type = normalize_string(row.get("BillType"))
        bill_number = normalize_string(row.get("BillNumber"))

        # We need these to identify the record
        if not bill_type or not bill_number:
            issues.append({
                "table": "bills",
                "record_key": None,
                "issue": "missing_key_fields",
                "details": f"Missing BillType or BillNumber. Raw: {row}",
                "raw_data": str(row)
            })
            continue

        try:
            bill_number_int = int(float(bill_number))
        except ValueError:
            issues.append({
                "table": "bills",
                "record_key": f"{bill_type}-{bill_number}",
                "issue": "invalid_bill_number",
                "details": f"BillNumber '{bill_number}' is not an integer.",
                "raw_data": str(row)
            })
            continue

        bill_key = f"{bill_type.strip()}-{bill_number_int}"

        records.append(
            {
                "bill_key": bill_key,
                "bill_type": bill_type.strip(),
                "bill_number": bill_number_int,
                "actual_bill_number": normalize_string(row.get("ActualBillNumber")),
                "current_status": normalize_string(row.get("CurrentStatus")),
                "intro_date": parse_date(row.get("IntroDate")),
                "ldoa": parse_date(row.get("LDOA")),
                "synopsis": normalize_string(row.get("Synopsis")),
                "abstract": normalize_string(row.get("Abstract")),
                "first_prime": normalize_string(row.get("FirstPrime")),
                "second_prime": normalize_string(row.get("SecondPrime")),
                "third_prime": normalize_string(row.get("ThirdPrime")),
                "identical_bill_number": normalize_string(row.get("IdenticalBillNumber")),
                "last_session_full_bill_number": normalize_string(row.get("LastSessionFullBillNumber")),
                "old_bill_number": normalize_string(row.get("OldBillNumber")),
                "proposed_date": parse_date(row.get("ProposedDate")),
                "mod_date": parse_date(row.get("ModDate")),
                "fn_certified": normalize_string(row.get("FNCertified")),
            }
        )

    return records, issues
