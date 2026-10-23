"""Venues table - physical locations where events are hosted."""
from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, Enum, Index, Integer, String, Table

from .base import metadata

venue_availability = Enum(
    "Available",
    "Unavailable",
    "Maintenance",
    name="venue_availability_status",
)

venues = Table(
    "venues",
    metadata,
    Column("venue_id", Integer, primary_key=True, autoincrement=True),
    Column("venue_name", String(120), nullable=False),
    Column("location", String(200), nullable=False),
    Column("capacity", Integer, nullable=False),
    Column("venue_type", String(60)),
    Column(
        "availability_status",
        venue_availability,
        nullable=False,
        server_default="Available",
    ),
    CheckConstraint("capacity > 0", name="ck_venues_capacity_positive"),
    Index("ix_venues_availability_status", "availability_status"),
    Index("ix_venues_venue_name", "venue_name"),
)
