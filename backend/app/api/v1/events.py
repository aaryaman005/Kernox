import logging
from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.event_schema import Event
from app.services.endpoint_registry import endpoint_registry

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(request: Request, event: Event):
    """
    Secure event ingestion endpoint.

    Security Layers:
    - Strict schema validation via Pydantic
    - Rejects unknown fields
    - Enforces schema version
    - Enforces exactly one payload group
    - Rejects unregistered endpoints
    """

    # ─────────────────────────────────────────────
    # 1️⃣ TRUST BOUNDARY CHECK
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
    # 2️⃣ ACCEPT EVENT (minimal safe logging)
    # ─────────────────────────────────────────────
    logger.info(
        f"Event accepted | "
        f"event_id={event.event_id} | "
        f"endpoint={event.endpoint.endpoint_id} | "
        f"type={event.event_type.value}"
    )

    # ─────────────────────────────────────────────
    # FUTURE SECURITY HOOKS (DO NOT REMOVE)
    # ─────────────────────────────────────────────
    # TODO:
    # - Verify HMAC signature
    # - Enforce rate limiting
    # - Check replay protection (event_id uniqueness)
    # - Timestamp drift validation
    # - Persist event to database
    # - Send to queue/worker pipeline

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "event_id": str(event.event_id),
        },
    )
