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
    parse_bill_history,
    parse_bill_subjects,
    parse_bill_documents,
    parse_committees,
    parse_agendas,
    parse_agenda_bills,
    parse_agenda_nominees,
    parse_legislator_bios,
    parse_subject_headings,
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
    ValidationIssue,
    filter_to_recent_sessions,
    validate_bill_sponsors,
    validate_bills,
    validate_committee_members,
    validate_districts,
    validate_legislators,
    validate_vote_records,
    validate_bill_history,
    validate_bill_subjects,
    validate_bill_documents,
    validate_committees,
    validate_agendas,
    validate_agenda_bills,
    validate_agenda_nominees,
    validate_legislator_bios,
    validate_subject_headings,
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
    bill_history: int
    bill_subjects: int
    bill_documents: int
    committees: int
    agendas: int
    agenda_bills: int
    agenda_nominees: int
    legislator_bios: int
    subject_headings: int


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


def _to_validation_issues(issues_dicts: list[dict]) -> list[ValidationIssue]:
    return [ValidationIssue(**i) for i in issues_dicts]


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
        ("MainBill", "Roster", "BillSpon", "COMember", "BillHist", "BillSubj", "BillWP", "Committee", "Agendas", "BAgendas", "NAgendas", "LegBio", "SubjHeadings"),
    )
    _download_bill_tracking(config, downloads_dir)
    _download_legdb_sessions(config, raw_dir / "legdb")
    votes_dir = raw_dir / "votes"
    vote_files = download_votes(config.votes_base_url, config.votes_readme_urls, votes_dir)
    feature_collection = fetch_all_features(config.gis_service_url)

    # Parse existing tables
    bills, bills_parse_issues = parse_mainbill(downloads_dir / "MAINBILL.TXT")
    legislators, legislators_parse_issues = parse_roster(downloads_dir / "ROSTER.TXT")
    active_legislators, former_legislators = split_legislators(legislators)
    bill_sponsors, bill_sponsors_parse_issues = parse_bill_sponsors(downloads_dir / "BILLSPON.TXT")
    committee_members, committee_members_parse_issues = parse_committee_members(downloads_dir / "COMEMBER.TXT")

    vote_records = []
    vote_records_parse_issues = []
    for vote_file in vote_files:
        v_recs, v_issues = parse_vote_file(vote_file)
        vote_records.extend(v_recs)
        vote_records_parse_issues.extend(v_issues)

    districts, districts_parse_issues = parse_districts(feature_collection)

    # Parse new tables
    bill_history, bill_history_parse_issues = parse_bill_history(downloads_dir / "BILLHIST.TXT")
    bill_subjects, bill_subjects_parse_issues = parse_bill_subjects(downloads_dir / "BILLSUBJ.TXT")
    bill_documents, bill_documents_parse_issues = parse_bill_documents(downloads_dir / "BILLWP.TXT")
    committees, committees_parse_issues = parse_committees(downloads_dir / "COMMITTEE.TXT")
    agendas, agendas_parse_issues = parse_agendas(downloads_dir / "AGENDAS.TXT")
    agenda_bills, agenda_bills_parse_issues = parse_agenda_bills(downloads_dir / "BAGENDA.TXT")
    agenda_nominees, agenda_nominees_parse_issues = parse_agenda_nominees(downloads_dir / "NAGENDA.TXT")
    legislator_bios, legislator_bios_parse_issues = parse_legislator_bios(downloads_dir / "LEGBIO.TXT")
    subject_headings, subject_headings_parse_issues = parse_subject_headings(downloads_dir / "SUBJHEADINGS.TXT")

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
    # Note: We should probably filter the new tables too (bill_history, etc.) but ignoring for now or relying on bill_key check in validation.

    processed_dir = snapshot_dir(config.data_dir, run_date)
    write_snapshot("bills", bills, processed_dir)
    write_snapshot("legislators", active_legislators, processed_dir)
    write_snapshot("former_legislators", former_legislators, processed_dir)
    write_snapshot("bill_sponsors", bill_sponsors, processed_dir)
    write_snapshot("committee_members", committee_members, processed_dir)
    write_snapshot("vote_records", vote_records, processed_dir)
    write_snapshot("districts", districts, processed_dir)

    # Snapshot new tables
    write_snapshot("bill_history", bill_history, processed_dir)
    write_snapshot("bill_subjects", bill_subjects, processed_dir)
    write_snapshot("bill_documents", bill_documents, processed_dir)
    write_snapshot("committees", committees, processed_dir)
    write_snapshot("agendas", agendas, processed_dir)
    write_snapshot("agenda_bills", agenda_bills, processed_dir)
    write_snapshot("agenda_nominees", agenda_nominees, processed_dir)
    write_snapshot("legislator_bios", legislator_bios, processed_dir)
    write_snapshot("subject_headings", subject_headings, processed_dir)

    if should_create_backup(config.data_dir, run_date, config.backup_interval_days):
        create_backup(processed_dir, backup_dir(config.data_dir, run_date))

    bills_result = validate_bills(bills)
    legislators_result = validate_legislators(legislators)
    bill_sponsors_result = validate_bill_sponsors(bill_sponsors, bills_result.valid_rows)
    committee_members_result = validate_committee_members(committee_members)
    vote_records_result = validate_vote_records(vote_records)
    districts_result = validate_districts(districts)

    bill_history_result = validate_bill_history(bill_history, bills_result.valid_rows)
    bill_subjects_result = validate_bill_subjects(bill_subjects, bills_result.valid_rows)
    bill_documents_result = validate_bill_documents(bill_documents, bills_result.valid_rows)
    committees_result = validate_committees(committees)
    agendas_result = validate_agendas(agendas)
    agenda_bills_result = validate_agenda_bills(agenda_bills, agendas_result.valid_rows, bills_result.valid_rows)
    agenda_nominees_result = validate_agenda_nominees(agenda_nominees, agendas_result.valid_rows)
    legislator_bios_result = validate_legislator_bios(legislator_bios, legislators_result.valid_rows)
    subject_headings_result = validate_subject_headings(subject_headings)

    validation_issues = (
        bills_result.issues
        + legislators_result.issues
        + bill_sponsors_result.issues
        + committee_members_result.issues
        + vote_records_result.issues
        + districts_result.issues
        + bill_history_result.issues
        + bill_subjects_result.issues
        + bill_documents_result.issues
        + committees_result.issues
        + agendas_result.issues
        + agenda_bills_result.issues
        + agenda_nominees_result.issues
        + legislator_bios_result.issues
        + subject_headings_result.issues
    )

    # Add parsing issues
    parsing_issues = (
        _to_validation_issues(bills_parse_issues)
        + _to_validation_issues(legislators_parse_issues)
        + _to_validation_issues(bill_sponsors_parse_issues)
        + _to_validation_issues(committee_members_parse_issues)
        + _to_validation_issues(vote_records_parse_issues)
        + _to_validation_issues(districts_parse_issues)
        + _to_validation_issues(bill_history_parse_issues)
        + _to_validation_issues(bill_subjects_parse_issues)
        + _to_validation_issues(bill_documents_parse_issues)
        + _to_validation_issues(committees_parse_issues)
        + _to_validation_issues(agendas_parse_issues)
        + _to_validation_issues(agenda_bills_parse_issues)
        + _to_validation_issues(agenda_nominees_parse_issues)
        + _to_validation_issues(legislator_bios_parse_issues)
        + _to_validation_issues(subject_headings_parse_issues)
    )

    all_issues = validation_issues + parsing_issues

    client = SupabaseClient(config.supabase_url, config.supabase_service_key)

    _upload_draft(client, "bills", bills, run_date)
    _upload_draft(client, "legislators", legislators, run_date)
    _upload_draft(client, "bill_sponsors", bill_sponsors, run_date)
    _upload_draft(client, "committee_members", committee_members, run_date)
    _upload_draft(client, "vote_records", vote_records, run_date)
    _upload_draft(client, "districts", districts, run_date)

    # Upload draft new tables
    _upload_draft(client, "bill_history", bill_history, run_date)
    _upload_draft(client, "bill_subjects", bill_subjects, run_date)
    _upload_draft(client, "bill_documents", bill_documents, run_date)
    _upload_draft(client, "committees", committees, run_date)
    _upload_draft(client, "agendas", agendas, run_date)
    _upload_draft(client, "agenda_bills", agenda_bills, run_date)
    _upload_draft(client, "agenda_nominees", agenda_nominees, run_date)
    _upload_draft(client, "legislator_bios", legislator_bios, run_date)
    _upload_draft(client, "subject_headings", subject_headings, run_date)


    if all_issues:
        issue_payloads = [issue.as_dict(run_date=run_date) for issue in all_issues]
        client.upsert("data_validation_issues", issue_payloads)

    _upload_changed(client, "bills", bills_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "legislators", legislators_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "bill_sponsors", bill_sponsors_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "committee_members", committee_members_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "vote_records", vote_records_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "districts", districts_result.valid_rows, config.data_dir, run_date)

    _upload_changed(client, "bill_history", bill_history_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "bill_subjects", bill_subjects_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "bill_documents", bill_documents_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "committees", committees_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "agendas", agendas_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "agenda_bills", agenda_bills_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "agenda_nominees", agenda_nominees_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "legislator_bios", legislator_bios_result.valid_rows, config.data_dir, run_date)
    _upload_changed(client, "subject_headings", subject_headings_result.valid_rows, config.data_dir, run_date)

    enforce_retention(config.data_dir, config.retention_days, config.backup_retention_count)

    return PipelineResult(
        bills=len(bills_result.valid_rows),
        legislators=len(legislators_result.valid_rows),
        bill_sponsors=len(bill_sponsors_result.valid_rows),
        committee_members=len(committee_members_result.valid_rows),
        vote_records=len(vote_records_result.valid_rows),
        districts=len(districts_result.valid_rows),
        validation_issues=len(all_issues),
        bill_history=len(bill_history_result.valid_rows),
        bill_subjects=len(bill_subjects_result.valid_rows),
        bill_documents=len(bill_documents_result.valid_rows),
        committees=len(committees_result.valid_rows),
        agendas=len(agendas_result.valid_rows),
        agenda_bills=len(agenda_bills_result.valid_rows),
        agenda_nominees=len(agenda_nominees_result.valid_rows),
        legislator_bios=len(legislator_bios_result.valid_rows),
        subject_headings=len(subject_headings_result.valid_rows),
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
