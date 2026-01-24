from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any

from backend.gis.arcgis_client import fetch_all_features, fetch_layer_metadata
from backend.gis.geometry import normalize_geometry
from backend.gis.repository import upsert_district


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


def _find_field(fields: list[dict[str, Any]], candidates: set[str]) -> str:
    for field in fields:
        name = field.get("name")
        if name and name.upper() in candidates:
            return name
    for field in fields:
        name = field.get("name")
        if name and any(candidate in name.upper() for candidate in candidates):
            return name
    raise IngestError(f"Unable to locate field from candidates: {sorted(candidates)}")


def _infer_chamber(attributes: dict[str, Any], layer_name: str | None) -> str:
    for key, value in attributes.items():
        if value is None:
            continue
        key_upper = key.upper()
        if key_upper in {"CHAMBER", "HOUSE", "LEGISLATIVE_BODY", "BODY"}:
            value_upper = str(value).strip().upper()
            if value_upper.startswith("A") or "ASSEMB" in value_upper:
                return "A"
            if value_upper.startswith("S") or "SEN" in value_upper:
                return "S"
    if layer_name:
        layer_upper = layer_name.upper()
        if "ASSEMB" in layer_upper:
            return "A"
        if "SENATE" in layer_upper:
            return "S"
    raise IngestError("Unable to infer chamber from feature attributes")


def _extract_int(attributes: dict[str, Any], field_name: str) -> int:
    if field_name not in attributes:
        raise IngestError(f"Missing field {field_name} in feature properties")
    try:
        return int(attributes[field_name])
    except (TypeError, ValueError) as exc:
        raise IngestError(f"Invalid value for {field_name}: {attributes[field_name]}") from exc


def _log(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def main() -> int:
    try:
        config = _validate_env()
        if not config.gis_ingestion_enabled:
            _log({"action": "skipped", "reason": "GIS_INGESTION_ENABLED=false"})
            return 0
        metadata = fetch_layer_metadata()
        source_srid = metadata["spatialReference"]["wkid"]
        fields = metadata.get("fields") or []
        district_field = _find_field(fields, {"DISTRICT", "DISTRICT_NUMBER", "DIST_NO"})
        objectid_field = _find_field(fields, {"OBJECTID", "OBJECT_ID"})
        layer_name = metadata.get("name")
        features = fetch_all_features()
        counts = {"inserted": 0, "updated": 0, "unchanged": 0}
        for feature in features:
            attributes = feature.get("properties") or {}
            district_number = _extract_int(attributes, district_field)
            chamber = _infer_chamber(attributes, layer_name)
            objectid = _extract_int(attributes, objectid_field)
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
    except Exception as exc:  # noqa: BLE001
        _log({"action": "error", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
