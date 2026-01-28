from __future__ import annotations

from pathlib import Path

from .utils import normalize_string, parse_date, parse_csv_robust, convert_csv_issue


def parse_agendas(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the AGENDAS.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "agendas") for i in parse_result.issues]

    for row in parse_result.rows:
        comm_house = normalize_string(row.get("CommHouse"))
        date_str = row.get("Date")
        time_str = normalize_string(row.get("Time"))
        agenda_type = normalize_string(row.get("Type"))

        if not comm_house or not date_str:
            issues.append({
                "table": "agendas",
                "record_key": None,
                "issue": "missing_key_fields",
                "details": "Missing CommHouse or Date",
                "raw_data": str(row)
            })
            continue

        agenda_key = f"{comm_house}-{date_str}-{time_str}-{agenda_type}"

        records.append(
            {
                "agenda_key": agenda_key,
                "committee_code": comm_house,
                "house": normalize_string(row.get("House")),
                "date": parse_date(date_str),
                "time": time_str,
                "agenda_type": agenda_type,
                "location": normalize_string(row.get("Location")),
                "description": normalize_string(row.get("Description")),
            }
        )
    return records, issues


def parse_agenda_bills(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the BAGENDA.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "agenda_bills") for i in parse_result.issues]

    for row in parse_result.rows:
        comm_house = normalize_string(row.get("CommHouse"))
        date_str = row.get("Date")
        time_str = normalize_string(row.get("Time"))
        agenda_type = normalize_string(row.get("Type"))

        bill_type = normalize_string(row.get("BillType"))
        bill_number = normalize_string(row.get("BillNumber"))

        if not comm_house or not date_str or not bill_type or not bill_number:
            issues.append({
                "table": "agenda_bills",
                "record_key": None,
                "issue": "missing_key_fields",
                "details": "Missing CommHouse, Date, BillType, or BillNumber",
                "raw_data": str(row)
            })
            continue

        try:
            bill_number_int = int(float(bill_number))
        except ValueError:
            issues.append({
                "table": "agenda_bills",
                "record_key": f"{bill_type}-{bill_number}",
                "issue": "invalid_bill_number",
                "details": f"BillNumber '{bill_number}' is not numeric",
                "raw_data": str(row)
            })
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
    return records, issues


def parse_agenda_nominees(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses the NAGENDA.TXT file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []

    parse_result = parse_csv_robust(path)
    issues = [convert_csv_issue(i, "agenda_nominees") for i in parse_result.issues]

    for row in parse_result.rows:
        comm_house = normalize_string(row.get("CommHouse"))
        date_str = row.get("Date")
        time_str = normalize_string(row.get("Time"))
        agenda_type = normalize_string(row.get("Type"))

        nominee_name = normalize_string(row.get("NomineeName"))

        if not comm_house or not date_str or not nominee_name:
            issues.append({
                "table": "agenda_nominees",
                "record_key": None,
                "issue": "missing_key_fields",
                "details": "Missing CommHouse, Date, or NomineeName",
                "raw_data": str(row)
            })
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
    return records, issues
