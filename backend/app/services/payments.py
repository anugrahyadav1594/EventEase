"""Payment workflows: recording money and keeping revenue consistent."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import attendees, events, payments, registrations

ALLOWED_PAYMENT_TRANSITIONS: dict[str, set[str]] = {
    "Pending": {"Pending", "Completed", "Refunded"},
    "Completed": {"Completed", "Refunded"},
    "Refunded": {"Refunded"},
}

BASE_PAYMENT_QUERY = (
    select(
        payments,
        registrations.c.attendee_id,
        registrations.c.event_id,
        attendees.c.full_name.label("attendee_name"),
        events.c.event_name.label("event_name"),
    )
    .select_from(
        payments.join(registrations, registrations.c.registration_id == payments.c.registration_id).join(
            attendees, attendees.c.attendee_id == registrations.c.attendee_id
        ).join(events, events.c.event_id == registrations.c.event_id)
    )
)


def get_payment_or_404(session: Session, payment_id: int):
    row = session.execute(BASE_PAYMENT_QUERY.where(payments.c.payment_id == payment_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payment {payment_id} was not found.")
    return row


def list_payments(
    session: Session,
    *,
    status_filter: str | None = None,
    method_filter: str | None = None,
    registration_id: int | None = None,
    event_id: int | None = None,
    search: str | None = None,
) -> list[dict]:
    statement = BASE_PAYMENT_QUERY.order_by(payments.c.payment_date.desc(), payments.c.payment_id.desc())
    if status_filter:
        statement = statement.where(payments.c.payment_status == status_filter)
    if method_filter:
        statement = statement.where(payments.c.payment_method == method_filter)
    if registration_id:
        statement = statement.where(payments.c.registration_id == registration_id)
    if event_id:
        statement = statement.where(registrations.c.event_id == event_id)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            attendees.c.full_name.like(pattern) | payments.c.transaction_reference.like(pattern)
        )
    return [dict(row._mapping) for row in session.execute(statement).all()]


def create_payment(session: Session, payload) -> dict:
    registration = session.execute(
        select(
            registrations.c.registration_id,
            registrations.c.ticket_price,
            registrations.c.registration_status,
            attendees.c.full_name.label("attendee_name"),
            events.c.event_name.label("event_name"),
        )
        .select_from(
            registrations.join(attendees, attendees.c.attendee_id == registrations.c.attendee_id).join(
                events, events.c.event_id == registrations.c.event_id
            )
        )
        .where(registrations.c.registration_id == payload.registration_id)
    ).first()
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration {payload.registration_id} was not found.",
        )
    if registration.registration_status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A payment cannot be recorded for a cancelled registration.",
        )

    if payload.transaction_reference:
        existing = session.execute(
            select(payments.c.payment_id).where(payments.c.transaction_reference == payload.transaction_reference)
        ).first()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transaction reference '{payload.transaction_reference}' is already used by payment {existing[0]}.",
            )

    values = {
        "registration_id": payload.registration_id,
        "amount": payload.amount,
        "payment_method": payload.payment_method.value if hasattr(payload.payment_method, "value") else payload.payment_method,
        "payment_status": payload.payment_status.value if hasattr(payload.payment_status, "value") else payload.payment_status,
        "transaction_reference": payload.transaction_reference,
        "payment_date": payload.payment_date or datetime.now(),
    }
    result = session.execute(payments.insert().values(**values))
    session.commit()
    return get_payment_or_404(session, int(result.inserted_primary_key[0]))._mapping


def update_payment_status(session: Session, payment_id: int, new_status: str) -> dict:
    row = get_payment_or_404(session, payment_id)
    mapping = dict(row._mapping)
    current = mapping["payment_status"]
    target = new_status.value if hasattr(new_status, "value") else new_status

    if target not in ALLOWED_PAYMENT_TRANSITIONS.get(current, set()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A payment cannot move from '{current}' to '{target}'.",
        )

    values: dict = {"payment_status": target}
    if target == "Completed":
        values["payment_date"] = datetime.now()

    session.execute(payments.update().where(payments.c.payment_id == payment_id).values(**values))
    session.commit()
    return get_payment_or_404(session, payment_id)._mapping


def revenue_summary(session: Session) -> dict[str, Decimal]:
    """Revenue is only counted for payments in the `Completed` state.

    A refunded payment is flipped to `Refunded` and is therefore never part of
    the completed sum - refunded money can not be counted twice.
    """
    rows = session.execute(
        select(payments.c.payment_status, func.coalesce(func.sum(payments.c.amount), 0)).group_by(
            payments.c.payment_status
        )
    ).all()
    summary = {status_name: Decimal("0") for status_name in ("Pending", "Completed", "Refunded")}
    for payment_status, total in rows:
        summary[payment_status] = Decimal(str(total or 0))
    summary["collected"] = summary["Completed"]
    summary["outstanding"] = summary["Pending"]
    summary["refunded"] = summary["Refunded"]
    return summary
