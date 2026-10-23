"""Events table - the core entity of the system."""
from __future__ import annotations

from sqlalchemy import (
    text,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    Time,
    text,
)

from .base import metadata
from .organizer import organizers
from .venue import venues

event_status_enum = Enum(
    "Upcoming",
    "Ongoing",
    "Completed",
    "Cancelled",
    name="event_status",
)

events = Table(
    "events",
    metadata,
    Column("event_id", Integer, primary_key=True, autoincrement=True),
    Column("event_name", String(160), nullable=False),
    Column("description", Text),
    Column("event_category", String(60), nullable=False),
    Column(
        "organizer_id",
        Integer,
        ForeignKey("organizers.organizer_id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column(
        "venue_id",
        Integer,
        ForeignKey("venues.venue_id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("event_date", Date, nullable=False),
    Column("start_time", Time, nullable=False),
    Column("end_time", Time, nullable=False),
    Column("capacity", Integer, nullable=False),
    Column("ticket_price", Numeric(10, 2), nullable=False, server_default="0"),
    Column(
        "event_status",
        event_status_enum,
        nullable=False,
        server_default="Upcoming",
    ),
    Column("created_at", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    # Business rule: capacity must be positive, price can never be negative.
    CheckConstraint("capacity > 0", name="ck_events_capacity_positive"),
    CheckConstraint("ticket_price >= 0", name="ck_events_ticket_price_non_negative"),
    CheckConstraint("end_time > start_time", name="ck_events_end_after_start"),
    # Indexes for the columns that are filtered / joined most often.
    Index("ix_events_event_date", "event_date"),
    Index("ix_events_event_category", "event_category"),
    Index("ix_events_event_status", "event_status"),
    Index("ix_events_organizer_id", "organizer_id"),
    Index("ix_events_venue_id", "venue_id"),
)
