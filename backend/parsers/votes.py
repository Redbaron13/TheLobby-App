from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


def _detect_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample)
    except csv.Error:
        return csv.excel


def parse_vote_file(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="latin1", newline="") as file:
        sample = file.read(2048)
        file.seek(0)
        dialect = _detect_dialect(sample)
        reader = csv.DictReader(file, dialect=dialect)
        for row in reader:
            normalized = {key.strip(): _normalize_value(value) for key, value in row.items() if key}
            data_payload = {"source_file": path.name, "fields": normalized}
            vote_record_key = _hash_payload(data_payload)
            records.append(
                {
                    "vote_record_key": vote_record_key,
                    "source_file": path.name,
                    "data": data_payload,
                }
            )
    return records


def _normalize_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _hash_payload(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
