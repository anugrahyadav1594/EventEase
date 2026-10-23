"""Insert the EventEase demo dataset into an empty database."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import insert, select
from sqlalchemy.engine import Connection

from ..models import attendees, events, metadata, organizers, payments, registrations, venues
from . import seed_data as sd


def _q(value: float | Decimal | int | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def database_is_empty(connection: Connection) -> bool:
    """True when the schema exists but does not contain any sample rows."""
    for table in (organizers, venues, events, attendees, registrations, payments):
        if connection.execute(select(table.c[table.c.keys()[0]]).limit(1)).first():
            return False
    return True


def seed_database(connection: Connection, reference: date | None = None) -> dict[str, int]:
    """Insert the full demo dataset and return the number of inserted rows."""
    reference = reference or sd.today()
    counts = {"organizers": 0, "venues": 0, "events": 0, "attendees": 0, "registrations": 0, "payments": 0}

    organizer_ids: list[int] = []
    for index, organizer in enumerate(sd.ORGANIZERS, start=1):
        # The primary keys are written explicitly so that the Python seeder and
        # `database/seed.sql` produce exactly the same rows with the same ids.
        connection.execute(
            insert(organizers).values(
                organizer_id=index,
                **organizer,
                created_at=datetime.combine(reference, time(hour=9)),
            )
        )
        organizer_ids.append(index)
    counts["organizers"] = len(organizer_ids)

    venue_ids: list[int] = []
    for index, venue in enumerate(sd.VENUES, start=1):
        connection.execute(insert(venues).values(venue_id=index, **venue))
        venue_ids.append(index)
    counts["venues"] = len(venue_ids)

    attendee_ids: list[int] = []
    for index, attendee in enumerate(sd.ATTENDEES, start=1):
        connection.execute(
            insert(attendees).values(
                attendee_id=index,
                **attendee,
                registration_date=datetime.combine(reference - timedelta(days=60), time(hour=8)),
            )
        )
        attendee_ids.append(index)
    counts["attendees"] = len(attendee_ids)

    event_ids: dict[str, int] = {}
    for index, event in enumerate(sd.EVENTS, start=1):
        connection.execute(
            insert(events).values(
                event_id=index,
                event_name=event.event_name,
                description=event.description,
                event_category=event.event_category,
                organizer_id=organizer_ids[event.organizer - 1],
                venue_id=venue_ids[event.venue - 1],
                event_date=sd.event_date(event, reference),
                start_time=datetime.strptime(event.start_time, "%H:%M:%S").time(),
                end_time=datetime.strptime(event.end_time, "%H:%M:%S").time(),
                capacity=event.capacity,
                ticket_price=_q(event.ticket_price),
                event_status=event.event_status,
                created_at=datetime.combine(reference - timedelta(days=90), time(hour=10)),
            )
        )
        event_ids[event.key] = index
    counts["events"] = len(event_ids)

    registration_id = 0
    payment_id = 0
    for event in sd.EVENTS:
        for seed in event.registrations:
            ticket_price = event.ticket_price if seed.amount is None else seed.amount
            registration_id += 1
            connection.execute(
                insert(registrations).values(
                    registration_id=registration_id,
                    attendee_id=attendee_ids[seed.attendee - 1],
                    event_id=event_ids[event.key],
                    registration_date=sd.registration_date(event, seed, reference),
                    registration_status=seed.status,
                    attendance_status=seed.attendance,
                    ticket_type=seed.ticket_type,
                    ticket_price=_q(ticket_price),
                )
            )
            counts["registrations"] += 1

            if seed.payment_status is not None:
                payment_id += 1
                connection.execute(
                    insert(payments).values(
                        payment_id=payment_id,
                        registration_id=registration_id,
                        amount=_q(ticket_price),
                        payment_method=seed.payment_method,
                        payment_status=seed.payment_status,
                        transaction_reference=f"TXN-{event.key}-{seed.attendee:02d}",
                        payment_date=sd.payment_date(event, seed, reference),
                    )
                )
                counts["payments"] += 1

    return counts


def create_schema(connection: Connection) -> None:
    """Create every table of the EventEase schema."""
    metadata.create_all(connection)
