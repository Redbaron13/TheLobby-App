from __future__ import annotations

import csv
from pathlib import Path

from .utils import normalize_string


HOUSE_MAP = {
    "S": "Senate",
    "A": "Assembly",
}


def parse_roster(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="latin1", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            roster_key = normalize_string(row.get("Roster Key"))
            if not roster_key:
                continue
            try:
                roster_key_int = int(float(roster_key))
            except ValueError:
                continue

            district = normalize_string(row.get("District"))
            district_int = int(float(district)) if district and district.isdigit() else None
            house_raw = normalize_string(row.get("House"))
            house = HOUSE_MAP.get(house_raw or "", house_raw)

            records.append(
                {
                    "roster_key": roster_key_int,
                    "district": district_int,
                    "house": house,
                    "last_name": normalize_string(row.get("LastName")),
                    "first_name": normalize_string(row.get("Firstname")),
                    "mid_name": normalize_string(row.get("MidName")),
                    "suffix": normalize_string(row.get("Suffix")),
                    "sex": normalize_string(row.get("Sex")),
                    "title": normalize_string(row.get("Title")),
                    "leg_pos": normalize_string(row.get("LegPos")),
                    "leg_status": normalize_string(row.get("LegStatus")),
                    "party": normalize_string(row.get("Party")),
                    "race": normalize_string(row.get("Race")),
                    "address": normalize_string(row.get("Address")),
                    "city": normalize_string(row.get("City")),
                    "state": normalize_string(row.get("State")),
                    "zipcode": normalize_string(row.get("Zipcode")),
                    "phone": normalize_string(row.get("Phone")),
                    "email": normalize_string(row.get("Email")),
                }
            )
    return records
