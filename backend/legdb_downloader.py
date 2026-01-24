from __future__ import annotations

import urllib.error
from pathlib import Path
from typing import Iterable

from backend.downloader import download_files, download_text_file


def download_legdb_session(
    base_url: str,
    year: int,
    filenames: Iterable[str],
    destination: Path,
) -> list[Path]:
    session_url = f"{base_url.rstrip('/')}/{year}data"
    destination.mkdir(parents=True, exist_ok=True)
    downloaded = download_files(session_url, filenames, destination)
    _download_optional_readme(session_url, destination)
    return downloaded


def _download_optional_readme(session_url: str, destination: Path) -> None:
    readme_url = f"{session_url}/Readme.txt"
    try:
        download_text_file(readme_url, destination)
    except urllib.error.HTTPError:
        return
