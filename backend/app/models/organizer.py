"""Organizers table - the people / clubs who run events."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, Index, Integer, String, Table, text

from .base import metadata

organizers = Table(
    "organizers",
    metadata,
    Column("organizer_id", Integer, primary_key=True, autoincrement=True),
    Column("organizer_name", String(120), nullable=False),
    Column("email", String(160), nullable=False, unique=True),
    Column("phone", String(25)),
    Column("organization_name", String(160)),
    Column("created_at", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Index("ix_organizers_organization_name", "organization_name"),
)
