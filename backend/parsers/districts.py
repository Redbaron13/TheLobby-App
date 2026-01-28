from __future__ import annotations

import json
from typing import Any


def parse_districts(feature_collection: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """
    Parses GeoJSON features into district records.
    Returns (valid_records, issues).
    """
    records: list[dict] = []
    issues: list[dict] = []

    for feature in feature_collection.get("features", []):
        properties = feature.get("properties", {})
        district_number = _extract_district_number(properties)
        name = _extract_name(properties)

        district_key = None
        if district_number is not None:
             district_key = str(district_number)
        else:
             fallback = _fallback_key(properties)
             if fallback == "unknown":
                 issues.append({
                     "table": "districts",
                     "record_key": None,
                     "issue": "missing_district_identifier",
                     "details": f"Could not determine district number or fallback ID. Properties: {properties.keys()}",
                     "raw_data": str(properties)
                 })
                 continue
             district_key = fallback

        geometry_json = json.dumps(feature.get("geometry"), sort_keys=True)
        records.append(
            {
                "district_key": district_key,
                "district_number": district_number,
                "name": name,
                "properties": properties,
                "geometry_json": geometry_json,
            }
        )
    return records, issues


def _extract_district_number(properties: dict[str, Any]) -> int | None:
    for key in properties.keys():
        if "DIST" in key.upper() and isinstance(properties[key], (int, float, str)):
            try:
                return int(properties[key])
            except (TypeError, ValueError):
                continue
    return None


def _extract_name(properties: dict[str, Any]) -> str | None:
    for key in ("NAME", "DistrictName", "DISTRICTNAME"):
        value = properties.get(key)
        if value:
            return str(value)
    return None


def _fallback_key(properties: dict[str, Any]) -> str:
    return str(properties.get("OBJECTID") or properties.get("FID") or "unknown")
