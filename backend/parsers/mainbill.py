from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_date, parse_csv_robust, convert_csv_issue

# Standard NJ Legislative Bill Types
VALID_BILL_TYPES = {
    "S", "A",
    "SR", "AR",
    "SCR", "ACR",
    "SJR", "AJR"
}

def parse_mainbill(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the MAINBILL.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    # Prepare markers for robust parsing
    # We include both "Type," and "Type " to catch various delimiters just in case,
    # but primarily commas for CSV.
    markers = []
    for bt in VALID_BILL_TYPES:
        markers.append(f"{bt},")
        markers.append(f'"{bt}",')
        # We also add markers for potential unquoted values at start of line
        # but risk false positives if a line starts with "A " (e.g. "A bill to...")
        # So we stick to comma which implies a column separation.

    parse_result = parse_csv_robust(path, row_start_markers=markers)
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

        # Validate Bill Type
        if bill_type not in VALID_BILL_TYPES:
            issues.append({
                "table": "bills",
                "record_key": f"{bill_type}-{bill_number}",
                "issue": "invalid_bill_type",
                "details": f"BillType '{bill_type}' is not a recognized NJ bill type.",
                "raw_data": str(row)
            })
             # We continue processing even if unknown type, but flag it.
             # Or should we skip? Let's process it, maybe it's a new type.

        try:
            bill_number_int = int(float(bill_number))
            if bill_number_int <= 0:
                issues.append({
                    "table": "bills",
                    "record_key": f"{bill_type}-{bill_number}",
                    "issue": "invalid_bill_number",
                    "details": f"BillNumber '{bill_number}' must be positive.",
                    "raw_data": str(row)
                })
                # Skip invalid numbers as they break primary key logic usually
                continue
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

        # Validate Row Integrity (e.g. Synopsis present?)
        synopsis = normalize_string(row.get("Synopsis"))
        if not synopsis:
             issues.append({
                "table": "bills",
                "record_key": bill_key,
                "issue": "missing_synopsis",
                "details": "Synopsis is missing or empty.",
                "raw_data": str(row)
            })

        records.append(
            {
                "bill_key": bill_key,
                "bill_type": bill_type.strip(),
                "bill_number": bill_number_int,
                "actual_bill_number": normalize_string(row.get("ActualBillNumber")),
                "current_status": normalize_string(row.get("CurrentStatus")),
                "intro_date": parse_date(row.get("IntroDate")),
                "ldoa": parse_date(row.get("LDOA")),
                "synopsis": synopsis,
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
