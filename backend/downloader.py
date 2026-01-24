from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from typing import Iterable

import urllib.parse


def fetch_index_html(base_url: str) -> str:
    with urllib.request.urlopen(base_url) as response:
        return response.read().decode("utf-8", errors="ignore")


def resolve_download_url(base_url: str, index_html: str, filename: str) -> str:
    pattern = re.compile(r'href=["\']([^"\']*%s)["\']' % re.escape(filename), re.IGNORECASE)
    match = pattern.search(index_html)
    if match:
        href = match.group(1)
        if href.startswith("http"):
            return href
        return f"{base_url.rstrip('/')}/{href.lstrip('/')}"

    return f"{base_url.rstrip('/')}/{filename}"


def download_files(base_url: str, filenames: Iterable[str], destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    index_html = fetch_index_html(base_url)
    downloaded_paths: list[Path] = []

    for filename in filenames:
        url = resolve_download_url(base_url, index_html, filename)
        target_path = destination / filename
        with urllib.request.urlopen(url) as response, target_path.open("wb") as f:
            f.write(response.read())
        downloaded_paths.append(target_path)

    return downloaded_paths


def download_text_file(url: str, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    filename = Path(urllib.parse.urlparse(url).path).name
    target_path = destination / filename
    with urllib.request.urlopen(url) as response, target_path.open("wb") as f:
        f.write(response.read())
    return target_path


def download_binary_file(url: str, destination: Path) -> Path:
    return download_text_file(url, destination)
