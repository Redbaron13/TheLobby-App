from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, timedelta
import psycopg2
from shapely.geometry import MultiPolygon, shape, mapping
from supabase import Client, create_client

from backend.gis.geometry import geometries_equal

@dataclass
class UpsertResult:
    action: str


class RepositoryError(RuntimeError):
    pass


def _get_psycopg2_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None
    connection = psycopg2.connect(database_url)
    connection.autocommit = True
    return connection


def _get_supabase_client() -> Client:
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(supabase_url, supabase_key)


def _psycopg2_upsert(
    chamber: str,
    district_number: int,
    geom: MultiPolygon,
    source_srid: int,
    source_objectid: int,
) -> UpsertResult:
    connection = _get_psycopg2_connection()
    if connection is None:
        raise RepositoryError("DATABASE_URL is required for direct PostGIS access")
    wkt = geom.wkt
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id,
                   ST_Equals(geom, ST_GeomFromText(%s, 4326)) AS equals_geom
              FROM legislative_districts
             WHERE chamber = %s
               AND district_number = %s
               AND valid_to IS NULL
             LIMIT 1
            """,
            (wkt, chamber, district_number),
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute(
                """
                INSERT INTO legislative_districts
                    (chamber, district_number, geom, source_sr, source_objectid)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326), %s, %s)
                """,
                (chamber, district_number, wkt, source_srid, source_objectid),
            )
            return UpsertResult(action="inserted")
        existing_id, equals_geom = row
        if equals_geom:
            return UpsertResult(action="unchanged")
        cursor.execute(
            """
            UPDATE legislative_districts
               SET valid_to = current_date - 1
             WHERE id = %s
            """,
            (existing_id,),
        )
        cursor.execute(
            """
            INSERT INTO legislative_districts
                (chamber, district_number, geom, source_sr, source_objectid, valid_from)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326), %s, %s, current_date)
            """,
            (chamber, district_number, wkt, source_srid, source_objectid),
        )
    return UpsertResult(action="updated")


def _supabase_upsert(
    chamber: str,
    district_number: int,
    geom: MultiPolygon,
    source_srid: int,
    source_objectid: int,
) -> UpsertResult:
    client = _get_supabase_client()
    existing_response = (
        client.table("legislative_districts")
        .select("id, geom")
        .eq("chamber", chamber)
        .eq("district_number", district_number)
        .is_("valid_to", "null")
        .limit(1)
        .execute()
    )
    existing_rows = existing_response.data or []
    geometry_payload = mapping(geom)
    if not existing_rows:
        client.table("legislative_districts").insert(
            {
                "chamber": chamber,
                "district_number": district_number,
                "geom": geometry_payload,
                "source_sr": source_srid,
                "source_objectid": source_objectid,
            }
        ).execute()
        return UpsertResult(action="inserted")
    existing_row = existing_rows[0]
    existing_geom = existing_row.get("geom")
    if existing_geom is None:
        raise RepositoryError("Existing district row missing geometry")
    existing_shape = shape(existing_geom)
    if geometries_equal(existing_shape, geom):
        return UpsertResult(action="unchanged")
    client.table("legislative_districts").update(
        {"valid_to": (date.today() - timedelta(days=1)).isoformat()}
    ).eq("id", existing_row["id"]).execute()
    client.table("legislative_districts").insert(
        {
            "chamber": chamber,
            "district_number": district_number,
            "geom": geometry_payload,
            "source_sr": source_srid,
            "source_objectid": source_objectid,
            "valid_from": date.today().isoformat(),
        }
    ).execute()
    return UpsertResult(action="updated")


def upsert_district(
    chamber: str,
    district_number: int,
    geom: MultiPolygon,
    source_srid: int,
    source_objectid: int,
) -> UpsertResult:
    """
    Logic:
    1. Find active row where:
         chamber = ?
         district_number = ?
         valid_to IS NULL
    2. If none exists → INSERT
    3. If exists AND geometry is identical → NOOP
    4. If exists AND geometry differs:
         a. UPDATE existing row set valid_to = current_date - 1
         b. INSERT new row with valid_from = current_date
    """
    if os.environ.get("DATABASE_URL"):
        return _psycopg2_upsert(
            chamber, district_number, geom, source_srid, source_objectid
        )
    return _supabase_upsert(
        chamber, district_number, geom, source_srid, source_objectid
    )
