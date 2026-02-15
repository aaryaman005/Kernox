import logging
import hmac
import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.event_schema import Event
from app.services.endpoint_registry import endpoint_registry
from app.services.event_guard import event_guard
from app.services.rate_limiter import rate_limiter
from app.core.config import settings


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(request: Request, event: Event):

    endpoint_id = event.endpoint.endpoint_id

    # ─────────────────────────────────────────────
    # 1️⃣ TRUST CHECK
    # ─────────────────────────────────────────────
    if not endpoint_registry.is_registered(endpoint_id):
        logger.warning(
            "unregistered_endpoint",
            extra={
                "extra_data": {
                    "event": "unregistered_endpoint",
                    "endpoint_id": endpoint_id,
                }
            },
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

    secret_hash = endpoint_registry.get_secret_hash(endpoint_id)

    if not secret_hash:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unregistered endpoint",
        )

    raw_body = await request.body()

    expected_signature = hmac.new(
        secret_hash.encode(),  # hashed secret used as key
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        logger.warning(
            "invalid_signature",
            extra={
                "extra_data": {
                    "event": "invalid_signature",
                    "endpoint_id": endpoint_id,
                }
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # ─────────────────────────────────────────────
    # 3️⃣ RATE LIMITING
    # ─────────────────────────────────────────────
    if not rate_limiter.is_allowed(endpoint_id):
        logger.warning(
            "rate_limit_exceeded",
            extra={
                "extra_data": {
                    "event": "rate_limit_exceeded",
                    "endpoint_id": endpoint_id,
                }
            },
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    # ─────────────────────────────────────────────
    # 4️⃣ REPLAY PROTECTION
    # ─────────────────────────────────────────────
    event_id_str = str(event.event_id)

    if event_guard.is_duplicate(event_id_str):
        logger.warning(
            "replay_detected",
            extra={
                "extra_data": {
                    "event": "replay_detected",
                    "endpoint_id": endpoint_id,
                    "event_id": event_id_str,
                }
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate event_id",
        )

    event_guard.record(event_id_str)

    # ─────────────────────────────────────────────
    # 5️⃣ TIMESTAMP DRIFT VALIDATION
    # ─────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    event_time = event.timestamp

    # Ensure timezone awareness
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)

    drift = abs((now - event_time).total_seconds())

    if drift > settings.MAX_TIMESTAMP_DRIFT_SECONDS:
        logger.warning(
            "timestamp_drift_rejected",
            extra={
                "extra_data": {
                    "event": "timestamp_drift_rejected",
                    "endpoint_id": endpoint_id,
                    "event_id": event_id_str,
                    "drift_seconds": drift,
                }
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid timestamp drift",
        )

    # ─────────────────────────────────────────────
    # 6️⃣ ACCEPT EVENT
    # ─────────────────────────────────────────────
    logger.info(
        "event_accepted",
        extra={
            "extra_data": {
                "event": "event_accepted",
                "endpoint_id": endpoint_id,
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
