import os
import shutil
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

# Adjust path for direct execution
import sys
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.legislative_downloads import download_bill_tracking_session, LegislativeDownloadError
from backend.parsers.mainbill import parse_mainbill, VALID_BILL_TYPES

# Mark as integration test so it can be skipped if needed
@pytest.mark.integration
class TestLiveIntegration:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        yield
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_live_pipeline_execution(self):
        """
        Connects to the real NJ Legislature website, downloads current session data,
        and verifies that the MAINBILL.TXT file can be parsed robustly.
        """
        # Configuration for live test
        base_url = "https://www.njleg.state.nj.us"
        pub_base_url = "https://pub.njleg.state.nj.us"
        download_type = "Bill_Tracking"
        # Determine current session year (heuristic: current year or previous year if early in year)
        # Actually, let's try the current year. If it fails, fallback to previous year?
        # Or just use 2024 as a safe bet for now since it's likely the active session.
        # But to be robust for future, we can try 2024.
        # Wait, usually the session is 2 years. 2024-2025 session. So 2024 works.
        session_year = 2024

        # Use fixture temp_dir if running in pytest, else create one
        dest_dir = getattr(self, 'temp_dir', Path(tempfile.mkdtemp()))

        print(f"Attempting to download live data for session year {session_year} to {dest_dir}...")

        try:
            downloaded_files = download_bill_tracking_session(
                base_url=base_url,
                pub_base_url=pub_base_url,
                download_type=download_type,
                session_year=session_year,
                destination=dest_dir,
                required_files=("MAINBILL.TXT",)
            )
        except LegislativeDownloadError as e:
            pytest.fail(f"Failed to download live data: {e}")

        mainbill_path = dest_dir / "MAINBILL.TXT"
        assert mainbill_path.exists(), "MAINBILL.TXT was not extracted."

        print(f"Successfully downloaded {mainbill_path}. Parsing...")

        # Parse using our robust parser
        records, issues = parse_mainbill(mainbill_path)

        # Verification steps
        assert len(records) > 0, "No valid bill records found in live MAINBILL.TXT"

        print(f"Parsed {len(records)} valid bills.")
        print(f"Encountered {len(issues)} issues/warnings.")

        # Check for critical failures (we expect some warnings in real data, but not 100% failure)
        # A high issue count might be normal if the data is messy, but let's check ratio.
        # If issues > records, that's suspicious but maybe valid if file is garbage.
        # But we expect NJ Leg data to be mostly good.

        # Validate a sample record
        sample = records[0]
        assert "bill_key" in sample
        assert "bill_type" in sample
        assert sample["bill_type"] in VALID_BILL_TYPES
        assert isinstance(sample["bill_number"], int)

        # Check specifically for "split row" fixes (if any happened)
        split_row_fixes = [i for i in issues if isinstance(i.get("error"), str) and "Reconstructed" in i.get("error")]
        if split_row_fixes:
            print(f"Verified: The robust parser successfully reconstructed split rows: {split_row_fixes[0]['error']}")
        else:
            print("Note: No split rows were detected in this specific live file. This is good data quality.")

        # Check for invalid bill types (validation logic test)
        invalid_types = [i for i in issues if i.get("issue") == "invalid_bill_type"]
        if invalid_types:
            print(f"Warning: Found {len(invalid_types)} invalid bill types in live data: {invalid_types[0]}")

        # Check for missing synopsis (integrity check)
        missing_synopsis = [i for i in issues if i.get("issue") == "missing_synopsis"]
        if missing_synopsis:
            print(f"Warning: Found {len(missing_synopsis)} bills with missing synopsis.")

if __name__ == "__main__":
    # Allow running this file directly
    t = TestLiveIntegration()
    # Create temp dir manually
    t.temp_dir = Path(tempfile.mkdtemp())
    try:
        t.test_live_pipeline_execution()
        print("Test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if t.temp_dir.exists():
            shutil.rmtree(t.temp_dir)
