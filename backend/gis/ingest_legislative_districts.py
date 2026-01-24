from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable

from backend.gis.setup_env import ensure_dependencies
from backend.gis.validation import (
    ValidationError,
    discover_fields,
    extract_int,
    infer_chamber,
    validate_feature,
)


@dataclass(frozen=True)
class IngestConfig:
    arcgis_rest_root: str
    arcgis_layer: str
    arcgis_page_size: int
    arcgis_target_srid: int
    gis_ingestion_enabled: bool
    supabase_url: str
    supabase_service_role_key: str
    database_url: str | None


REQUIRED_ENV = [
    "ARCGIS_REST_ROOT",
    "ARCGIS_LEGISLATIVE_DISTRICTS_LAYER",
    "ARCGIS_QUERY_PAGE_SIZE",
    "ARCGIS_TARGET_SRID",
    "GIS_INGESTION_ENABLED",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
]


class IngestError(RuntimeError):
    pass


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _validate_env() -> IngestConfig:
    missing = [key for key in REQUIRED_ENV if not os.getenv(key)]
    if missing:
        raise IngestError(f"Missing required environment variables: {', '.join(missing)}")
    target_srid = int(os.environ["ARCGIS_TARGET_SRID"])
    if target_srid != 4326:
        raise IngestError("ARCGIS_TARGET_SRID must be 4326")
    return IngestConfig(
        arcgis_rest_root=os.environ["ARCGIS_REST_ROOT"],
        arcgis_layer=os.environ["ARCGIS_LEGISLATIVE_DISTRICTS_LAYER"],
        arcgis_page_size=int(os.environ["ARCGIS_QUERY_PAGE_SIZE"]),
        arcgis_target_srid=target_srid,
        gis_ingestion_enabled=_parse_bool(os.environ["GIS_INGESTION_ENABLED"]),
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_service_role_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        database_url=os.getenv("DATABASE_URL"),
    )


def _import_runtime() -> tuple[
    Callable[[], dict[str, Any]],
    Callable[[], list[dict[str, Any]]],
    Callable[[dict[str, Any], int], Any],
    Callable[..., Any],
]:
    from backend.gis.arcgis_client import fetch_all_features, fetch_layer_metadata
    from backend.gis.geometry import normalize_geometry
    from backend.gis.repository import upsert_district

    return fetch_layer_metadata, fetch_all_features, normalize_geometry, upsert_district


def _log(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def main() -> int:
    try:
        ensure_dependencies()
        config = _validate_env()
        if not config.gis_ingestion_enabled:
            _log({"action": "skipped", "reason": "GIS_INGESTION_ENABLED=false"})
            return 0
        fetch_layer_metadata, fetch_all_features, normalize_geometry, upsert_district = (
            _import_runtime()
        )
        metadata = fetch_layer_metadata()
        source_srid = metadata["spatialReference"]["wkid"]
        fields = metadata.get("fields") or []
        field_names = discover_fields(fields)
        layer_name = metadata.get("name")
        features = fetch_all_features()
        counts = {"inserted": 0, "updated": 0, "unchanged": 0}
        for feature in features:
            validate_feature(feature, field_names.district_field, field_names.objectid_field)
            attributes = feature.get("properties") or {}
            district_number = extract_int(attributes, field_names.district_field)
            chamber = infer_chamber(attributes, layer_name, field_names.chamber_field)
            objectid = extract_int(attributes, field_names.objectid_field)
            geom = normalize_geometry(feature, source_srid)
            result = upsert_district(
                chamber=chamber,
                district_number=district_number,
                geom=geom,
                source_srid=source_srid,
                source_objectid=objectid,
            )
            counts[result.action] += 1
            _log(
                {
                    "district_number": district_number,
                    "chamber": chamber,
                    "action": result.action,
                }
            )
        summary = {
            "total_features": len(features),
            "inserted": counts["inserted"],
            "updated": counts["updated"],
            "unchanged": counts["unchanged"],
        }
        _log(summary)
        return 0
    except (IngestError, ValidationError) as exc:
        _log({"action": "error", "error": str(exc)})
        return 1
    except Exception as exc:  # noqa: BLE001
        _log({"action": "error", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
