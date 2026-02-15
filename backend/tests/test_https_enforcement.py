from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


client = TestClient(app)


def test_http_allowed_in_development(monkeypatch):
    monkeypatch.setattr(settings, "ENV", "development")
    monkeypatch.setattr(settings, "ENFORCE_HTTPS", True)

    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_http_blocked_in_production(monkeypatch):
    monkeypatch.setattr(settings, "ENV", "production")
    monkeypatch.setattr(settings, "ENFORCE_HTTPS", True)

    response = client.get("/api/v1/health")
    assert response.status_code == 400
    assert response.json()["detail"] == "HTTPS required"
