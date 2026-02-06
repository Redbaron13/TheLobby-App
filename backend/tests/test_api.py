from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "idle"

def test_trigger_sync():
    # We don't want to actually run the pipeline in tests, but we can check the endpoint triggers
    response = client.post("/sync", json={})
    assert response.status_code == 200
    assert response.json()["message"] == "Pipeline triggered successfully"

    # Status should now be running (or completed if it finishes very fast, but it's a background task)
    status_resp = client.get("/status")
    assert status_resp.json()["status"] in ["running", "completed", "failed"]
