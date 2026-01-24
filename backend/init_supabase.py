from __future__ import annotations

import json
import os
import sys

import psycopg2

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
        connection.commit()


def main() -> int:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        _log({"action": "error", "error": "DATABASE_URL is required"})
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
