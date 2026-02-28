import pytest
from pathlib import Path
from backend.parsers.utils import parse_csv_robust

def test_parse_csv_robust_splits(tmp_path):
    # Create a CSV with split rows
    # Expected format: BillType, BillNumber, Synopsis
    # Broken row 2: "S,123,This is a synopsis\nthat was split."
    csv_content = (
        "BillType,BillNumber,Synopsis\n"
        "S,100,Normal Bill\n"
        "S,123,This is a synopsis\n"  # Split here
        "that was split.\n"
        "A,200,Another Normal Bill\n"
    )

    file_path = tmp_path / "broken.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    # Markers include "S," and "A,"
    markers = ["S,", "A,"]

    result = parse_csv_robust(file_path, encoding="utf-8", row_start_markers=markers)

    # Should result in 3 rows, not 4
    assert len(result.rows) == 3

    row2 = result.rows[1]
    assert row2["BillType"] == "S"
    assert row2["BillNumber"] == "123"
    # The synopsis should be joined with space
    assert row2["Synopsis"] == "This is a synopsis that was split."

    # Verify issue logged
    print(f"DEBUG: Issues found: {result.issues}")
    # The error message says "Split rows detected", the raw field has details
    assert any("Split rows detected" in str(i.get("error", "")) for i in result.issues)

def test_parse_csv_robust_no_split(tmp_path):
    csv_content = (
        "BillType,BillNumber,Synopsis\n"
        "S,100,Normal Bill\n"
        "A,200,Another Normal Bill\n"
    )
    file_path = tmp_path / "clean.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    markers = ["S,", "A,"]
    result = parse_csv_robust(file_path, encoding="utf-8", row_start_markers=markers)

    assert len(result.rows) == 2
    assert not any("Reconstructed" in str(i.get("error", "")) for i in result.issues)
