"""Payment endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..schemas import PaymentCreate, PaymentRead, PaymentStatusUpdate
from ..services.helpers import jsonable_rows
from ..services.payments import (
    create_payment,
    get_payment_or_404,
    list_payments,
    revenue_summary,
    update_payment_status,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("")
def get_payments(
    session: Session = Depends(get_db),
    payment_status: str | None = Query(default=None, alias="status"),
    payment_method: str | None = Query(default=None, alias="method"),
    registration_id: int | None = Query(default=None),
    event_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
):
    rows = list_payments(
        session,
        status_filter=payment_status,
        method_filter=payment_method,
        registration_id=registration_id,
        event_id=event_id,
        search=search,
    )
    summary = revenue_summary(session)
    return {
        "items": jsonable_rows(rows),
        "total": len(rows),
        "summary": {key: float(value) for key, value in summary.items()},
    }


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, session: Session = Depends(get_db)):
    row = get_payment_or_404(session, payment_id)
    return jsonable_rows([dict(row._mapping)])[0]


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def post_payment(payload: PaymentCreate, session: Session = Depends(get_db)):
    row = create_payment(session, payload)
    return jsonable_rows([dict(row)])[0]


@router.patch("/{payment_id}/status", response_model=PaymentRead)
def patch_payment_status(
    payment_id: int,
    payload: PaymentStatusUpdate,
    session: Session = Depends(get_db),
):
    row = update_payment_status(session, payment_id, payload.payment_status)
    return jsonable_rows([dict(row)])[0]
