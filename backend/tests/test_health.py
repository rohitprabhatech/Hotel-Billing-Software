"""Health endpoint smoke tests (no DB required for /health)."""

from app import create_app


def test_health_ok():
    app = create_app("testing")
    client = app.test_client()
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "ok"
    assert payload["error"] is None


def test_root_ok():
    app = create_app("testing")
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["data"]["api_base"] == "/api/v1"