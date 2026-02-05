
import json
import shutil
from pathlib import Path
from backend.snapshot import write_snapshot, load_latest_hashes, compute_row_hash
from backend.pipeline import _diff_rows_using_hashes

def test_compute_row_hash():
    row1 = {"id": 1, "val": "a"}
    row2 = {"val": "a", "id": 1} # Same content, different order
    row3 = {"id": 1, "val": "b"}

    # Hash should be deterministic regarding key order
    assert compute_row_hash(row1) == compute_row_hash(row2)
    assert compute_row_hash(row1) != compute_row_hash(row3)

def test_snapshot_hashing_roundtrip(tmp_path):
    # Setup
    rows = [
        {"id": "1", "val": "a"},
        {"id": "2", "val": "b"}
    ]
    # We need to mock PRIMARY_KEYS for "test_table" or just use a known table
    # write_snapshot looks up PRIMARY_KEYS.
    # Let's mock backend.snapshot.PRIMARY_KEYS using monkeypatch if pytest
    # But simpler: just use a table known in config, e.g. "bills" (key: bill_key)

    rows = [
        {"bill_key": "1", "val": "a"},
        {"bill_key": "2", "val": "b"}
    ]

    write_snapshot("bills", rows, tmp_path)

    # Check file exists
    hash_file = tmp_path / "bills.hashes.json"
    assert hash_file.exists()

    # Check content
    with hash_file.open() as f:
        hashes = json.load(f)

    assert "1" in hashes
    assert "2" in hashes
    assert hashes["1"] == compute_row_hash(rows[0])

def test_diff_rows_using_hashes():
    previous_rows = [
        {"bill_key": "1", "val": "a"},
        {"bill_key": "2", "val": "b"},
        {"bill_key": "3", "val": "c"}
    ]
    previous_hashes = {
        "1": compute_row_hash(previous_rows[0]),
        "2": compute_row_hash(previous_rows[1]),
        "3": compute_row_hash(previous_rows[2]),
    }

    current_rows = [
        {"bill_key": "1", "val": "a"},       # Same
        {"bill_key": "2", "val": "b_mod"},   # Changed
        {"bill_key": "4", "val": "d"}        # New
    ]

    changed = _diff_rows_using_hashes(current_rows, previous_hashes, "bill_key")

    # Expect: 2 (changed) and 4 (new). 1 is ignored. 3 is missing (deleted) but diff only returns changed/new current rows.

    changed_keys = sorted([r["bill_key"] for r in changed])
    assert changed_keys == ["2", "4"]
