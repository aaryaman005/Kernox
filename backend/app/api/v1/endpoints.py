from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import logging

from app.schemas.endpoint_schema import EndpointRegistration
from app.services.endpoint_registry import endpoint_registry

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/endpoints/register", status_code=status.HTTP_201_CREATED)
def register_endpoint(payload: EndpointRegistration):

    endpoint_registry.register(
        endpoint_id=payload.endpoint_id,
        hostname=payload.hostname,
    )

    logger.info(f"Endpoint registered | endpoint_id={payload.endpoint_id}")

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "registered",
            "endpoint_id": payload.endpoint_id,
        },
    )
