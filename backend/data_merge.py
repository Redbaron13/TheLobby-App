from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Sequence


def merge_rows_by_key(
    rows: Iterable[dict],
    key: str,
    date_fields: Sequence[str],
) -> list[dict]:
    merged: dict[str, dict] = {}
    for row in rows:
        row_key = row.get(key)
        if row_key is None:
            continue
        row_key_str = str(row_key)
        existing = merged.get(row_key_str)
        if existing is None or _is_newer(row, existing, date_fields):
            merged[row_key_str] = row
    return list(merged.values())


def _is_newer(candidate: dict, existing: dict, date_fields: Sequence[str]) -> bool:
    candidate_date = _latest_date(candidate, date_fields)
    existing_date = _latest_date(existing, date_fields)
    if candidate_date and existing_date:
        return candidate_date > existing_date
    if candidate_date and not existing_date:
        return True
    return False


def _latest_date(row: dict, date_fields: Sequence[str]) -> date | None:
    latest: date | None = None
    for field in date_fields:
        value = row.get(field)
        if not value:
            continue
        parsed = _parse_iso_date(value)
        if parsed and (latest is None or parsed > latest):
            latest = parsed
    return latest


def _parse_iso_date(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None
