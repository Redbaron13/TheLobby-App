from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


def _detect_dialect(sample: str) -> csv.Dialect | type[csv.Dialect]:
    try:
        return csv.Sniffer().sniff(sample)
    except csv.Error:
        return csv.excel


def parse_vote_file(path: Path) -> tuple[list[dict], list[dict]]:
    """
    Parses a vote CSV file.
    Returns (valid_records, issues).
    """
    records: list[dict] = []
    issues: list[dict] = []

    if not path.exists():
        return records, issues

    with path.open("r", encoding="latin1", newline="") as file:
        try:
            sample = file.read(2048)
            file.seek(0)
            dialect = _detect_dialect(sample)
            reader = csv.reader(file, dialect=dialect)
        except csv.Error as e:
            issues.append({
                "table": "vote_records",
                "record_key": None,
                "issue": "csv_init_error",
                "details": f"Failed to initialize CSV reader for {path.name}: {e}",
                "raw_data": ""
            })
            return records, issues

        try:
            header = next(reader, None)
        except csv.Error as e:
            issues.append({
                "table": "vote_records",
                "record_key": None,
                "issue": "header_read_error",
                "details": f"Failed to read header: {e}",
                "raw_data": ""
            })
            return records, issues

        if not header:
            return records, issues

        header_len = len(header)

        for line_num, row in enumerate(reader, start=2):
            if len(row) != header_len:
                issues.append({
                    "table": "vote_records",
                    "record_key": None,
                    "issue": "column_mismatch",
                    "details": f"Expected {header_len} columns, got {len(row)} in {path.name}",
                    "raw_data": ",".join(row)
                })
                continue

            # Create dict manually
            row_dict = dict(zip(header, row))

            normalized = {key.strip(): _normalize_value(value) for key, value in row_dict.items() if key}
            data_payload = {"source_file": path.name, "fields": normalized}
            vote_record_key = _hash_payload(data_payload)
            records.append(
                {
                    "vote_record_key": vote_record_key,
                    "source_file": path.name,
                    "data": data_payload,
                }
            )

    return records, issues


def _normalize_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _hash_payload(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
