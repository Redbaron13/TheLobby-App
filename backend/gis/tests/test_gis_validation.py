import pytest

from backend.gis.validation import (
    ValidationError,
    discover_fields,
    extract_int,
    infer_chamber,
    validate_feature,
)


def test_discover_fields() -> None:
    fields = [
        {"name": "OBJECTID"},
        {"name": "DISTRICT"},
        {"name": "CHAMBER"},
    ]
    field_names = discover_fields(fields)
    assert field_names.district_field == "DISTRICT"
    assert field_names.objectid_field == "OBJECTID"
    assert field_names.chamber_field == "CHAMBER"


def test_extract_int_invalid_value() -> None:
    with pytest.raises(ValidationError):
        extract_int({"DISTRICT": "N/A"}, "DISTRICT")


def test_infer_chamber_from_field() -> None:
    attributes = {"CHAMBER": "Senate"}
    assert infer_chamber(attributes, None, "CHAMBER") == "S"


def test_validate_feature_bounds() -> None:
    feature = {
        "type": "Feature",
        "properties": {"DISTRICT": 41, "OBJECTID": 10},
        "geometry": {"type": "Polygon", "coordinates": []},
    }
    with pytest.raises(ValidationError):
        validate_feature(feature, "DISTRICT", "OBJECTID")
