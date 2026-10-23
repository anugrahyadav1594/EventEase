"""Business rules for events (capacity vs. venue, venue double booking)."""
from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from ..models import events, organizers, payments, registrations, venues
from .helpers import rows_as_dicts

ACTIVE_REGISTRATION_STATUSES = ("Registered", "Confirmed")


def get_event_or_404(session: Session, event_id: int):
    row = session.execute(
        select(
            events,
            organizers.c.organizer_name,
            organizers.c.organization_name,
            venues.c.venue_name,
            venues.c.location.label("venue_location"),
            venues.c.capacity.label("venue_capacity"),
        )
        .select_from(
            events.join(organizers, organizers.c.organizer_id == events.c.organizer_id).join(
                venues, venues.c.venue_id == events.c.venue_id
            )
        )
        .where(events.c.event_id == event_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} was not found.")
    return row


def registration_counts(session: Session, event_id: int) -> dict[str, int]:
    counts = {status_name: 0 for status_name in ("Registered", "Confirmed", "Cancelled", "Waitlisted")}
    for row in session.execute(
        select(registrations.c.registration_status, func.count(registrations.c.registration_id))
        .where(registrations.c.event_id == event_id)
        .group_by(registrations.c.registration_status)
    ):
        counts[row[0]] = int(row[1])
    return counts


def active_registration_count(session: Session, event_id: int) -> int:
    """Registrations that consume a seat (waitlisted / cancelled do not)."""
    return int(
        session.execute(
            select(func.count(registrations.c.registration_id)).where(
                registrations.c.event_id == event_id,
                registrations.c.registration_status.in_(ACTIVE_REGISTRATION_STATUSES),
            )
        ).scalar()
        or 0
    )


def assert_capacity_within_venue(session: Session, venue_id: int, capacity: int) -> None:
    venue_capacity = session.execute(
        select(venues.c.capacity, venues.c.venue_name).where(venues.c.venue_id == venue_id)
    ).first()
    if venue_capacity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue {venue_id} was not found.")
    if capacity > int(venue_capacity[0]):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Event capacity ({capacity}) cannot exceed the capacity of "
                f"{venue_capacity[1]} ({int(venue_capacity[0])} seats)."
            ),
        )


def assert_organizer_exists(session: Session, organizer_id: int) -> None:
    """Make sure the referenced organizer really exists (clear 404 instead of a DB error)."""
    exists = session.execute(
        select(organizers.c.organizer_id).where(organizers.c.organizer_id == organizer_id)
    ).first()
    if exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organizer {organizer_id} was not found.",
        )


def assert_venue_available(session: Session, venue_id: int, event_date: date, start_time: time, end_time: time, event_id: int | None = None) -> None:
    """Reject a booking that overlaps another event in the same venue.

    Two events overlap when `start_time < other.end_time` and
    `end_time > other.start_time` on the same calendar day.
    """
    statement = select(
        events.c.event_id,
        events.c.event_name,
        events.c.start_time,
        events.c.end_time,
    ).where(
        events.c.venue_id == venue_id,
        events.c.event_date == event_date,
        events.c.event_status != "Cancelled",
        events.c.start_time < end_time,
        events.c.end_time > start_time,
    )
    if event_id is not None:
        statement = statement.where(events.c.event_id != event_id)

    clash = session.execute(statement).first()
    if clash is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Venue is already booked on {event_date.isoformat()} for "
                f"'{clash[1]}' ({clash[2]} - {clash[3]}). The new slot overlaps it."
            ),
        )


def assert_capacity_not_below_registered(session: Session, event_id: int, capacity: int) -> None:
    registered = active_registration_count(session, event_id)
    if capacity < registered:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"The event already has {registered} active registrations, "
                f"so the capacity cannot be reduced to {capacity}."
            ),
        )


def list_events(
    session: Session,
    *,
    search: str | None = None,
    category: str | None = None,
    status_filter: str | None = None,
    organizer_id: int | None = None,
    venue_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[dict]:
    statement = (
        select(
            events,
            organizers.c.organizer_name,
            organizers.c.organization_name,
            venues.c.venue_name,
            venues.c.location.label("venue_location"),
        )
        .select_from(
            events.join(organizers, organizers.c.organizer_id == events.c.organizer_id).join(
                venues, venues.c.venue_id == events.c.venue_id
            )
        )
        .order_by(events.c.event_date.desc(), events.c.event_id.desc())
    )
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                events.c.event_name.like(pattern),
                events.c.description.like(pattern),
                events.c.event_category.like(pattern),
            )
        )
    if category:
        statement = statement.where(events.c.event_category == category)
    if status_filter:
        statement = statement.where(events.c.event_status == status_filter)
    if organizer_id:
        statement = statement.where(events.c.organizer_id == organizer_id)
    if venue_id:
        statement = statement.where(events.c.venue_id == venue_id)
    if date_from:
        statement = statement.where(events.c.event_date >= date_from)
    if date_to:
        statement = statement.where(events.c.event_date <= date_to)

    return rows_as_dicts(session.execute(statement))


def event_summary(session: Session, mapping: dict) -> dict:
    """Turn the joined event row into the JSON payload used by the API."""
    event_id = mapping["event_id"]
    counts = registration_counts(session, event_id)
    total = sum(counts.values())
    capacity = int(mapping["capacity"])
    present = int(
        session.execute(
            select(func.count(registrations.c.registration_id)).where(
                registrations.c.event_id == event_id,
                registrations.c.attendance_status == "Present",
            )
        ).scalar()
        or 0
    )
    revenue = session.execute(
        select(func.coalesce(func.sum(payments.c.amount), 0))
        .select_from(
            registrations.join(payments, payments.c.registration_id == registrations.c.registration_id)
        )
        .where(
            registrations.c.event_id == event_id,
            payments.c.payment_status == "Completed",
        )
    ).scalar() or 0
    return {
        "event_id": event_id,
        "event_name": mapping["event_name"],
        "description": mapping["description"],
        "event_category": mapping["event_category"],
        "organizer_id": mapping["organizer_id"],
        "organizer_name": mapping.get("organizer_name"),
        "organization_name": mapping.get("organization_name"),
        "venue_id": mapping["venue_id"],
        "venue_name": mapping.get("venue_name"),
        "venue_location": mapping.get("venue_location"),
        "event_date": mapping["event_date"],
        "start_time": mapping["start_time"],
        "end_time": mapping["end_time"],
        "capacity": capacity,
        "ticket_price": mapping["ticket_price"],
        "event_status": mapping["event_status"],
        "created_at": mapping.get("created_at"),
        "registration_count": total,
        "confirmed_count": counts.get("Confirmed", 0),
        "present_count": present,
        "seats_available": max(0, capacity - counts.get("Registered", 0) - counts.get("Confirmed", 0)),
        "fill_rate_percent": round((counts.get("Registered", 0) + counts.get("Confirmed", 0)) * 100.0 / capacity, 2)
        if capacity
        else 0.0,
        "revenue": revenue,
    }
