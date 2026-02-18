from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.event import Event


class TimeWindowQueryEngine:
    """
    Deterministic, index-aware time window querying.
    Uses flat_event_type + timestamp composite index.
    """

    @staticmethod
    def get_events_within_window(
        db: Session,
        *,
        endpoint_id: int,
        event_type: str,
        reference_time: datetime,
        window_seconds: int,
    ) -> List[Event]:
        window_start = reference_time - timedelta(seconds=window_seconds)

        return (
            db.query(Event)
            .filter(
                and_(
                    Event.endpoint_id == endpoint_id,
                    Event.flat_event_type == event_type,
                    Event.timestamp >= window_start,
                    Event.timestamp <= reference_time,
                )
            )
            .order_by(Event.timestamp.asc())
            .all()
        )
