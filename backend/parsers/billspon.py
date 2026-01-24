from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string, parse_date


def parse_bill_sponsors(path: Path, session_year: int | None = None) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            bill_type = normalize_string(row.get("BillType"))
            bill_number = normalize_string(row.get("BillNumber"))
            sequence = normalize_string(row.get("Sequence"))
            if not bill_type or not bill_number or not sequence:
                continue
            try:
                bill_number_int = int(float(bill_number))
                sequence_int = int(float(sequence))
            except ValueError:
                continue

            session_prefix = f"{session_year}-" if session_year else ""
            bill_key = f"{session_prefix}{bill_type.strip()}-{bill_number_int}"
            sponsor = normalize_string(row.get("Sponsor"))
            bill_sponsor_key = f"{bill_key}-{sequence_int}"

            records.append(
                {
                    "bill_sponsor_key": bill_sponsor_key,
                    "bill_key": bill_key,
                    "session_year": session_year,
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
    return records
