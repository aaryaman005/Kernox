from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel


class EventRead(BaseModel):
    event_id: UUID
    endpoint_id: str
    event_type: str
    severity: str
    timestamp: datetime
    received_at: datetime
    payload: dict[str, Any]

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
    }


class EventListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    results: list[EventRead]

    model_config = {"extra": "forbid"}
