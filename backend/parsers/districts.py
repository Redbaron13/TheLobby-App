from __future__ import annotations

import json
from typing import Any


def parse_districts(feature_collection: dict[str, Any]) -> list[dict]:
    records: list[dict] = []
    for feature in feature_collection.get("features", []):
        properties = feature.get("properties", {})
        district_number = _extract_district_number(properties)
        name = _extract_name(properties)
        district_key = str(district_number) if district_number is not None else _fallback_key(properties)
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
    return records


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
