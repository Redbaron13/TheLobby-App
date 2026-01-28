from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


def normalize_string(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def parse_date(value: str | None) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


@dataclass
class CsvParseResult:
    rows: List[Dict[str, str]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)


def parse_csv_robust(path: Path, encoding: str = "latin1") -> CsvParseResult:
    """
    Parses a CSV file robustly, capturing malformed rows instead of crashing.
    Returns a CsvParseResult containing valid rows and a list of issues.
    """
    result = CsvParseResult()
    if not path.exists():
        return result

    with path.open("r", encoding=encoding, newline="") as f:
        # Read header first
        try:
            reader = csv.reader(f)
            header = next(reader, None)
        except csv.Error as e:
            result.issues.append({
                "line_num": 1,
                "raw": "",
                "error": f"Failed to read header: {e}"
            })
            return result

        if not header:
            return result

        header_len = len(header)

        # Iterate remaining lines
        for line_num, row in enumerate(reader, start=2):
            if len(row) != header_len:
                # Row length mismatch
                result.issues.append({
                    "line_num": line_num,
                    "raw": ",".join(row), # Best effort reconstruction
                    "error": f"Column mismatch: expected {header_len}, got {len(row)}"
                })
                continue

            # Create dict
            row_dict = dict(zip(header, row))
            result.rows.append(row_dict)

    return result

def convert_csv_issue(csv_issue: Dict[str, Any], table: str) -> Dict[str, Any]:
    return {
        "table": table,
        "record_key": None,
        "issue": "csv_parsing_error",
        "details": f"Line {csv_issue.get('line_num')}: {csv_issue.get('error')}",
        "raw_data": csv_issue.get('raw')
    }
