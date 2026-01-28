from __future__ import annotations

from unittest import mock

import backend.init_arcgis_pipeline as init_arcgis_pipeline
import backend.init_legislative_pipeline as init_legislative_pipeline


def test_init_legislative_pipeline_runs() -> None:
    with (
        mock.patch.object(init_legislative_pipeline, "load_config") as load_config,
        mock.patch.object(init_legislative_pipeline, "run_pipeline") as run_pipeline,
    ):
        load_config.return_value = mock.Mock()
        run_pipeline.return_value = mock.Mock(
            bills=1,
            legislators=2,
            former_legislators=3,
            bill_sponsors=4,
            committee_members=5,
            vote_records=6,
            districts=7,
            validation_issues=0,
        )
        result = init_legislative_pipeline.main()

    assert result == 0
    load_config.assert_called_once()
    run_pipeline.assert_called_once()


def test_init_arcgis_pipeline_runs() -> None:
    with (
        mock.patch.object(init_arcgis_pipeline, "ensure_dependencies") as ensure_dependencies,
        mock.patch.object(init_arcgis_pipeline, "_load_ingest_main") as load_ingest_main,
    ):
        ingest_main = mock.Mock(return_value=0)
        load_ingest_main.return_value = ingest_main
        result = init_arcgis_pipeline.main()

    assert result == 0
    ensure_dependencies.assert_called_once()
    load_ingest_main.assert_called_once()
    ingest_main.assert_called_once()
