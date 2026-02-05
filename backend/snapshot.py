from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from backend.config import PRIMARY_KEYS


def snapshot_dir(base_dir: Path, date_str: str) -> Path:
    return base_dir / "processed" / date_str


def backup_dir(base_dir: Path, date_str: str) -> Path:
    return base_dir / "backups" / date_str


def compute_row_hash(row: dict) -> str:
    """Computes a SHA-512 hash for a dictionary row."""
    encoded = json.dumps(row, sort_keys=True).encode("utf-8")
    return hashlib.sha512(encoded).hexdigest()


def write_snapshot(table: str, rows: Iterable[dict], target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"{table}.jsonl"

    pk_field = PRIMARY_KEYS.get(table)
    hashes: dict[str, str] = {}

    with output_path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, sort_keys=True))
            file.write("\n")

            if pk_field:
                val = row.get(pk_field)
                if val is not None:
                    hashes[str(val)] = compute_row_hash(row)

    if hashes:
        hash_path = target_dir / f"{table}.hashes.json"
        with hash_path.open("w", encoding="utf-8") as hf:
            json.dump(hashes, hf)

    return output_path


def load_latest_snapshot(base_dir: Path, table: str, exclude_date: str | None = None) -> list[dict]:
    processed_root = base_dir / "processed"
    if not processed_root.exists():
        return []

    date_dirs = sorted([p for p in processed_root.iterdir() if p.is_dir()])
    for date_dir in reversed(date_dirs):
        if exclude_date and date_dir.name == exclude_date:
            continue
        snapshot_path = date_dir / f"{table}.jsonl"
        if snapshot_path.exists():
            return _read_snapshot(snapshot_path)
    return []


def load_latest_hashes(base_dir: Path, table: str, exclude_date: str | None = None) -> dict[str, str] | None:
    """
    Loads the latest hash map for a table.
    Returns None if no hash map is found, allowing fallback to full snapshot load.
    """
    processed_root = base_dir / "processed"
    if not processed_root.exists():
        return None

    date_dirs = sorted([p for p in processed_root.iterdir() if p.is_dir()])
    for date_dir in reversed(date_dirs):
        if exclude_date and date_dir.name == exclude_date:
            continue
        hash_path = date_dir / f"{table}.hashes.json"
        # If hash file doesn't exist but snapshot does, we found the latest version
        # but it's legacy (unhashed). Return None to trigger fallback.
        snapshot_path = date_dir / f"{table}.jsonl"

        if hash_path.exists():
            with hash_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        elif snapshot_path.exists():
            # Found a snapshot but no hash file -> Legacy snapshot
            return None

    return None


def _read_snapshot(snapshot_path: Path) -> list[dict]:
    rows: list[dict] = []
    with snapshot_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def should_create_backup(base_dir: Path, date_str: str, interval_days: int) -> bool:
    backups_root = base_dir / "backups"
    backups_root.mkdir(parents=True, exist_ok=True)
    existing = sorted([p for p in backups_root.iterdir() if p.is_dir()])
    if not existing:
        return True

    latest_backup = existing[-1].name
    try:
        latest_dt = datetime.strptime(latest_backup, "%Y-%m-%d")
    except ValueError:
        return True

    current_dt = datetime.strptime(date_str, "%Y-%m-%d")
    return current_dt - latest_dt >= timedelta(days=interval_days)


def create_backup(processed_dir: Path, backup_target: Path) -> None:
    if backup_target.exists():
        shutil.rmtree(backup_target)
    shutil.copytree(processed_dir, backup_target)


def enforce_retention(base_dir: Path, retention_days: int, backup_retention_count: int) -> None:
    processed_root = base_dir / "processed"
    backups_root = base_dir / "backups"

    if processed_root.exists():
        processed_dirs = sorted([p for p in processed_root.iterdir() if p.is_dir()])
        if len(processed_dirs) > retention_days:
            for path in processed_dirs[: max(0, len(processed_dirs) - retention_days)]:
                shutil.rmtree(path)

    if backups_root.exists():
        backup_dirs = sorted([p for p in backups_root.iterdir() if p.is_dir()])
        if len(backup_dirs) > backup_retention_count:
            for path in backup_dirs[: max(0, len(backup_dirs) - backup_retention_count)]:
                shutil.rmtree(path)
