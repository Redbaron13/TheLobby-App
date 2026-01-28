from datetime import date

from backend.validation import (
    ValidationIssue,
    filter_to_recent_sessions,
    validate_bill_sponsors,
    validate_bills,
    validate_legislators,
)
from backend.session_filter import SessionWindow


def test_validate_bills_flags_key_mismatch() -> None:
    bills = [
        {"bill_key": "A-2", "bill_type": "A", "bill_number": 1},
        {"bill_key": "S-2", "bill_type": "S", "bill_number": 2, "intro_date": "2024-01-02", "mod_date": "2024-01-03"},
    ]
    result = validate_bills(bills)
    assert result.valid_rows == [bills[1]]
    assert any(issue.issue == "bill_key_mismatch" for issue in result.issues)


def test_validate_bill_sponsors_requires_existing_bill() -> None:
    bills = [{"bill_key": "S-2", "bill_type": "S", "bill_number": 2}]
    sponsors = [
        {"bill_sponsor_key": "S-2-1", "bill_key": "S-2"},
        {"bill_sponsor_key": "A-1-1", "bill_key": "A-1"},
    ]
    result = validate_bill_sponsors(sponsors, bills)
    assert result.valid_rows == [sponsors[0]]
    assert any(issue.issue == "unknown_bill_key" for issue in result.issues)


def test_validate_legislators_flags_invalid_district() -> None:
    legislators = [
        {"roster_key": 1, "district": 41},
        {"roster_key": 2, "district": 12},
    ]
    result = validate_legislators(legislators)
    assert result.valid_rows == [legislators[1]]
    assert ValidationIssue(
        table="legislators",
        record_key="1",
        issue="invalid_district",
        details="41",
    ) in result.issues


def test_filter_to_recent_sessions_filters_votes() -> None:
    session_window = SessionWindow(cutoff_date=date(2023, 1, 1), lookback_sessions=3, session_length_years=2)
    vote_records = [
        {"data": {"fields": {"VoteDate": "12/31/2022"}}},
        {"data": {"fields": {"VoteDate": "01/02/2023"}}},
    ]
    bills, sponsors, committee, votes = filter_to_recent_sessions(
        bills=[],
        bill_sponsors=[],
        committee_members=[],
        vote_records=vote_records,
        session_window=session_window,
    )
    assert votes == [vote_records[1]]
