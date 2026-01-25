from __future__ import annotations

import os
import subprocess
from pathlib import Path
from getpass import getpass


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
GITIGNORE_PATH = ROOT_DIR / ".gitignore"


def _prompt(label: str, *, secret: bool = False, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    prompt = f"{label}{suffix}: "
    if secret:
        value = getpass(prompt)
    else:
        value = input(prompt)
    if not value and default is not None:
        return default
    return value.strip()


def _ensure_gitignore() -> None:
    if not GITIGNORE_PATH.exists():
        GITIGNORE_PATH.write_text(".env\n", encoding="utf-8")
        return
    content = GITIGNORE_PATH.read_text(encoding="utf-8")
    if ".env" not in content.splitlines():
        with GITIGNORE_PATH.open("a", encoding="utf-8") as handle:
            handle.write("\n.env\n")


def _write_env(values: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in values.items() if value]
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    print("Backend bootstrap: this will create/update a local .env file (gitignored).")
    _ensure_gitignore()

    supabase_url = _prompt("SUPABASE_URL")
    service_role_key = _prompt("SUPABASE_SERVICE_ROLE_KEY", secret=True)
    anon_key = _prompt("SUPABASE_ANON_KEY (used by the app)", secret=True)
    database_url = _prompt("DATABASE_URL (optional, needed for schema init)", default="")

    env_values = {
        "SUPABASE_URL": supabase_url,
        "SUPABASE_SERVICE_ROLE_KEY": service_role_key,
        "SUPABASE_ANON_KEY": anon_key,
    }
    if database_url:
        env_values["DATABASE_URL"] = database_url

    _write_env(env_values)
    print(f"✅ Wrote {ENV_PATH}")

    if database_url:
        print("Initializing schema and pipelines...")
        _run(["python", "-m", "backend.init_pipelines", "--pipeline", "both", "--action", "init"])
    else:
        print("Skipping schema init (DATABASE_URL not provided).")

    print("Running backend tests...")
    _run(["python", "-m", "pytest", "backend/tests"])

    print("Bootstrap complete.")


if __name__ == "__main__":
    main()
