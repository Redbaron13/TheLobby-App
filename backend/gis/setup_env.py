from __future__ import annotations

import json
import subprocess
import sys
from importlib.util import find_spec


DEPENDENCIES: tuple[tuple[str, str], ...] = (
    ("requests", "requests"),
    ("shapely", "shapely"),
    ("pyproj", "pyproj"),
    ("geojson", "geojson"),
    ("supabase", "supabase"),
    ("dotenv", "python-dotenv"),
    ("psycopg2", "psycopg2-binary"),
)


class DependencyError(RuntimeError):
    pass


def _log(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


def _install_packages(packages: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", *packages],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        _log(
            {
                "action": "dependency_install_failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        raise DependencyError("Failed to install dependencies")


def ensure_dependencies() -> None:
    missing = [package for module, package in DEPENDENCIES if find_spec(module) is None]
    if not missing:
        _log({"action": "dependencies_ready"})
        return
    _log({"action": "installing_dependencies", "packages": missing})
    _install_packages(missing)
    _log({"action": "dependencies_installed", "packages": missing})
