"""Health / readiness endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..db.base import get_db, version_sql
from ..services.helpers import jsonable_rows, rows_as_dicts

router = APIRouter(tags=["system"])


@router.get("/health")
def health(session: Session = Depends(get_db)) -> dict:
    """Basic liveness probe including a real round trip to the database."""
    counts: dict[str, int] = {}
    database_ok = True
    error: str | None = None
    try:
        rows = rows_as_dicts(
            session.execute(
                text(
                    """
                    SELECT
                        (SELECT COUNT(*) FROM organizers)    AS organizers,
                        (SELECT COUNT(*) FROM venues)        AS venues,
                        (SELECT COUNT(*) FROM events)        AS events,
                        (SELECT COUNT(*) FROM attendees)     AS attendees,
                        (SELECT COUNT(*) FROM registrations) AS registrations,
                        (SELECT COUNT(*) FROM payments)      AS payments
                    """
                )
            )
        )
        counts = {key: int(value or 0) for key, value in (rows[0] if rows else {}).items()}
    except Exception as exc:  # pragma: no cover - only when the DB is down
        database_ok = False
        error = str(exc)

    return {
        "status": "ok" if database_ok else "degraded",
        "service": "EventEase API",
        "database_connected": database_ok,
        "dialect": session.bind.dialect.name if session.bind is not None else None,
        "server_version": (
            session.execute(text(version_sql(session.bind.dialect.name))).scalar() if database_ok else None
        ),
        "row_counts": counts,
        "error": error,
    }
