from __future__ import annotations

import json
import sys

from backend.config import load_config
from backend.pipeline import run_pipeline


def _log(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


def main() -> int:
    try:
        config = load_config()
        result = run_pipeline(config)
        _log(
            {
                "action": "pipeline_complete",
                "bills": result.bills,
                "legislators": result.legislators,
                "former_legislators": result.former_legislators,
                "bill_sponsors": result.bill_sponsors,
                "committee_members": result.committee_members,
                "vote_records": result.vote_records,
                "districts": result.districts,
                "validation_issues": result.validation_issues,
            }
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        _log({"action": "error", "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
