from shapely.geometry import Polygon

from backend.gis.geometry import geometries_equal, normalize_geometry


def test_projection_3857_to_4326() -> None:
    feature = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [0, 0],
                    [1000, 0],
                    [1000, 1000],
                    [0, 1000],
                    [0, 0],
                ]
            ],
        },
    }
    geom = normalize_geometry(feature, 3857)
    minx, miny, maxx, maxy = geom.bounds
    assert minx == 0
    assert miny == 0
    assert maxx > 0
    assert maxy > 0
    assert maxx < 0.02
    assert maxy < 0.02


def test_polygon_to_multipolygon() -> None:
    feature = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-74.0, 40.0],
                    [-74.0, 40.1],
                    [-73.9, 40.1],
                    [-73.9, 40.0],
                    [-74.0, 40.0],
                ]
            ],
        },
    }
    geom = normalize_geometry(feature, 4326)
    assert geom.geom_type == "MultiPolygon"
    assert len(geom.geoms) == 1


def test_idempotent_geometry_comparison() -> None:
    polygon = Polygon(
        [
            (-74.0, 40.0),
            (-74.0, 40.1),
            (-73.9, 40.1),
            (-73.9, 40.0),
            (-74.0, 40.0),
        ]
    )
    multipolygon = normalize_geometry(
        {"type": "Feature", "properties": {}, "geometry": polygon.__geo_interface__},
        4326,
    )
    assert geometries_equal(multipolygon, multipolygon)
