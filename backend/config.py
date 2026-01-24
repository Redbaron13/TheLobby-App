from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    base_url: str
    votes_base_url: str
    votes_readme_urls: tuple[str, ...]
    gis_service_url: str
    legdb_readme_url: str
    data_dir: Path
    supabase_url: str
    supabase_service_key: str
    retention_days: int
    backup_retention_count: int
    backup_interval_days: int
    files_to_download: tuple[str, ...]


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
    data_dir = Path(os.getenv("NJLEG_DATA_DIR", "backend/data")).resolve()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    retention_days = int(os.getenv("DATA_RETENTION_DAYS", "3"))
    backup_retention_count = int(os.getenv("BACKUP_RETENTION_COUNT", "2"))
    backup_interval_days = int(os.getenv("BACKUP_INTERVAL_DAYS", "14"))

    files_to_download = (
        "MAINBILL.TXT",
        "ROSTER.TXT",
        "BILLSPON.TXT",
        "COMEMBER.TXT",
    )

    return PipelineConfig(
        base_url=base_url,
        votes_base_url=votes_base_url,
        votes_readme_urls=tuple(url for url in votes_readme_urls if url),
        gis_service_url=gis_service_url,
        legdb_readme_url=legdb_readme_url,
        data_dir=data_dir,
        supabase_url=supabase_url,
        supabase_service_key=supabase_service_key,
        retention_days=retention_days,
        backup_retention_count=backup_retention_count,
        backup_interval_days=backup_interval_days,
        files_to_download=files_to_download,
    )


PRIMARY_KEYS = {
    "bills": "bill_key",
    "legislators": "roster_key",
    "bill_sponsors": "bill_sponsor_key",
    "committee_members": "committee_member_key",
    "vote_records": "vote_record_key",
    "districts": "district_key",
}
