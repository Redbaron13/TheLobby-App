from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string


def parse_bill_documents(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            bill_type = normalize_string(row.get("BillType"))
            bill_number = normalize_string(row.get("BillNumber"))
            doc_type = normalize_string(row.get("DocumentType"))

            if not bill_type or not bill_number:
                continue

            try:
                bill_number_int = int(float(bill_number))
            except ValueError:
                continue

            bill_key = f"{bill_type.strip()}-{bill_number_int}"
            description = normalize_string(row.get("Description"))
            # Generate a key.
            bill_document_key = f"{bill_key}-{doc_type}-{description}"[:200]

            records.append(
                {
                    "bill_document_key": bill_document_key,
                    "bill_key": bill_key,
                    "document_type": doc_type,
                    "description": description,
                    "year": normalize_string(row.get("Year")),
                }
            )
    return records
