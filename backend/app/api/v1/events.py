import logging
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.event_schema import Event
from app.services.endpoint_registry import endpoint_registry
from app.services.event_guard import event_guard
from datetime import datetime, timezone
from app.core.config import settings
import hmac
import hashlib



router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(request: Request, event: Event):

    # ─────────────────────────────────────────────
    # 1️⃣ TRUST CHECK
    # ─────────────────────────────────────────────
    if not endpoint_registry.is_registered(event.endpoint.endpoint_id):
        logger.warning(
            f"Rejected event from unregistered endpoint | "
            f"endpoint={event.endpoint.endpoint_id}"
        )
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

    secret = endpoint_registry.get_secret(event.endpoint.endpoint_id)

    raw_body = await request.body()

    expected_signature = hmac.new(
        secret.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        logger.warning(
            f"Invalid signature | endpoint={event.endpoint.endpoint_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # ─────────────────────────────────────────────
    # 2️⃣ REPLAY PROTECTION
    # ─────────────────────────────────────────────
    if event_guard.is_duplicate(str(event.event_id)):
        logger.warning(
            f"Replay detected | event_id={event.event_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate event_id",
        )

    # Record event as seen
    event_guard.record(str(event.event_id))

        # ─────────────────────────────────────────────
    # 3️⃣ TIMESTAMP DRIFT VALIDATION
    # ─────────────────────────────────────────────
    now = datetime.now(timezone.utc)

    event_time = event.timestamp

    # Normalize naive timestamps to UTC
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)

    drift = abs((now - event_time).total_seconds())

    if drift > settings.MAX_TIMESTAMP_DRIFT_SECONDS:
        logger.warning(
            f"Rejected event due to timestamp drift | "
            f"event_id={event.event_id} | drift={drift}s"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid timestamp drift",
        )


    # ─────────────────────────────────────────────
    # 3️⃣ ACCEPT EVENT
    # ─────────────────────────────────────────────
    logger.info(
        f"Event accepted | "
        f"event_id={event.event_id} | "
        f"endpoint={event.endpoint.endpoint_id} | "
        f"type={event.event_type.value}"
    )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "event_id": str(event.event_id),
        },
    )
