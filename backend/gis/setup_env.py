from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from importlib.util import find_spec
from typing import Iterable


@dataclass(frozen=True)
class DependencySpec:
    module: str
    package: str


DEPENDENCIES: tuple[DependencySpec, ...] = (
    DependencySpec(module="requests", package="requests"),
    DependencySpec(module="shapely", package="shapely"),
    DependencySpec(module="pyproj", package="pyproj"),
    DependencySpec(module="geojson", package="geojson"),
    DependencySpec(module="supabase", package="supabase"),
    DependencySpec(module="dotenv", package="python-dotenv"),
    DependencySpec(module="psycopg2", package="psycopg2-binary"),
)


class DependencyError(RuntimeError):
    pass


def _log(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True))


def _missing_dependencies(dependencies: Iterable[DependencySpec]) -> list[DependencySpec]:
    missing: list[DependencySpec] = []
    for dep in dependencies:
        if find_spec(dep.module) is None:
            missing.append(dep)
    return missing


def ensure_dependencies() -> None:
    missing = _missing_dependencies(DEPENDENCIES)
    if not missing:
        _log({"action": "dependencies_ready"})
        return
    packages = [dep.package for dep in missing]
    _log({"action": "installing_dependencies", "packages": packages})
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
    _log({"action": "dependencies_installed", "packages": packages})
