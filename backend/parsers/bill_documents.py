from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_csv_robust, convert_csv_issue


def parse_bill_documents(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the BILLWP.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "bill_documents") for i in parse_result.issues]

    for row in parse_result.rows:
        bill_type = normalize_string(row.get("BillType"))
        bill_number = normalize_string(row.get("BillNumber"))
        doc_type = normalize_string(row.get("DocumentType"))

        if not bill_type or not bill_number:
            issues.append({
                "table": "bill_documents",
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
                "table": "bill_documents",
                "record_key": f"{bill_type}-{bill_number}",
                "issue": "invalid_bill_number",
                "details": f"BillNumber '{bill_number}' is not numeric",
                "raw_data": str(row)
            })
            continue

        bill_key = f"{bill_type.strip()}-{bill_number_int}"
        description = normalize_string(row.get("Description"))

        bill_document_key = f"{bill_key}-{doc_type}-{description}"[:200]
        bill_document_key = bill_document_key.replace(" ", "-")

        records.append(
            {
                "bill_document_key": bill_document_key,
                "bill_key": bill_key,
                "document_type": doc_type,
                "description": description,
                "year": normalize_string(row.get("Year")),
            }
        )
    return records, issues
