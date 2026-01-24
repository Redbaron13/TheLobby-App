from __future__ import annotations

import re
from typing import Iterable


class ReadmeError(RuntimeError):
    pass


def parse_available_tables(readme_text: str) -> list[str]:
    tables: list[str] = []
    in_table_section = False
    for line in readme_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.upper().startswith("README"):
            in_table_section = True
            continue
        if cleaned.upper().startswith("AS OF JULY 20, 2012"):
            break
        if not in_table_section:
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9]*$", cleaned):
            tables.append(cleaned)
    return tables


def ensure_required_tables(readme_text: str, required_tables: Iterable[str]) -> None:
    available = set(parse_available_tables(readme_text))
    missing = [table for table in required_tables if table not in available]
    if missing:
        raise ReadmeError(f"Readme missing required tables: {', '.join(missing)}")
