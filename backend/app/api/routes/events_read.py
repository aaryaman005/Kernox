from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.db.session import get_db
from app.models.event import Event as EventModel
from app.models.endpoint import Endpoint
from app.schemas.event_read_schema import EventRead, EventListResponse
from app.schemas.event_schema import Severity, EventType


router = APIRouter()

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

ALLOWED_SORT_FIELDS = {
    "received_at": EventModel.received_at,
}


def _serialize(event: EventModel) -> EventRead:
    payload = event.payload or {}

    return EventRead(
        event_id=payload.get("event_id"),
        endpoint_id=event.endpoint.endpoint_id,
        event_type=payload.get("event_type"),
        severity=payload.get("severity"),
        timestamp=payload.get("timestamp"),
        received_at=event.received_at,
        payload=payload,
    )


# ─────────────────────────────────────────────
# GET SINGLE EVENT
# ─────────────────────────────────────────────
@router.get("/events/{event_id}", response_model=EventRead)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    stmt = (
        select(EventModel)
        .join(Endpoint)
        .where(EventModel.payload["event_id"].as_string() == str(event_id))
    )

    event = db.execute(stmt).scalar_one_or_none()

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return _serialize(event)


# ─────────────────────────────────────────────
# LIST EVENTS
# ─────────────────────────────────────────────
@router.get("/events", response_model=EventListResponse)
def list_events(
    db: Session = Depends(get_db),
    endpoint_id: Optional[str] = None,
    severity: Optional[Severity] = None,
    event_type: Optional[EventType] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1),
    sort_by: str = "received_at",
):
    if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE

    stmt = select(EventModel).join(Endpoint)

    if endpoint_id:
        stmt = stmt.where(Endpoint.endpoint_id == endpoint_id)

    if severity:
        stmt = stmt.where(EventModel.payload["severity"].as_string() == severity.value)

    if event_type:
        stmt = stmt.where(
            EventModel.payload["event_type"].as_string() == event_type.value
        )

    if start:
        stmt = stmt.where(EventModel.received_at >= start)

    if end:
        stmt = stmt.where(EventModel.received_at <= end)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    sort_column = ALLOWED_SORT_FIELDS.get(sort_by, EventModel.received_at)
    stmt = stmt.order_by(desc(sort_column))

    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    events = db.execute(stmt).scalars().all()

    return EventListResponse(
        page=page,
        page_size=page_size,
        total=total,
        results=[_serialize(e) for e in events],
    )
