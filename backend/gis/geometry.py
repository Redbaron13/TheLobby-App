from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import transform
from shapely.validation import explain_validity
from pyproj import Transformer


class GeometryError(ValueError):
    pass


def geometries_equal(left: MultiPolygon, right: MultiPolygon, tolerance: float = 0.000001) -> bool:
    return left.equals_exact(right, tolerance)


def _ensure_multipolygon(geom: Polygon | MultiPolygon) -> MultiPolygon:
    if isinstance(geom, MultiPolygon):
        return geom
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    raise GeometryError(f"Unsupported geometry type: {geom.geom_type}")


def normalize_geometry(feature: dict, source_srid: int) -> MultiPolygon:
    """
    - Accepts GeoJSON feature
    - Converts Polygon → MultiPolygon if needed
    - Reprojects from source_srid to 4326
    - Returns shapely.geometry.MultiPolygon
    """
    if "geometry" not in feature or feature["geometry"] is None:
        raise GeometryError("Feature has no geometry")
    raw_geom = shape(feature["geometry"])
    multipolygon = _ensure_multipolygon(raw_geom)
    transformer = Transformer.from_crs(source_srid, 4326, always_xy=True)
    projected = transform(transformer.transform, multipolygon)
    if not projected.is_valid:
        fixed = projected.buffer(0)
        if not fixed.is_valid:
            raise GeometryError(
                f"Invalid geometry after fix: {explain_validity(fixed)}"
            )
        projected = fixed
    return _ensure_multipolygon(projected)
