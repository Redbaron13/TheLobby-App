from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
import urllib.error

from backend.config import PRIMARY_KEYS, PipelineConfig, draft_table_name
from backend.downloader import download_files, download_text_file
from backend.data_merge import merge_rows_by_key
from backend.legdb_readme import ensure_required_tables
from backend.legdb_downloader import download_legdb_session
from backend.legislative_downloads import (
    LegislativeDownloadError,
    download_bill_tracking_session,
)
from backend.arcgis import fetch_all_features
from backend.parsers import (
    parse_bill_sponsors,
    parse_committee_members,
    parse_mainbill,
    parse_roster,
    parse_vote_file,
    parse_districts,
)
from backend.snapshot import (
    backup_dir,
    create_backup,
    enforce_retention,
    load_latest_snapshot,
    should_create_backup,
    snapshot_dir,
    write_snapshot,
)
from backend.supabase_loader import SupabaseClient
from backend.votes_downloader import download_votes
from backend.session_filter import build_session_window
from backend.roster_split import split_legislators
from backend.validation import (
    filter_to_recent_sessions,
    validate_bill_sponsors,
    validate_bills,
    validate_committee_members,
    validate_districts,
    validate_legislators,
    validate_vote_records,
)


@dataclass
class PipelineResult:
    bills: int
    legislators: int
    former_legislators: int
    bill_sponsors: int
    committee_members: int
    vote_records: int
    districts: int
    validation_issues: int


def _index_by_key(rows: Iterable[dict], key: str) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for row in rows:
        value = row.get(key)
        if value is not None:
            indexed[str(value)] = row
    return indexed


def _diff_rows(current_rows: list[dict], previous_rows: list[dict], key: str) -> list[dict]:
    previous_map = _index_by_key(previous_rows, key)
    changed: list[dict] = []
    for row in current_rows:
        row_key = str(row.get(key))
        if row_key not in previous_map or previous_map[row_key] != row:
            changed.append(row)
    return changed


def run_pipeline(config: PipelineConfig, date_str: str | None = None) -> PipelineResult:
    if not config.supabase_url or not config.supabase_service_key:
        raise RuntimeError("Supabase URL and key are required to run the pipeline.")

    run_date = date_str or datetime.utcnow().strftime("%Y-%m-%d")
    raw_dir = config.data_dir / "raw" / run_date
    downloads_dir = raw_dir / "downloads"
    readme_path = download_text_file(config.legdb_readme_url, downloads_dir)
    readme_text = readme_path.read_text(encoding="latin1", errors="ignore")
    ensure_required_tables(
        readme_text,
        ("MainBill", "Roster", "BillSpon", "COMember"),
    )
    _download_bill_tracking(config, downloads_dir)
    _download_legdb_sessions(config, raw_dir / "legdb")
    votes_dir = raw_dir / "votes"
    vote_files = download_votes(config.votes_base_url, config.votes_readme_urls, votes_dir)
    feature_collection = fetch_all_features(config.gis_service_url)

    bills = parse_mainbill(downloads_dir / "MAINBILL.TXT")
    legislators = parse_roster(downloads_dir / "ROSTER.TXT")
    active_legislators, former_legislators = split_legislators(legislators)
    bill_sponsors = parse_bill_sponsors(downloads_dir / "BILLSPON.TXT")
    committee_members = parse_committee_members(downloads_dir / "COMEMBER.TXT")
    vote_records = []
    for vote_file in vote_files:
        vote_records.extend(parse_vote_file(vote_file))
    districts = parse_districts(feature_collection)

    session_window = build_session_window(
        config.session_lookback_count,
        config.session_length_years,
    )
    (
        bills,
        bill_sponsors,
        committee_members,
        vote_records,
    ) = filter_to_recent_sessions(
        bills=bills,
        bill_sponsors=bill_sponsors,
        committee_members=committee_members,
        vote_records=vote_records,
        session_window=session_window,
    )

    processed_dir = snapshot_dir(config.data_dir, run_date)
    write_snapshot("bills", bills, processed_dir)
    write_snapshot("legislators", active_legislators, processed_dir)
    write_snapshot("former_legislators", former_legislators, processed_dir)
    write_snapshot("bill_sponsors", bill_sponsors, processed_dir)
    write_snapshot("committee_members", committee_members, processed_dir)
    write_snapshot("vote_records", vote_records, processed_dir)
    write_snapshot("districts", districts, processed_dir)

    if should_create_backup(config.data_dir, run_date, config.backup_interval_days):
        create_backup(processed_dir, backup_dir(config.data_dir, run_date))

    bills_result = validate_bills(bills)
    legislators_result = validate_legislators(legislators)
    bill_sponsors_result = validate_bill_sponsors(bill_sponsors, bills_result.valid_rows)
    committee_members_result = validate_committee_members(committee_members)
    vote_records_result = validate_vote_records(vote_records)
    districts_result = validate_districts(districts)

    validation_issues = (
        bills_result.issues
        + legislators_result.issues
        + bill_sponsors_result.issues
        + committee_members_result.issues
        + vote_records_result.issues
        + districts_result.issues
    )

    client = SupabaseClient(config.supabase_url, config.supabase_service_key)

    _upload_draft(client, "bills", bills, run_date)
    _upload_draft(client, "legislators", legislators, run_date)
    _upload_draft(client, "bill_sponsors", bill_sponsors, run_date)
    _upload_draft(client, "committee_members", committee_members, run_date)
    _upload_draft(client, "vote_records", vote_records, run_date)
    _upload_draft(client, "districts", districts, run_date)

    if validation_issues:
        issue_payloads = [issue.as_dict(run_date=run_date) for issue in validation_issues]
        client.upsert("data_validation_issues", issue_payloads)

    _upload_changed(client, "bills", bills_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "legislators", legislators_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "bill_sponsors", bill_sponsors_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "committee_members", committee_members_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "vote_records", vote_records_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "districts", districts_result.valid_rows, config.data_dir, run_date)

    enforce_retention(config.data_dir, config.retention_days, config.backup_retention_count)

    return PipelineResult(
        bills=len(bills_result.valid_rows),
        legislators=len(legislators_result.valid_rows),
        bill_sponsors=len(bill_sponsors_result.valid_rows),
        committee_members=len(committee_members_result.valid_rows),
        vote_records=len(vote_records_result.valid_rows),
        districts=len(districts_result.valid_rows),
        validation_issues=len(validation_issues),
    )


def _download_bill_tracking(config: PipelineConfig, downloads_dir: Path) -> None:
    session_year = max(config.bill_tracking_years)
    try:
        download_bill_tracking_session(
            base_url="https://www.njleg.state.nj.us",
            pub_base_url="https://pub.njleg.state.nj.us",
            download_type=config.download_type,
            session_year=session_year,
            destination=downloads_dir,
            required_files=config.files_to_download,
        )
    except LegislativeDownloadError:
        download_files(config.base_url, config.files_to_download, downloads_dir)


def _download_legdb_sessions(config: PipelineConfig, destination: Path) -> list[Path]:
    downloaded: list[Path] = []
    for year in config.legdb_years:
        downloaded.extend(
            download_legdb_session(config.legdb_base_url, year, config.files_to_download, destination / str(year))
        )
    return downloaded


def _upload_changed(
    client: SupabaseClient,
    table: str,
    current_rows: list[dict],
    base_dir: Path,
    run_date: str,
) -> None:
    key = PRIMARY_KEYS[table]
    previous_rows = load_latest_snapshot(base_dir, table, exclude_date=run_date)
    changed_rows = _diff_rows(current_rows, previous_rows, key)
    client.upsert(table, changed_rows)


def _upload_draft(client: SupabaseClient, table: str, rows: list[dict], run_date: str) -> None:
    draft_table = draft_table_name(table)
    draft_rows = [{**row, "run_date": run_date} for row in rows]
    client.upsert(draft_table, draft_rows)
