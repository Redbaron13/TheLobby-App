from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldNames:
    district_field: str
    objectid_field: str
    chamber_field: str | None


class ValidationError(RuntimeError):
    pass


CHAMBER_FIELD_CANDIDATES = {"CHAMBER", "HOUSE", "LEGISLATIVE_BODY", "BODY", "CHAMB"}
DISTRICT_FIELD_CANDIDATES = {"DISTRICT", "DISTRICT_NUMBER", "DIST_NO", "DIST_NUM"}
OBJECTID_FIELD_CANDIDATES = {"OBJECTID", "OBJECT_ID"}


def find_field(fields: list[dict[str, Any]], candidates: set[str]) -> str:
    for field in fields:
        name = field.get("name")
        if name and name.upper() in candidates:
            return name
    for field in fields:
        name = field.get("name")
        if name and any(candidate in name.upper() for candidate in candidates):
            return name
    raise ValidationError(f"Unable to locate field from candidates: {sorted(candidates)}")


def find_optional_field(fields: list[dict[str, Any]], candidates: set[str]) -> str | None:
    for field in fields:
        name = field.get("name")
        if name and name.upper() in candidates:
            return name
    for field in fields:
        name = field.get("name")
        if name and any(candidate in name.upper() for candidate in candidates):
            return name
    return None


def discover_fields(fields: list[dict[str, Any]]) -> FieldNames:
    district_field = find_field(fields, DISTRICT_FIELD_CANDIDATES)
    objectid_field = find_field(fields, OBJECTID_FIELD_CANDIDATES)
    chamber_field = find_optional_field(fields, CHAMBER_FIELD_CANDIDATES)
    return FieldNames(
        district_field=district_field,
        objectid_field=objectid_field,
        chamber_field=chamber_field,
    )


def extract_int(attributes: dict[str, Any], field_name: str) -> int:
    if field_name not in attributes:
        raise ValidationError(f"Missing field {field_name} in feature properties")
    try:
        return int(attributes[field_name])
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Invalid value for {field_name}: {attributes[field_name]}") from exc


def infer_chamber(
    attributes: dict[str, Any],
    layer_name: str | None,
    chamber_field: str | None,
) -> str:
    if chamber_field and chamber_field in attributes:
        value = attributes.get(chamber_field)
        if value is not None:
            value_upper = str(value).strip().upper()
            if value_upper.startswith("A") or "ASSEMB" in value_upper:
                return "A"
            if value_upper.startswith("S") or "SEN" in value_upper:
                return "S"
    for key, value in attributes.items():
        if value is None:
            continue
        key_upper = key.upper()
        if key_upper in CHAMBER_FIELD_CANDIDATES:
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
    raise ValidationError("Unable to infer chamber from feature attributes")


def validate_feature(
    feature: dict[str, Any],
    district_field: str,
    objectid_field: str,
) -> None:
    if "geometry" not in feature or feature["geometry"] is None:
        raise ValidationError("Feature geometry is missing")
    attributes = feature.get("properties") or {}
    district_number = extract_int(attributes, district_field)
    objectid = extract_int(attributes, objectid_field)
    if district_number <= 0:
        raise ValidationError("District number must be positive")
    if district_number > 40:
        raise ValidationError("District number exceeds expected NJ range")
    if objectid <= 0:
        raise ValidationError("ObjectID must be positive")
