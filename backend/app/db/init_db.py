"""Database initialisation helpers (schema + views + demo data)."""
from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

from ..models import metadata
from .base import engine as default_engine
from .seed import database_is_empty, seed_database
from .views import create_views


def create_schema(connection: Connection) -> None:
    """Create every table plus every view of the EventEase schema."""
    metadata.create_all(connection)
    create_views(connection)


def init_database(
    engine: Engine | None = None,
    *,
    seed: bool = True,
    reference: date | None = None,
) -> dict[str, Any]:
    """Create the schema (and optionally the demo data) in an idempotent way."""
    engine = engine or default_engine
    result: dict[str, Any] = {"created": False, "seeded": False, "counts": {}}

    with engine.begin() as connection:
        create_schema(connection)
        result["created"] = True
        if seed:
            if database_is_empty(connection):
                result["counts"] = seed_database(connection, reference=reference)
                result["seeded"] = True

    if not result["seeded"] and seed:
        with engine.connect() as connection:
            result["counts"] = {
                "organizers": connection.execute(text("SELECT COUNT(*) FROM organizers")).scalar(),
                "venues": connection.execute(text("SELECT COUNT(*) FROM venues")).scalar(),
                "events": connection.execute(text("SELECT COUNT(*) FROM events")).scalar(),
                "attendees": connection.execute(text("SELECT COUNT(*) FROM attendees")).scalar(),
                "registrations": connection.execute(text("SELECT COUNT(*) FROM registrations")).scalar(),
                "payments": connection.execute(text("SELECT COUNT(*) FROM payments")).scalar(),
            }

    return result
