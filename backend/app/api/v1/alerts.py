from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.db.session import get_db
from app.models.alert import Alert
from app.schemas.alert_read_schema import AlertListResponse, AlertRead

router = APIRouter()

MAX_PAGE_SIZE = 100

SORTABLE_FIELDS = {
    "created_at": Alert.created_at,
    "risk_score": Alert.risk_score,
    "severity": Alert.severity,
}

ALLOWED_SORT_ORDERS = {"asc", "desc"}


@router.get("/alerts", response_model=AlertListResponse)
def list_alerts(
    db: Session = Depends(get_db),
    endpoint_id: int | None = Query(default=None),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    min_risk: int | None = Query(default=None, ge=0),
    max_risk: int | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
):
    # Enforce page_size cap
    if page_size > MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"page_size cannot exceed {MAX_PAGE_SIZE}",
        )

    # Validate sort field
    if sort_by not in SORTABLE_FIELDS:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by field",
        )

    # Validate sort order
    if sort_order not in ALLOWED_SORT_ORDERS:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_order value",
        )

    query = db.query(Alert)

    # ───────────── Filtering ─────────────
    if endpoint_id is not None:
        query = query.filter(Alert.endpoint_id == endpoint_id)

    if severity is not None:
        query = query.filter(Alert.severity == severity)

    if status is not None:
        query = query.filter(Alert.status == status)

    if min_risk is not None:
        query = query.filter(Alert.risk_score >= min_risk)

    if max_risk is not None:
        query = query.filter(Alert.risk_score <= max_risk)

    total = query.count()

    # ───────────── Sorting ─────────────
    sort_column = SORTABLE_FIELDS[sort_by]

    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # ───────────── Pagination ─────────────
    offset = (page - 1) * page_size
    alerts = query.offset(offset).limit(page_size).all()

    return AlertListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=[AlertRead.model_validate(alert) for alert in alerts],
    )
