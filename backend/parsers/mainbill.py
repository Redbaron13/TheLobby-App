from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string, parse_date


def parse_mainbill(path: Path, session_year: int | None = None) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            bill_type = normalize_string(row.get("BillType"))
            bill_number = normalize_string(row.get("BillNumber"))
            if not bill_type or not bill_number:
                continue

            try:
                bill_number_int = int(float(bill_number))
            except ValueError:
                continue

            session_prefix = f"{session_year}-" if session_year else ""
            bill_key = f"{session_prefix}{bill_type.strip()}-{bill_number_int}"
            records.append(
                {
                    "bill_key": bill_key,
                    "session_year": session_year,
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
    return records
