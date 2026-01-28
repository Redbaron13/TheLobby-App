from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from backend.config import load_config
from backend.init_arcgis_pipeline import main as run_arcgis_pipeline
from backend.init_legislative_pipeline import main as run_legislative_pipeline
from backend.gis.setup_env import ensure_dependencies as ensure_gis_dependencies


LEGISLATIVE_ENV_KEYS = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
]

GIS_ENV_KEYS = [
    "ARCGIS_REST_ROOT",
    "ARCGIS_LEGISLATIVE_DISTRICTS_LAYER",
    "ARCGIS_QUERY_PAGE_SIZE",
    "ARCGIS_TARGET_SRID",
    "GIS_INGESTION_ENABLED",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
]


def _log(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


def _missing_env(keys: list[str]) -> list[str]:
    return [key for key in keys if not os.getenv(key)]


def _load_initialize_schema():
    from backend.init_supabase import initialize_schema

    return initialize_schema


def _init_legislative(run_schema: bool) -> int:
    config = load_config()
    missing = _missing_env(LEGISLATIVE_ENV_KEYS)
    if missing:
        _log({"action": "legislative_init_failed", "missing_env": missing})
        return 1
    if run_schema:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            _log({"action": "legislative_init_failed", "error": "DATABASE_URL is required for schema init"})
            return 1
        initialize_schema = _load_initialize_schema()
        initialize_schema(database_url)
    data_dir = Path(config.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    _log(
        {
            "action": "legislative_initialized",
            "data_dir": str(data_dir),
            "bill_tracking_years": list(config.bill_tracking_years),
        }
    )
    return 0


def _init_gis(run_schema: bool) -> int:
    ensure_gis_dependencies()
    missing = _missing_env(GIS_ENV_KEYS)
    if missing:
        _log({"action": "gis_init_failed", "missing_env": missing})
        return 1
    if run_schema:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            _log({"action": "gis_init_failed", "error": "DATABASE_URL is required for schema init"})
            return 1
        initialize_schema = _load_initialize_schema()
        initialize_schema(database_url)
    _log({"action": "gis_initialized"})
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize or run ingestion pipelines.")
    parser.add_argument(
        "--pipeline",
        choices=("legislative", "gis", "both"),
        default="both",
        help="Which pipeline to target.",
    )
    parser.add_argument(
        "--action",
        choices=("init", "run"),
        default="init",
        help="Initialize or run the pipeline.",
    )
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip schema initialization when running init.",
    )
    args = parser.parse_args(argv)

    if args.action == "init":
        run_schema = not args.skip_schema
        if args.pipeline in ("legislative", "both"):
            result = _init_legislative(run_schema)
            if result != 0:
                return result
        if args.pipeline in ("gis", "both"):
            result = _init_gis(run_schema)
            if result != 0:
                return result
        return 0

    if args.pipeline == "legislative":
        return run_legislative_pipeline()
    if args.pipeline == "gis":
        return run_arcgis_pipeline()

    result = run_legislative_pipeline()
    if result != 0:
        return result
    return run_arcgis_pipeline()


if __name__ == "__main__":
    sys.exit(main())
