from __future__ import annotations

from typing import Iterable


FORMER_STATUS_KEYWORDS = (
    "FORMER",
    "RETIRED",
    "RESIGNED",
    "DECEASED",
    "LEFT OFFICE",
    "INACTIVE",
)

ACTIVE_STATUS_KEYWORDS = (
    "ACTIVE",
    "SERVING",
    "INCUMBENT",
    "IN OFFICE",
)


def split_legislators(legislators: Iterable[dict]) -> tuple[list[dict], list[dict]]:
    active: list[dict] = []
    former: list[dict] = []
    for legislator in legislators:
        status = _normalize_status(legislator.get("leg_status"))
        if not status:
            active.append(legislator)
            continue
        if _has_keyword(status, FORMER_STATUS_KEYWORDS):
            former.append(legislator)
            continue
        if _has_keyword(status, ACTIVE_STATUS_KEYWORDS):
            active.append(legislator)
            continue
        active.append(legislator)
    return active, former


def _normalize_status(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip().upper()


def _has_keyword(status: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in status for keyword in keywords)
