import os
from typing import Any
from urllib.parse import urljoin

import requests


class ArcGISClientError(RuntimeError):
    pass


def _layer_url() -> str:
    root = os.environ["ARCGIS_REST_ROOT"].rstrip("/") + "/"
    layer = os.environ["ARCGIS_LEGISLATIVE_DISTRICTS_LAYER"].lstrip("/")
    return urljoin(root, layer)


def fetch_layer_metadata() -> dict[str, Any]:
    """
    GET {layer_url}?f=pjson
    Validate:
      - geometryType is polygon/multipolygon
      - spatialReference.wkid exists
    """
    layer_url = _layer_url()
    response = requests.get(f"{layer_url}?f=pjson", timeout=30)
    if response.status_code != 200:
        raise ArcGISClientError(
            f"Layer metadata request failed with status {response.status_code}"
        )
    payload = response.json()
    geometry_type = payload.get("geometryType")
    if geometry_type not in {"esriGeometryPolygon", "esriGeometryMultiPolygon"}:
        raise ArcGISClientError(
            f"Unexpected geometry type {geometry_type} in layer metadata"
        )
    spatial_ref = payload.get("spatialReference") or {}
    wkid = spatial_ref.get("wkid")
    if wkid is None:
        raise ArcGISClientError("Layer metadata missing spatialReference.wkid")
    return payload


def _query_params(result_offset: int, result_record_count: int) -> dict[str, Any]:
    return {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "resultOffset": result_offset,
        "resultRecordCount": result_record_count,
    }


def fetch_all_features() -> list[dict[str, Any]]:
    """
    Query FeatureServer with pagination.
    Must:
      - use returnGeometry=true
      - request f=geojson
      - respect ARCGIS_QUERY_PAGE_SIZE
    Returns list of GeoJSON features.
    """
    layer_url = _layer_url()
    page_size = int(os.environ["ARCGIS_QUERY_PAGE_SIZE"])
    all_features: list[dict[str, Any]] = []
    offset = 0
    while True:
        response = requests.get(
            f"{layer_url}/query",
            params=_query_params(offset, page_size),
            timeout=60,
        )
        if response.status_code != 200:
            raise ArcGISClientError(
                f"Feature query failed with status {response.status_code}"
            )
        payload = response.json()
        features = payload.get("features") or []
        all_features.extend(features)
        if len(features) < page_size:
            break
        offset += page_size
    if not all_features:
        raise ArcGISClientError("No features returned from ArcGIS layer query")
    return all_features
