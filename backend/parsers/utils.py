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


def parse_csv_robust(
    path: Path,
    encoding: str = "latin1",
    row_start_markers: Optional[List[str]] = None
) -> CsvParseResult:
    """
    Parses a CSV file robustly, capturing malformed rows and attempting to fix split rows.

    Args:
        path: Path to the CSV file.
        encoding: File encoding.
        row_start_markers: A list of valid strings that the first column MUST start with to be considered a new row.
                           If provided, lines NOT starting with one of these will be treated as continuations of the previous line.
                           Example for bills: ["S", "A", "SR", "AR", "SCR", "ACR", "SJR", "AJR"]
    """
    result = CsvParseResult()
    if not path.exists():
        return result

    try:
        with path.open("r", encoding=encoding, newline="") as f:
            all_lines = f.readlines()
    except Exception as e:
        result.issues.append({
            "line_num": 0,
            "raw": "",
            "error": f"Failed to read file: {e}"
        })
        return result

    if not all_lines:
        return result

    raw_lines = []
    # Header is always the first line
    header_line = all_lines[0].strip()
    raw_lines.append(header_line)

    if row_start_markers:
        # Smart reconstruction logic
        current_record_parts = []
        reconstructed_count = 0

        # Start from second line (index 1)
        for line in all_lines[1:]:
            stripped = line.strip()
            if not stripped:
                continue

            # Check if this line starts a new record
            # We check if the line STARTS with any of the markers followed by common delimiters or just the marker
            # Actually, typically it's "S,123,..." so starts with "S" is risky if "Synopsis" starts with "S".
            # Markers should be distinct.
            # For bills: S, A, etc. usually followed by a comma if it's a CSV.
            # But the raw line might be quoted: "S",...
            # We'll stick to simple startswith for now as provided by the user's heuristic.
            is_new_record = any(stripped.startswith(m) for m in row_start_markers)

            if is_new_record:
                # Flush previous record if exists
                if current_record_parts:
                    # Join with space to recover from newline split
                    full_line = " ".join(current_record_parts)
                    raw_lines.append(full_line)
                    if len(current_record_parts) > 1:
                        reconstructed_count += 1
                    current_record_parts = []

                current_record_parts.append(stripped)
            else:
                # Continuation
                current_record_parts.append(stripped)

        # Flush the final record
        if current_record_parts:
            full_line = " ".join(current_record_parts)
            raw_lines.append(full_line)
            if len(current_record_parts) > 1:
                reconstructed_count += 1

        if reconstructed_count > 0:
            # We log this as an "issue" just so the user sees it in the report,
            # but it's actually a successful repair.
            result.issues.append({
                "line_num": 0,
                "raw": f"Reconstructed {reconstructed_count} split records",
                "error": "Info: Split rows detected and merged based on start markers."
            })

    else:
        # Standard: just add all non-empty lines
        raw_lines.extend([line.strip() for line in all_lines[1:] if line.strip()])

    # Second pass: Parse CSV from the (potentially reconstructed) lines
    try:
        reader = csv.reader(raw_lines)
        header = next(reader, None)
    except csv.Error as e:
        result.issues.append({
            "line_num": 1,
            "raw": "",
            "error": f"Failed to parse header: {e}"
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
                "raw": ",".join(row),
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
