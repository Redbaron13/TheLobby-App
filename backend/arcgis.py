from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LobbyTrackBot/1.0; +https://www.njleg.state.nj.us/)",
    "Accept": "application/json",
}


def fetch_service_metadata(service_url: str) -> dict[str, Any]:
    url = f"{service_url}?f=pjson"
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_all_features(service_url: str) -> dict[str, Any]:
    metadata = fetch_service_metadata(service_url)
    max_records = int(metadata.get("maxRecordCount", 2000))
    features: list[dict[str, Any]] = []
    offset = 0

    while True:
        query_params = {
            "where": "1=1",
            "outFields": "*",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": max_records,
        }
        query_url = f"{service_url}/query?{urllib.parse.urlencode(query_params)}"
        request = urllib.request.Request(query_url, headers=DEFAULT_HEADERS)
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
        batch_features = payload.get("features", [])
        features.extend(batch_features)

        if len(batch_features) < max_records:
            break
        offset += max_records

    return {
        "type": "FeatureCollection",
        "features": features,
    }
