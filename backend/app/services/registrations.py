"""Registration workflows: enrolment, status transitions and attendance."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from ..models import attendees, events, payments, registrations, venues
from .events import ACTIVE_REGISTRATION_STATUSES, active_registration_count

# Allowed status transitions (used to reject impossible updates).
ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "Registered": {"Registered", "Confirmed", "Waitlisted", "Cancelled"},
    "Confirmed": {"Confirmed", "Registered", "Waitlisted", "Cancelled"},
    "Waitlisted": {"Waitlisted", "Registered", "Confirmed", "Cancelled"},
    "Cancelled": {"Cancelled", "Registered", "Waitlisted"},
}

BASE_REGISTRATION_QUERY = (
    select(
        registrations,
        attendees.c.full_name.label("attendee_name"),
        attendees.c.email.label("attendee_email"),
        events.c.event_name.label("event_name"),
        events.c.event_category.label("event_category"),
        events.c.event_date.label("event_date"),
        events.c.capacity.label("event_capacity"),
        venues.c.venue_name.label("venue_name"),
    )
    .select_from(
        registrations.join(attendees, attendees.c.attendee_id == registrations.c.attendee_id).join(
            events, events.c.event_id == registrations.c.event_id
        ).join(venues, venues.c.venue_id == events.c.venue_id)
    )
)


def _lock_event(session: Session, event_id: int):
    """Lock the event row so that two concurrent registrations cannot
    both pass the capacity check (MySQL row lock)."""
    statement = select(events.c.event_id, events.c.capacity, events.c.ticket_price, events.c.event_status).where(
        events.c.event_id == event_id
    )
    if session.bind is not None and session.bind.dialect.name != "sqlite":
        statement = statement.with_for_update()
    return session.execute(statement).first()


def get_registration_or_404(session: Session, registration_id: int):
    row = session.execute(BASE_REGISTRATION_QUERY.where(registrations.c.registration_id == registration_id)).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration {registration_id} was not found.",
        )
    return row


def list_registrations(
    session: Session,
    *,
    event_id: int | None = None,
    attendee_id: int | None = None,
    status_filter: str | None = None,
    attendance_filter: str | None = None,
    search: str | None = None,
) -> list[dict]:
    statement = BASE_REGISTRATION_QUERY.order_by(registrations.c.registration_date.desc(), registrations.c.registration_id.desc())
    if event_id:
        statement = statement.where(registrations.c.event_id == event_id)
    if attendee_id:
        statement = statement.where(registrations.c.attendee_id == attendee_id)
    if status_filter:
        statement = statement.where(registrations.c.registration_status == status_filter)
    if attendance_filter:
        statement = statement.where(registrations.c.attendance_status == attendance_filter)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                attendees.c.full_name.like(pattern),
                attendees.c.email.like(pattern),
                events.c.event_name.like(pattern),
            )
        )

    rows = session.execute(statement).all()
    registration_ids = [row._mapping["registration_id"] for row in rows]

    payment_state: dict[int, tuple[str | None, Decimal]] = {}
    if registration_ids:
        for row in session.execute(
            select(
                payments.c.registration_id,
                payments.c.payment_status,
                func.sum(payments.c.amount),
            )
            .where(payments.c.registration_id.in_(registration_ids))
            .group_by(payments.c.registration_id, payments.c.payment_status)
        ):
            registration_id, payment_status, amount = row
            current_status, current_amount = payment_state.get(registration_id, (None, Decimal("0")))
            if payment_status == "Completed":
                current_amount = current_amount + Decimal(str(amount or 0))
            payment_state[registration_id] = (payment_status or current_status, current_amount)

    results: list[dict] = []
    for row in rows:
        mapping = dict(row._mapping)
        payment_status, amount_paid = payment_state.get(mapping["registration_id"], (None, Decimal("0")))
        mapping["payment_status"] = payment_status
        mapping["amount_paid"] = amount_paid
        results.append(mapping)
    return results


def create_registration(session: Session, payload) -> dict:
    """Register an attendee for an event (transactional capacity check)."""
    attendee = session.execute(
        select(attendees.c.attendee_id, attendees.c.full_name).where(attendees.c.attendee_id == payload.attendee_id)
    ).first()
    if attendee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendee {payload.attendee_id} was not found.",
        )

    locked_event = _lock_event(session, payload.event_id)
    if locked_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {payload.event_id} was not found.",
        )
    _, event_capacity, event_ticket_price, event_status = locked_event

    if event_status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This event was cancelled, registrations are closed.",
        )
    if event_status == "Completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This event is already over, registrations are closed.",
        )

    duplicate = session.execute(
        select(registrations.c.registration_id).where(
            registrations.c.attendee_id == payload.attendee_id,
            registrations.c.event_id == payload.event_id,
        )
    ).first()
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Attendee {attendee[1]} is already registered for this event "
                f"(registration {duplicate[0]})."
            ),
        )

    active = active_registration_count(session, payload.event_id)
    if active >= int(event_capacity):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"This event is full: {active} of {int(event_capacity)} seats are taken. "
                "A waitlisted place can be requested instead."
            ),
        )

    ticket_price = payload.ticket_price if payload.ticket_price is not None else event_ticket_price
    values = {
        "attendee_id": payload.attendee_id,
        "event_id": payload.event_id,
        "registration_date": payload.registration_date or datetime.now(),
        "registration_status": payload.registration_status.value if hasattr(payload.registration_status, "value") else payload.registration_status,
        "attendance_status": "Not Marked",
        "ticket_type": payload.ticket_type or ("Free" if Decimal(str(ticket_price)) == 0 else "General"),
        "ticket_price": ticket_price,
    }
    result = session.execute(registrations.insert().values(**values))
    session.commit()
    return get_registration_or_404(session, int(result.inserted_primary_key[0]))._mapping


def update_registration_status(session: Session, registration_id: int, new_status: str) -> dict:
    row = get_registration_or_404(session, registration_id)
    mapping = dict(row._mapping)
    current = mapping["registration_status"]
    target = new_status.value if hasattr(new_status, "value") else new_status

    if target not in ALLOWED_STATUS_TRANSITIONS.get(current, set()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A registration cannot move from '{current}' to '{target}'.",
        )

    if target in ACTIVE_REGISTRATION_STATUSES and current not in ACTIVE_REGISTRATION_STATUSES:
        active = active_registration_count(session, mapping["event_id"])
        capacity = int(mapping["event_capacity"])
        if active >= capacity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"This event is full ({active}/{capacity}); the registration cannot be confirmed.",
            )

    session.execute(
        registrations.update()
        .where(registrations.c.registration_id == registration_id)
        .values(registration_status=target)
    )
    session.commit()
    return get_registration_or_404(session, registration_id)._mapping


def mark_attendance(session: Session, registration_id: int, attendance_status: str) -> dict:
    row = get_registration_or_404(session, registration_id)
    mapping = dict(row._mapping)
    if mapping["registration_status"] == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance cannot be recorded for a cancelled registration.",
        )
    target = attendance_status.value if hasattr(attendance_status, "value") else attendance_status
    session.execute(
        registrations.update()
        .where(registrations.c.registration_id == registration_id)
        .values(attendance_status=target)
    )
    session.commit()
    return get_registration_or_404(session, registration_id)._mapping
