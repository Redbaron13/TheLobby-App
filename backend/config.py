from __future__ import annotations

import os
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    base_url: str
    votes_base_url: str
    votes_readme_urls: tuple[str, ...]
    gis_service_url: str
    legdb_readme_url: str
    download_type: str
    bill_tracking_years: tuple[int, ...]
    data_dir: Path
    supabase_url: str
    supabase_service_key: str
    retention_days: int
    backup_retention_count: int
    backup_interval_days: int
    files_to_download: tuple[str, ...]
    session_lookback_count: int
    session_length_years: int
    legdb_base_url: str
    legdb_years: tuple[int, ...]


def load_config() -> PipelineConfig:
    base_url = os.getenv("NJLEG_DOWNLOAD_BASE_URL", "https://www.njleg.state.nj.us/downloads")
    votes_base_url = os.getenv("NJLEG_VOTES_BASE_URL", "https://pub.njleg.state.nj.us/votes")
    votes_readme_urls = (
        os.getenv("NJLEG_VOTES_README_URL", "https://pub.njleg.state.nj.us/votes/_Readme.txt"),
        os.getenv("NJLEG_VOTES_COMM_README_URL", "https://pub.njleg.state.nj.us/votes/_CommRdme.txt"),
    )
    gis_service_url = os.getenv(
        "NJLEG_GIS_SERVICE_URL",
        "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/"
        "Legislative_Districts_of_NJ_Hosted_3424/FeatureServer/0",
    )
    legdb_readme_url = os.getenv(
        "NJLEG_LEGDB_README_URL",
        "https://pub.njleg.state.nj.us/leg-databases/2024data/Readme.txt",
    )
    legdb_base_url = os.getenv("NJLEG_LEGDB_BASE_URL", "https://pub.njleg.state.nj.us/leg-databases")
    download_type = os.getenv("NJLEG_DOWNLOAD_TYPE", "Bill_Tracking")
    bill_tracking_years = _parse_years(os.getenv("NJLEG_BILL_TRACKING_YEARS", "2024"))
    data_dir = Path(os.getenv("NJLEG_DATA_DIR", "backend/data")).resolve()
    supabase_url = os.getenv("SUPABASE_URL", "https://zgtevahaudnjpocptzgj.supabase.co").strip()
    supabase_service_key = _resolve_supabase_key()

    retention_days = int(os.getenv("DATA_RETENTION_DAYS", "3"))
    backup_retention_count = int(os.getenv("BACKUP_RETENTION_COUNT", "2"))
    backup_interval_days = int(os.getenv("BACKUP_INTERVAL_DAYS", "14"))
    session_lookback_count = int(os.getenv("SESSION_LOOKBACK_COUNT", "3"))
    session_length_years = int(os.getenv("SESSION_LENGTH_YEARS", "2"))

    files_to_download = (
        "MAINBILL.TXT",
        "ROSTER.TXT",
        "BILLSPON.TXT",
        "COMEMBER.TXT",
    )

    legdb_years = _parse_years(os.getenv("NJLEG_LEGDB_YEARS", "2024"))

    return PipelineConfig(
        base_url=base_url,
        votes_base_url=votes_base_url,
        votes_readme_urls=tuple(url for url in votes_readme_urls if url),
        gis_service_url=gis_service_url,
        legdb_readme_url=legdb_readme_url,
        download_type=download_type,
        bill_tracking_years=bill_tracking_years,
        data_dir=data_dir,
        supabase_url=supabase_url,
        supabase_service_key=supabase_service_key,
        retention_days=retention_days,
        backup_retention_count=backup_retention_count,
        backup_interval_days=backup_interval_days,
        files_to_download=files_to_download,
        session_lookback_count=session_lookback_count,
        session_length_years=session_length_years,
        legdb_base_url=legdb_base_url,
        legdb_years=legdb_years,
    )


def _parse_years(value: str) -> tuple[int, ...]:
    years: list[int] = []
    for chunk in value.split(","):
        cleaned = chunk.strip()
        if not cleaned:
            continue
        years.append(int(cleaned))
    return tuple(years)


def _resolve_supabase_key() -> str:
    for key in ("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"):
        value = os.getenv(key)
        if value:
            return value
    return ""


PRIMARY_KEYS = {
    "bills": "bill_key",
    "legislators": "roster_key",
    "former_legislators": "roster_key",
    "bill_sponsors": "bill_sponsor_key",
    "committee_members": "committee_member_key",
    "vote_records": "vote_record_key",
    "districts": "district_key",
}

DRAFT_TABLE_PREFIX = "draft_"


def draft_table_name(table: str) -> str:
    return f"{DRAFT_TABLE_PREFIX}{table}"
