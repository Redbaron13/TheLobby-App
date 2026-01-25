from __future__ import annotations

import json
import sys

from backend.gis.setup_env import ensure_dependencies


def _log(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


def _load_ingest_main():
    from backend.gis.ingest_legislative_districts import main as ingest_main

    return ingest_main


def main() -> int:
    try:
        ensure_dependencies()
        ingest_main = _load_ingest_main()
        result = ingest_main()
        if result == 0:
            _log({"action": "arcgis_ingestion_complete"})
        else:
            _log({"action": "arcgis_ingestion_failed"})
        return result
    except Exception as exc:  # noqa: BLE001
        _log({"action": "error", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
