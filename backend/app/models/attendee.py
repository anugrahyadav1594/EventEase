"""Attendees table - the people who register for events."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, Index, Integer, String, Table, text

from .base import metadata

attendees = Table(
    "attendees",
    metadata,
    Column("attendee_id", Integer, primary_key=True, autoincrement=True),
    Column("full_name", String(140), nullable=False),
    Column("email", String(160), nullable=False, unique=True),
    Column("phone", String(25)),
    Column("organization", String(160)),
    Column("registration_date", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Index("ix_attendees_full_name", "full_name"),
)
