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


def parse_associations(readme_text: str) -> list[dict]:
    associations: list[dict] = []
    lines = readme_text.splitlines()
    i = 0
    current_source = None

    # Simple state machine to capture "Table Key to Table Key" patterns
    # This is heuristic based on the viewed format.

    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("-"):
            i += 1
            continue

        # Look for pattern: TableName KeyDescription
        match = re.match(r"^([A-Za-z0-9]+)\s+(.+)$", line)
        if match:
            table, key = match.groups()

            # Peek ahead for "to"
            if i + 2 < len(lines) and lines[i+2].strip().lower() == "to":
                # Check next line after "to"
                if i + 4 < len(lines):
                    target_line = lines[i+4].strip()
                    target_match = re.match(r"^([A-Za-z0-9]+)\s+(.+)$", target_line)
                    if target_match:
                        target_table, target_key = target_match.groups()
                        associations.append({
                            "source_table": table,
                            "source_key": key.strip(),
                            "target_table": target_table,
                            "target_key": target_key.strip()
                        })
                        i += 4
                        continue
        i += 1
    return associations


def ensure_required_tables(readme_text: str, required_tables: Iterable[str]) -> None:
    available = set(parse_available_tables(readme_text))
    missing = [table for table in required_tables if table not in available]
    if missing:
        raise ReadmeError(f"Readme missing required tables: {', '.join(missing)}")
