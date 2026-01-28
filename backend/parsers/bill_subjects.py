from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string


def parse_bill_subjects(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            bill_type = normalize_string(row.get("BillType"))
            bill_number = normalize_string(row.get("BillNumber"))
            subject_code = normalize_string(row.get("SubjectKey")) # Assuming SubjectKey links to SubjHeadings

            if not bill_type or not bill_number or not subject_code:
                continue

            try:
                bill_number_int = int(float(bill_number))
            except ValueError:
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
    return records
