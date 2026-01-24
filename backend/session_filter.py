from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Sequence


@dataclass(frozen=True)
class SessionWindow:
    cutoff_date: date
    lookback_sessions: int
    session_length_years: int


def build_session_window(
    lookback_sessions: int,
    session_length_years: int,
    today: date | None = None,
) -> SessionWindow:
    if lookback_sessions < 1:
        raise ValueError("lookback_sessions must be at least 1.")
    if session_length_years < 1:
        raise ValueError("session_length_years must be at least 1.")
    current = today or date.today()
    cutoff_year = current.year - (lookback_sessions * session_length_years)
    cutoff = date(cutoff_year, 1, 1)
    return SessionWindow(
        cutoff_date=cutoff,
        lookback_sessions=lookback_sessions,
        session_length_years=session_length_years,
    )


def filter_rows_by_date(
    rows: Iterable[dict],
    date_fields: Sequence[str],
    cutoff: date,
) -> list[dict]:
    filtered: list[dict] = []
    for row in rows:
        if _row_is_recent(row, date_fields, cutoff):
            filtered.append(row)
    return filtered


def _row_is_recent(row: dict, date_fields: Sequence[str], cutoff: date) -> bool:
    seen_date = False
    for field in date_fields:
        value = row.get(field)
        if not value:
            continue
        parsed = _parse_iso_date(value)
        if not parsed:
            continue
        seen_date = True
        if parsed >= cutoff:
            return True
    return not seen_date


def _parse_iso_date(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None
