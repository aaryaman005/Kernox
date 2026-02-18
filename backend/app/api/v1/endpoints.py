from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from app.schemas.endpoint_schema import EndpointRegistration
from app.services.endpoint_registry import endpoint_registry
from app.db.session import get_db


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/endpoints/register", status_code=status.HTTP_201_CREATED)
def register_endpoint(
    payload: EndpointRegistration,
    db: Session = Depends(get_db),
):
    endpoint = endpoint_registry.register(
        db=db,
        endpoint_id=payload.endpoint_id,
        hostname=payload.hostname,
        secret=payload.secret,
    )

    logger.info(f"Endpoint registered | endpoint_id={endpoint.endpoint_id}")

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "registered",
            "endpoint_id": endpoint.endpoint_id,
        },
    )
