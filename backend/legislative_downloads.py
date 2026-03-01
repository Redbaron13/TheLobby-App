from __future__ import annotations

import json
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from backend.downloader import download_file


@dataclass(frozen=True)
class DownloadEntry:
    name: str
    entry_type: str
    date_modified: str
    extension: str
    download_type: str


class LegislativeDownloadError(RuntimeError):
    pass


def _fetch_json(url: str) -> list[dict]:
    with urllib.request.urlopen(url) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        raise LegislativeDownloadError("Unexpected API response format")
    return payload


def fetch_download_path(base_url: str, download_type: str) -> str:
    url = f"{base_url.rstrip('/')}/api/downloads/bills/{urllib.parse.quote(download_type)}"
    payload = _fetch_json(url)
    if not payload:
        raise LegislativeDownloadError("No download path returned from API")
    download_path = payload[0].get("Download_Path")
    if not download_path:
        raise LegislativeDownloadError("Download_Path missing in API response")
    return download_path


def list_download_entries(
    base_url: str,
    download_path: str,
    download_type: str,
    pub_base_url: str,
) -> list[DownloadEntry]:
    normalized_path = download_path if download_path.startswith("/") else f"/{download_path}"
    encoded_path = normalized_path.replace("/", "|")
    pub_host = urllib.parse.urlparse(pub_base_url).netloc or pub_base_url
    url = (
        f"{base_url.rstrip('/')}/api/downloads/{encoded_path}/"
        f"{pub_host}/{urllib.parse.quote(download_type)}"
    )
    payload = _fetch_json(url)
    entries: list[DownloadEntry] = []
    for entry in payload:
        entries.append(
            DownloadEntry(
                name=entry.get("FileName", ""),
                entry_type=entry.get("Type", ""),
                date_modified=entry.get("DateModified", ""),
                extension=entry.get("Ext", ""),
                download_type=entry.get("DownloadType", ""),
            )
        )
    return entries


def select_session_directory(entries: Iterable[DownloadEntry], session_year: int) -> str:
    target = f"{session_year}data"
    for entry in entries:
        if entry.entry_type.upper() == "D" and entry.name == target:
            return entry.name
    raise LegislativeDownloadError(f"Session directory {target} not found")


def select_text_zip(entries: Iterable[DownloadEntry], session_year: int) -> str:
    preferred = f"DB{session_year}_TEXT.zip"
    for entry in entries:
        if entry.entry_type.upper() == "F" and entry.name == preferred:
            return entry.name
    for entry in entries:
        if entry.entry_type.upper() == "F" and entry.extension.lower() == ".zip":
            return entry.name
    raise LegislativeDownloadError("No downloadable ZIP found for session")


def download_bill_tracking_session(
    *,
    base_url: str,
    pub_base_url: str,
    download_type: str,
    session_year: int,
    destination: Path,
    required_files: Iterable[str],
) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    download_path = fetch_download_path(base_url, download_type)
    root_entries = list_download_entries(base_url, download_path, download_type, pub_base_url)
    session_dir = select_session_directory(root_entries, session_year)
    session_path = f"{download_path.rstrip('/')}/{session_dir}"
    session_entries = list_download_entries(
        base_url, session_path, download_type, pub_base_url
    )
    zip_name = select_text_zip(session_entries, session_year)
    zip_url = (
        f"{pub_base_url.rstrip('/')}/{download_path.strip('/')}/"
        f"{session_dir}/{zip_name}"
    )
    zip_path = download_file(zip_url, destination)
    extracted_paths: list[Path] = []
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination)
        extracted_paths = [destination / name for name in archive.namelist()]

    missing = [name for name in required_files if not (destination / name).exists()]
    if missing:
        raise LegislativeDownloadError(
            f"Missing required files after extraction: {', '.join(missing)}"
        )
    return extracted_paths
