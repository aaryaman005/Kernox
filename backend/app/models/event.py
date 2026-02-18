from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
import uuid

from app.db.base import Base


# 🔵 Dialect-aware JSON type
class JSONBCompat(TypeDecorator):
    """
    Uses JSONB for PostgreSQL.
    Falls back to JSON for SQLite (tests).
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 🔐 Unique event id
    event_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="RESTRICT"),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    flat_event_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    flat_severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # 🔵 PostgreSQL → JSONB
    # 🔵 SQLite → JSON
    payload: Mapped[dict] = mapped_column(
        JSONBCompat(),
        nullable=False,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    endpoint = relationship("Endpoint")

    # 🔥 PRODUCTION SAFE NORMALIZATION (UNCHANGED LOGIC)
    def __init__(self, **kwargs):
        payload = kwargs.get("payload") or {}

        # Ensure event_id always exists
        event_id = kwargs.get("event_id") or payload.get("event_id")
        if not event_id:
            event_id = str(uuid.uuid4())

        kwargs["event_id"] = event_id

        # Ensure event_type exists
        if not kwargs.get("event_type") and payload.get("event_type"):
            kwargs["event_type"] = payload.get("event_type")

        # Normalized fields
        if not kwargs.get("flat_event_type") and payload.get("event_type"):
            kwargs["flat_event_type"] = payload.get("event_type")

        if not kwargs.get("flat_severity") and payload.get("severity"):
            kwargs["flat_severity"] = payload.get("severity")

        if not kwargs.get("timestamp") and payload.get("timestamp"):
            try:
                kwargs["timestamp"] = datetime.fromisoformat(payload.get("timestamp"))
            except Exception:
                kwargs["timestamp"] = datetime.now(timezone.utc)

        super().__init__(**kwargs)


# 🔥 Indexes (UNCHANGED)
Index("idx_events_endpoint_id", Event.endpoint_id)
Index("idx_events_timestamp", Event.timestamp)
Index("idx_events_event_type", Event.flat_event_type)
Index("idx_events_severity", Event.flat_severity)
