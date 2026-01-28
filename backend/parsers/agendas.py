from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string, parse_date


def parse_agendas(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Key = CommHouse + Date + Time + Type
            comm_house = normalize_string(row.get("CommHouse"))
            date_str = row.get("Date")
            time_str = normalize_string(row.get("Time"))
            agenda_type = normalize_string(row.get("Type"))

            if not comm_house or not date_str:
                continue

            agenda_key = f"{comm_house}-{date_str}-{time_str}-{agenda_type}"

            records.append(
                {
                    "agenda_key": agenda_key,
                    "committee_code": comm_house, # Assuming CommHouse maps to committee code
                    "house": normalize_string(row.get("House")), # If available
                    "date": parse_date(date_str),
                    "time": time_str,
                    "agenda_type": agenda_type,
                    "location": normalize_string(row.get("Location")),
                    "description": normalize_string(row.get("Description")),
                }
            )
    return records


def parse_agenda_bills(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            comm_house = normalize_string(row.get("CommHouse"))
            date_str = row.get("Date")
            time_str = normalize_string(row.get("Time"))
            agenda_type = normalize_string(row.get("Type"))

            bill_type = normalize_string(row.get("BillType"))
            bill_number = normalize_string(row.get("BillNumber"))

            if not comm_house or not date_str or not bill_type or not bill_number:
                continue

            try:
                bill_number_int = int(float(bill_number))
            except ValueError:
                continue

            agenda_key = f"{comm_house}-{date_str}-{time_str}-{agenda_type}"
            bill_key = f"{bill_type.strip()}-{bill_number_int}"
            agenda_bill_key = f"{agenda_key}-{bill_key}"

            records.append(
                {
                    "agenda_bill_key": agenda_bill_key,
                    "agenda_key": agenda_key,
                    "bill_key": bill_key,
                }
            )
    return records


def parse_agenda_nominees(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return []

    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            comm_house = normalize_string(row.get("CommHouse"))
            date_str = row.get("Date")
            time_str = normalize_string(row.get("Time"))
            agenda_type = normalize_string(row.get("Type"))

            nominee_name = normalize_string(row.get("NomineeName"))

            if not comm_house or not date_str or not nominee_name:
                continue

            agenda_key = f"{comm_house}-{date_str}-{time_str}-{agenda_type}"
            agenda_nominee_key = f"{agenda_key}-{nominee_name}"

            records.append(
                {
                    "agenda_nominee_key": agenda_nominee_key,
                    "agenda_key": agenda_key,
                    "nominee_name": nominee_name,
                    "position": normalize_string(row.get("Position")),
                }
            )
    return records
