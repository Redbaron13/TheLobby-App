from __future__ import annotations

from pathlib import Path


def load_schema_sql() -> str:
    schema_path = Path(__file__).with_name("schema.sql")
    return schema_path.read_text(encoding="utf-8")

def load_migrations() -> list[str]:
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        return []

    # Sort files to ensure migrations run in order (e.g., 01_..., 02_...)
    migration_files = sorted(migrations_dir.glob("*.sql"))
    return [f.read_text(encoding="utf-8") for f in migration_files]
