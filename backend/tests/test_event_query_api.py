from uuid import uuid4
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.endpoint import Endpoint
from app.models.event import Event as EventModel


client = TestClient(app)


def create_test_event():
    db = SessionLocal()

    endpoint = Endpoint(
        endpoint_id="test-endpoint-1",
        secret_hash="dummyhash",
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)

    payload = {
        "event_id": str(uuid4()),
        "schema_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": {"endpoint_id": "test-endpoint-1", "hostname": "test-host"},
        "event_type": "process_start",
        "severity": "medium",
        "process": {"pid": 1, "ppid": 0, "name": "bash"},
    }

    event = EventModel(
        endpoint_id=endpoint.id,
        event_type="process_start",
        payload=payload,
    )

    db.add(event)
    db.commit()
    db.close()

    return payload["event_id"]


def test_get_single_event_success():
    event_id = create_test_event()

    response = client.get(f"/api/v1/events/{event_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["event_id"] == event_id
    assert "id" not in data
    assert "secret_hash" not in str(data)


def test_get_single_event_not_found():
    random_id = str(uuid4())

    response = client.get(f"/api/v1/events/{random_id}")

    assert response.status_code == 404


def test_invalid_uuid_returns_422():
    response = client.get("/api/v1/events/not-a-uuid")

    assert response.status_code == 422


def test_list_events_pagination_cap():
    create_test_event()

    response = client.get("/api/v1/events?page=1&page_size=500")

    assert response.status_code == 200
    data = response.json()

    assert data["page_size"] <= 100


def test_filter_by_severity():
    create_test_event()

    response = client.get("/api/v1/events?severity=medium")

    assert response.status_code == 200
    data = response.json()

    assert len(data["results"]) >= 1
    assert data["results"][0]["severity"] == "medium"


def test_sort_whitelist_enforced():
    create_test_event()

    response = client.get("/api/v1/events?sort_by=non_existing_field")

    assert response.status_code == 200
