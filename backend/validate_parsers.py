from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

from backend.parsers import parse_bill_sponsors, parse_committee_members, parse_mainbill, parse_roster


def main() -> None:
    sample_dir = Path("app/dataclean")
    if not sample_dir.exists():
        raise SystemExit("Sample data directory not found: app/dataclean")

    bills = parse_mainbill(sample_dir / "MAINBILL.TXT", session_year=2024)
    roster = parse_roster(sample_dir / "ROSTER.TXT", session_year=2024)
    sponsors = parse_bill_sponsors(sample_dir / "BILLSPON.TXT", session_year=2024)
    committees = parse_committee_members(sample_dir / "COMEMBER.TXT", session_year=2024)

    if not bills:
        raise SystemExit("No bills parsed from MAINBILL.TXT")
    if not roster:
        raise SystemExit("No legislators parsed from ROSTER.TXT")
    if not sponsors:
        raise SystemExit("No bill sponsors parsed from BILLSPON.TXT")
    if not committees:
        raise SystemExit("No committee members parsed from COMEMBER.TXT")

    print("Parser validation passed.")
    print(f"Bills: {len(bills)}")
    print(f"Legislators: {len(roster)}")
    print(f"Bill sponsors: {len(sponsors)}")
    print(f"Committee members: {len(committees)}")


if __name__ == "__main__":
    main()
