import os
from unittest import mock

import pytest

from backend import config


def test_load_config_defaults() -> None:
    with mock.patch.dict(os.environ, {}, clear=True):
        cfg = config.load_config()
        assert cfg.supabase_url == "https://zgtevahaudnjpocptzgj.supabase.co"
        assert cfg.supabase_service_key == ""
        assert cfg.supabase_db_url == ""


def test_load_config_env_vars() -> None:
    env = {
        "NJLEG_DOWNLOAD_BASE_URL": "http://example.com",
        "SUPABASE_URL": "http://supabase.example.com",
        "SUPABASE_SERVICE_ROLE_KEY": "secret",
        "SUPABASE_DB_URL": "postgres://user:pass@host:5432/db",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        cfg = config.load_config()
        assert cfg.base_url == "https://www.njleg.state.nj.us/downloads"
        assert cfg.supabase_url == "http://supabase.example.com"
        assert cfg.supabase_service_key == "secret"
        assert cfg.supabase_db_url == "postgres://user:pass@host:5432/db"


def test_load_config_years() -> None:
    env = {"NJLEG_BILL_TRACKING_YEARS": "2020, 2021"}
    with mock.patch.dict(os.environ, env, clear=True):
        cfg = config.load_config()
        assert cfg.bill_tracking_years == (2020, 2021)

def test_load_config_backend_mode_local_postgres() -> None:
    # Test BACKEND_MODE=local_postgres
    env = {
        "BACKEND_MODE": "local_postgres",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        cfg = config.load_config()
        assert cfg.supabase_url == "http://localhost:5432"
        assert cfg.supabase_db_url == "postgresql://postgres:postgres@db:5432/postgres"

def test_load_config_backend_mode_local_supabase() -> None:
    # Test BACKEND_MODE=local_supabase
    env = {
        "BACKEND_MODE": "local_supabase",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        cfg = config.load_config()
        assert cfg.supabase_url == "http://127.0.0.1:54321"
        assert cfg.supabase_db_url == "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

def test_load_config_legacy_local_dev() -> None:
    # Test deprecated LOCAL_DEV=true falls back to local_postgres
    env = {
        "LOCAL_DEV": "true",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        cfg = config.load_config()
        assert cfg.supabase_url == "http://localhost:5432"
        # Should match local_postgres defaults
