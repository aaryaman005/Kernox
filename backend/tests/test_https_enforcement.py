from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


client = TestClient(app)


def test_http_allowed_in_development():
    settings.ENV = "development"
    settings.ENFORCE_HTTPS = True

    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_http_blocked_in_production():
    settings.ENV = "production"
    settings.ENFORCE_HTTPS = True

    response = client.get("/api/v1/health")
    assert response.status_code == 400
    assert response.json()["detail"] == "HTTPS required"

    # Reset to avoid affecting other tests
    settings.ENV = "development"
    settings.ENFORCE_HTTPS = False
