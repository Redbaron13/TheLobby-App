
import time
import tracemalloc
import json
import os
import shutil
import tempfile
from pathlib import Path
from backend.pipeline import _diff_rows, _diff_rows_using_hashes
from backend.snapshot import write_snapshot, load_latest_snapshot, load_latest_hashes

# Mock data generator
def generate_rows(count, start_id=0):
    rows = []
    for i in range(count):
        rows.append({
            "bill_key": f"BILL_{start_id + i}",
            "bill_number": start_id + i,
            "title": f"An act to do something important #{start_id + i}",
            "description": "This is a very long description that takes up memory " * 5,
            "status": "intro",
            "sponsors": ["Leg_1", "Leg_2", "Leg_3"]
        })
    return rows

def run_benchmark():
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        data_dir = Path(tmp_dir_str)
        processed_dir = data_dir / "processed" / "2023-01-01"
        processed_dir.mkdir(parents=True)

        row_count = 50000
        print(f"Generating {row_count} rows...")
        previous_rows = generate_rows(row_count)

        # Write "previous" snapshot
        print("Writing previous snapshot...")
        write_snapshot("bills", previous_rows, processed_dir)

        # Create "current" rows (mostly same, some changes)
        print("Generating current rows...")
        current_rows = generate_rows(row_count)
        # Modify 5% of rows
        for i in range(0, row_count, 20):
            current_rows[i]["status"] = "passed"
        # Add 100 new rows
        current_rows.extend(generate_rows(100, start_id=row_count))

        # Benchmark Loading + Diffing (Optimized)
        print("Starting benchmark (Optimized)...")
        tracemalloc.start()
        start_time = time.time()

        # 1. Load hashes
        loaded_hashes = load_latest_hashes(data_dir, "bills", exclude_date="2023-01-02")

        if loaded_hashes is None:
            print("ERROR: Hashes not found!")
            return

        # 2. Diff using hashes
        changes = _diff_rows_using_hashes(current_rows, loaded_hashes, "bill_key")

        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"Time taken: {end_time - start_time:.4f} seconds")
        print(f"Peak memory usage: {peak / 10**6:.2f} MB")
        print(f"Changes found: {len(changes)}")

        hash_file = processed_dir / "bills.hashes.json"
        if hash_file.exists():
            print(f"Verified: Hash file created at {hash_file}")
        else:
            print(f"Error: Hash file not found at {hash_file}")

if __name__ == "__main__":
    run_benchmark()
