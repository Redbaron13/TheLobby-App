from __future__ import annotations

import json
import os
import sys

import psycopg2
from pathlib import Path

from backend.config import load_config
from backend.schema import load_schema_sql


class InitError(RuntimeError):
    pass


def _log(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


def initialize_schema(database_url: str) -> None:
    schema_sql = load_schema_sql()
    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)

            # If backend mode is 'local_postgres', initialize roles for PostgREST
            backend_mode = os.getenv("BACKEND_MODE", "cloud").lower()
            if backend_mode == "local_postgres":
                roles_path = Path(__file__).parent / "roles.sql"
                if roles_path.exists():
                    roles_sql = roles_path.read_text(encoding="utf-8")
                    cursor.execute(roles_sql)
                    _log({"action": "roles_initialized", "mode": backend_mode})

        connection.commit()


def main() -> int:
    config = load_config()
    database_url = config.supabase_db_url

    if not database_url:
        _log({"action": "error", "error": "SUPABASE_DB_URL or DATABASE_URL is required"})
        return 1
    try:
        initialize_schema(database_url)
        _log({"action": "schema_initialized"})
        return 0
    except Exception as exc:  # noqa: BLE001
        _log({"action": "error", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
