from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.services.endpoint_registry import endpoint_registry


client = TestClient(app)


def build_event(event_id: str):
    return {
        "event_id": event_id,
        "schema_version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": {
            "endpoint_id": "node-replay",
            "hostname": "ubuntu"
        },
        "event_type": "process_start",
        "severity": "low",
        "process": {
            "pid": 123,
            "ppid": 1,
            "name": "bash"
        },
        "file": None,
        "network": None,
        "auth": None,
        "signature": None
    }


def test_replay_protection():

    # Register endpoint first
    endpoint_registry.register("node-replay", "ubuntu")

    event_id = str(uuid4())
    payload = build_event(event_id)

    # First request should succeed
    response1 = client.post("/api/v1/events", json=payload)
    assert response1.status_code == 202

    # Second request with same event_id should fail
    response2 = client.post("/api/v1/events", json=payload)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Duplicate event_id"
