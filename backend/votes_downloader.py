from __future__ import annotations

import re
import urllib.parse
from pathlib import Path
from typing import Iterable

from backend.downloader import download_text_file


def extract_vote_filenames(readme_text: str) -> list[str]:
    pattern = re.compile(r"([A-Za-z0-9_\\-]+\\.(?:TXT|CSV))", re.IGNORECASE)
    return sorted(set(match.group(1) for match in pattern.finditer(readme_text)))


def download_votes(base_url: str, readme_urls: Iterable[str], destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for readme_url in readme_urls:
        readme_path = download_text_file(readme_url, destination)
        readme_text = readme_path.read_text(encoding="latin1", errors="ignore")
        filenames = extract_vote_filenames(readme_text)
        for filename in filenames:
            file_url = f"{base_url.rstrip('/')}/{urllib.parse.quote(filename)}"
            files.append(download_text_file(file_url, destination))
    return files
