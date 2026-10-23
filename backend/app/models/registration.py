"""Registrations table - links attendees to events.

The composite UNIQUE constraint on (attendee_id, event_id) is what prevents a
duplicate registration at database level (the API also checks it inside the
same transaction so the user gets a friendly error message).
"""
from __future__ import annotations

from sqlalchemy import (
    text,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    text,
)

from .base import metadata
from .attendee import attendees
from .event import events

registration_status_enum = Enum(
    "Registered",
    "Confirmed",
    "Cancelled",
    "Waitlisted",
    name="registration_status",
)

attendance_status_enum = Enum(
    "Not Marked",
    "Present",
    "Absent",
    name="attendance_status",
)

registrations = Table(
    "registrations",
    metadata,
    Column("registration_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "attendee_id",
        Integer,
        ForeignKey("attendees.attendee_id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column(
        "event_id",
        Integer,
        ForeignKey("events.event_id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("registration_date", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column(
        "registration_status",
        registration_status_enum,
        nullable=False,
        server_default="Registered",
    ),
    Column(
        "attendance_status",
        attendance_status_enum,
        nullable=False,
        server_default="Not Marked",
    ),
    Column("ticket_type", String(40)),
    Column("ticket_price", Numeric(10, 2), nullable=False, server_default="0"),
    CheckConstraint("ticket_price >= 0", name="ck_registrations_ticket_price_non_negative"),
    UniqueConstraint("attendee_id", "event_id", name="uq_registrations_attendee_event"),
    Index("ix_registrations_event_id", "event_id"),
    Index("ix_registrations_attendee_id", "attendee_id"),
    Index("ix_registrations_registration_status", "registration_status"),
    Index("ix_registrations_attendance_status", "attendance_status"),
)
