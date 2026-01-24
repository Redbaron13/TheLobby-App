from backend.config import load_config


def test_load_config_prefers_service_role_key(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "publishable")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    config = load_config()
    assert config.supabase_service_key == "service-role"


def test_load_config_falls_back_to_publishable_key(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "publishable")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    config = load_config()
    assert config.supabase_service_key == "publishable"


def test_load_config_falls_back_to_anon_key(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    config = load_config()
    assert config.supabase_service_key == "anon"
