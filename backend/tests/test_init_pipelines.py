from __future__ import annotations

from unittest import mock

import backend.init_pipelines as init_pipelines


def test_init_pipelines_runs_legislative_init(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-key")

    with (
        mock.patch.object(init_pipelines, "_load_initialize_schema") as load_initialize_schema,
        mock.patch.object(init_pipelines, "load_config") as load_config,
    ):
        load_config.return_value = mock.Mock(data_dir="backend/data", bill_tracking_years=(2024,))
        result = init_pipelines.main(["--pipeline", "legislative", "--action", "init", "--skip-schema"])

    assert result == 0
    load_initialize_schema.assert_not_called()


def test_init_pipelines_runs_gis_init(monkeypatch) -> None:
    monkeypatch.setenv("ARCGIS_REST_ROOT", "https://example.arcgis.com")
    monkeypatch.setenv("ARCGIS_LEGISLATIVE_DISTRICTS_LAYER", "/FeatureServer/0")
    monkeypatch.setenv("ARCGIS_QUERY_PAGE_SIZE", "2000")
    monkeypatch.setenv("ARCGIS_TARGET_SRID", "4326")
    monkeypatch.setenv("GIS_INGESTION_ENABLED", "true")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-key")

    with (
        mock.patch.object(init_pipelines, "ensure_gis_dependencies") as ensure_dependencies,
        mock.patch.object(init_pipelines, "_load_initialize_schema") as load_initialize_schema,
    ):
        result = init_pipelines.main(["--pipeline", "gis", "--action", "init", "--skip-schema"])

    assert result == 0
    ensure_dependencies.assert_called_once()
    load_initialize_schema.assert_not_called()
