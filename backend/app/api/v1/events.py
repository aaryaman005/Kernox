import logging
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.schemas.event_schema import Event

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(request: Request, event: Event):
    """
    Secure event ingestion endpoint.

    - Strict schema validation via Pydantic
    - Rejects unknown fields
    - Enforces version
    - Enforces exactly one payload group
    """

    # ─────────────────────────────────────────────
    # SECURITY: Log minimal safe metadata only
    # ─────────────────────────────────────────────
    logger.info(
    f"Event accepted | event_id={event.event_id} | endpoint={event.endpoint.endpoint_id}"
    )


    # ─────────────────────────────────────────────
    # FUTURE SECURITY HOOKS (DO NOT REMOVE)
    # ─────────────────────────────────────────────
    # TODO:
    # - Verify endpoint registration
    # - Verify HMAC signature
    # - Enforce rate limiting
    # - Check replay protection (event_id uniqueness)
    # - Timestamp drift validation

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "event_id": str(event.event_id),
        },
    )
