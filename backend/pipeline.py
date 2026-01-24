from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from backend.config import PRIMARY_KEYS, PipelineConfig
from backend.downloader import download_files, download_text_file
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


@dataclass
class PipelineResult:
    bills: int
    legislators: int
    bill_sponsors: int
    committee_members: int
    vote_records: int
    districts: int


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
        raise RuntimeError("Supabase credentials are required to run the pipeline.")

    run_date = date_str or datetime.utcnow().strftime("%Y-%m-%d")
    raw_dir = config.data_dir / "raw" / run_date
    download_text_file(config.legdb_readme_url, raw_dir)
    votes_dir = config.data_dir / "raw" / run_date / "votes"
    vote_files = download_votes(config.votes_base_url, config.votes_readme_urls, votes_dir)
    feature_collection = fetch_all_features(config.gis_service_url)

    bills: list[dict] = []
    legislators: list[dict] = []
    bill_sponsors: list[dict] = []
    committee_members: list[dict] = []

    for session_year in config.sessions:
        session_dir = raw_dir / "sessions" / str(session_year)
        session_base = f"https://pub.njleg.state.nj.us/leg-databases/{session_year}data"
        download_files(session_base, config.files_to_download, session_dir)
        bills.extend(parse_mainbill(session_dir / "MAINBILL.TXT", session_year=session_year))
        legislators.extend(parse_roster(session_dir / "ROSTER.TXT", session_year=session_year))
        bill_sponsors.extend(parse_bill_sponsors(session_dir / "BILLSPON.TXT", session_year=session_year))
        committee_members.extend(parse_committee_members(session_dir / "COMEMBER.TXT", session_year=session_year))
    vote_records = []
    for vote_file in vote_files:
        vote_records.extend(parse_vote_file(vote_file))
    districts = parse_districts(feature_collection)

    processed_dir = snapshot_dir(config.data_dir, run_date)
    write_snapshot("bills", bills, processed_dir)
    write_snapshot("legislators", legislators, processed_dir)
    write_snapshot("bill_sponsors", bill_sponsors, processed_dir)
    write_snapshot("committee_members", committee_members, processed_dir)
    write_snapshot("vote_records", vote_records, processed_dir)
    write_snapshot("districts", districts, processed_dir)

    if should_create_backup(config.data_dir, run_date, config.backup_interval_days):
        create_backup(processed_dir, backup_dir(config.data_dir, run_date))

    client = SupabaseClient(config.supabase_url, config.supabase_service_key)

    _upload_changed(client, "bills", bills, config.data_dir, run_date)
    _upload_changed(client, "legislators", legislators, config.data_dir, run_date)
    _upload_changed(client, "bill_sponsors", bill_sponsors, config.data_dir, run_date)
    _upload_changed(client, "committee_members", committee_members, config.data_dir, run_date)
    _upload_changed(client, "vote_records", vote_records, config.data_dir, run_date)
    _upload_changed(client, "districts", districts, config.data_dir, run_date)

    enforce_retention(config.data_dir, config.retention_days, config.backup_retention_count)

    return PipelineResult(
        bills=len(bills),
        legislators=len(legislators),
        bill_sponsors=len(bill_sponsors),
        committee_members=len(committee_members),
        vote_records=len(vote_records),
        districts=len(districts),
    )


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
