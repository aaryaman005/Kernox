import logging
import hmac
import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Request, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.event_schema import Event
from app.services.event_guard import event_guard
from app.services.rate_limiter import rate_limiter
from app.core.config import settings
from app.db.session import get_db
from app.models.endpoint import Endpoint
from app.models.event import Event as EventModel
from app.services.detection_engine import DetectionEngine

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(
    request: Request,
    event: Event,
    db: Session = Depends(get_db),
):
    endpoint_external_id = event.endpoint.endpoint_id

    # ─────────────────────────────────────────────
    # 1️⃣ TRUST CHECK
    # ─────────────────────────────────────────────
    endpoint = db.query(Endpoint).filter_by(endpoint_id=endpoint_external_id).first()

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unregistered endpoint",
        )

    # ─────────────────────────────────────────────
    # 2️⃣ HMAC SIGNATURE VERIFICATION
    # ─────────────────────────────────────────────
    signature = request.headers.get("X-Signature")

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature",
        )

    raw_body = await request.body()

    expected_signature = hmac.new(
        endpoint.secret_hash.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # ─────────────────────────────────────────────
    # 3️⃣ RATE LIMITING
    # ─────────────────────────────────────────────
    if not rate_limiter.is_allowed(endpoint_external_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    # ─────────────────────────────────────────────
    # 4️⃣ REPLAY PROTECTION (memory check only)
    # ─────────────────────────────────────────────
    event_id_str = str(event.event_id)

    if event_guard.is_duplicate(event_id_str):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate event_id",
        )

    # ─────────────────────────────────────────────
    # 5️⃣ TIMESTAMP DRIFT VALIDATION
    # ─────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    event_time = event.timestamp

    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)

    drift = abs((now - event_time).total_seconds())

    if drift > settings.MAX_TIMESTAMP_DRIFT_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid timestamp drift",
        )

    # ─────────────────────────────────────────────
    # 6️⃣ NORMALIZED PERSISTENCE
    # ─────────────────────────────────────────────
    event_record = EventModel(
        event_id=event_id_str,
        endpoint_id=endpoint.id,
        event_type=event.event_type.value,  # required field
        flat_event_type=event.event_type.value,
        flat_severity=event.severity.value,
        timestamp=event_time,
        payload=event.model_dump(mode="json"),
    )

    try:
        db.add(event_record)
        db.flush()

        # 🔥 Run detection inside same transaction
        DetectionEngine.run(db, event_record)

        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate event_id",
        )

    # 🔥 RECORD REPLAY ONLY AFTER SUCCESSFUL COMMIT
    event_guard.record(event_id_str)

    logger.info(
        "event_accepted",
        extra={
            "extra_data": {
                "endpoint_id": endpoint_external_id,
                "event_id": event_id_str,
            }
        },
    )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "event_id": event_id_str,
        },
    )
