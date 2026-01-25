from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Sequence

from backend.session_filter import SessionWindow, filter_rows_by_date


@dataclass(frozen=True)
class ValidationIssue:
    table: str
    record_key: str | None
    issue: str
    details: str | None = None

    def as_dict(self, run_date: str | None = None) -> dict:
        payload = {
            "table_name": self.table,
            "record_key": self.record_key,
            "issue": self.issue,
            "details": self.details,
        }
        if run_date:
            payload["run_date"] = run_date
        return payload


@dataclass(frozen=True)
class ValidationResult:
    valid_rows: list[dict]
    issues: list[ValidationIssue]


def filter_to_recent_sessions(
    *,
    bills: list[dict],
    bill_sponsors: list[dict],
    committee_members: list[dict],
    vote_records: list[dict],
    session_window: SessionWindow,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    bills_filtered = filter_rows_by_date(
        bills,
        ["mod_date", "intro_date", "proposed_date", "ldoa"],
        session_window.cutoff_date,
    )
    bill_sponsors_filtered = filter_rows_by_date(
        bill_sponsors,
        ["mod_date", "spon_date", "with_date"],
        session_window.cutoff_date,
    )
    committee_members_filtered = filter_rows_by_date(
        committee_members,
        ["mod_date"],
        session_window.cutoff_date,
    )
    vote_records_filtered = _filter_vote_records(vote_records, session_window.cutoff_date)
    return (
        bills_filtered,
        bill_sponsors_filtered,
        committee_members_filtered,
        vote_records_filtered,
    )


def validate_bills(bills: list[dict]) -> ValidationResult:
    valid: list[dict] = []
    issues: list[ValidationIssue] = []
    for bill in bills:
        bill_key = bill.get("bill_key")
        bill_type = bill.get("bill_type")
        bill_number = bill.get("bill_number")
        if not bill_key or not bill_type or bill_number is None:
            issues.append(
                ValidationIssue(
                    table="bills",
                    record_key=bill_key,
                    issue="missing_required_fields",
                    details="bill_key, bill_type, and bill_number are required",
                )
            )
            continue
        expected_key = f"{bill_type}-{bill_number}"
        if bill_key != expected_key:
            issues.append(
                ValidationIssue(
                    table="bills",
                    record_key=bill_key,
                    issue="bill_key_mismatch",
                    details=f"expected {expected_key}",
                )
            )
            continue
        if not _dates_in_order(bill, "intro_date", "mod_date"):
            issues.append(
                ValidationIssue(
                    table="bills",
                    record_key=bill_key,
                    issue="invalid_date_order",
                    details="mod_date precedes intro_date",
                )
            )
            continue
        valid.append(bill)
    return ValidationResult(valid_rows=valid, issues=issues)


def validate_legislators(legislators: list[dict], *, table: str = "legislators") -> ValidationResult:
    valid: list[dict] = []
    issues: list[ValidationIssue] = []
    for legislator in legislators:
        roster_key = legislator.get("roster_key")
        if roster_key is None:
            issues.append(
                ValidationIssue(
                    table=table,
                    record_key=None,
                    issue="missing_roster_key",
                )
            )
            continue
        district = legislator.get("district")
        if district is not None and not (1 <= int(district) <= 40):
            issues.append(
                ValidationIssue(
                    table=table,
                    record_key=str(roster_key),
                    issue="invalid_district",
                    details=str(district),
                )
            )
            continue
        valid.append(legislator)
    return ValidationResult(valid_rows=valid, issues=issues)


def validate_bill_sponsors(bill_sponsors: list[dict], bills: Sequence[dict]) -> ValidationResult:
    bill_keys = {bill.get("bill_key") for bill in bills if bill.get("bill_key")}
    valid: list[dict] = []
    issues: list[ValidationIssue] = []
    for sponsor in bill_sponsors:
        sponsor_key = sponsor.get("bill_sponsor_key")
        bill_key = sponsor.get("bill_key")
        if not sponsor_key or not bill_key:
            issues.append(
                ValidationIssue(
                    table="bill_sponsors",
                    record_key=sponsor_key,
                    issue="missing_required_fields",
                )
            )
            continue
        if bill_key not in bill_keys:
            issues.append(
                ValidationIssue(
                    table="bill_sponsors",
                    record_key=sponsor_key,
                    issue="unknown_bill_key",
                    details=bill_key,
                )
            )
            continue
        valid.append(sponsor)
    return ValidationResult(valid_rows=valid, issues=issues)


def validate_committee_members(committee_members: list[dict]) -> ValidationResult:
    valid: list[dict] = []
    issues: list[ValidationIssue] = []
    for member in committee_members:
        key = member.get("committee_member_key")
        if not key:
            issues.append(
                ValidationIssue(
                    table="committee_members",
                    record_key=None,
                    issue="missing_committee_member_key",
                )
            )
            continue
        if not member.get("committee_code") or not member.get("member"):
            issues.append(
                ValidationIssue(
                    table="committee_members",
                    record_key=key,
                    issue="missing_required_fields",
                )
            )
            continue
        valid.append(member)
    return ValidationResult(valid_rows=valid, issues=issues)


def validate_vote_records(vote_records: list[dict]) -> ValidationResult:
    valid: list[dict] = []
    issues: list[ValidationIssue] = []
    for record in vote_records:
        key = record.get("vote_record_key")
        data = record.get("data")
        if not key or not data:
            issues.append(
                ValidationIssue(
                    table="vote_records",
                    record_key=key,
                    issue="missing_vote_payload",
                )
            )
            continue
        valid.append(record)
    return ValidationResult(valid_rows=valid, issues=issues)


def validate_districts(districts: list[dict]) -> ValidationResult:
    valid: list[dict] = []
    issues: list[ValidationIssue] = []
    for district in districts:
        key = district.get("district_key")
        if not key:
            issues.append(
                ValidationIssue(
                    table="districts",
                    record_key=None,
                    issue="missing_district_key",
                )
            )
            continue
        if not district.get("geometry_json"):
            issues.append(
                ValidationIssue(
                    table="districts",
                    record_key=key,
                    issue="missing_geometry",
                )
            )
            continue
        valid.append(district)
    return ValidationResult(valid_rows=valid, issues=issues)


def _dates_in_order(row: dict, start_field: str, end_field: str) -> bool:
    start = _parse_iso_date(row.get(start_field))
    end = _parse_iso_date(row.get(end_field))
    if not start or not end:
        return True
    return end >= start


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def _filter_vote_records(vote_records: Iterable[dict], cutoff: date) -> list[dict]:
    filtered: list[dict] = []
    for record in vote_records:
        vote_date = _extract_vote_date(record)
        if vote_date is None or vote_date >= cutoff:
            filtered.append(record)
    return filtered


def _extract_vote_date(record: dict) -> date | None:
    data = record.get("data") or {}
    fields = data.get("fields") or {}
    for key in ("VoteDate", "Date", "MeetingDate", "ActionDate"):
        value = fields.get(key)
        if value:
            parsed = _parse_vote_date(value)
            if parsed:
                return parsed
    return None


def _parse_vote_date(value: str) -> date | None:
    text = str(value).strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
