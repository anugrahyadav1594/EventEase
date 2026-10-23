"""Small helpers shared by the API routers."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from collections.abc import Iterable
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import Result, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import Select

# MySQL / SQLite error codes that we can translate into friendly messages.
MYSQL_DUPLICATE = 1062
MYSQL_FOREIGN_KEY = 1452
MYSQL_ROW_REFERENCED = 1451
MYSQL_CHECK_VIOLATION = 3819


def rows_as_dicts(result: Result | Iterable[Any]) -> list[dict[str, Any]]:
    """Convert a SQLAlchemy result (or a list of rows) into dictionaries."""
    rows = result.fetchall() if hasattr(result, "fetchall") else list(result)
    return [dict(row._mapping) for row in rows]


def jsonable(value: Any) -> Any:
    """Make a database value JSON serialisable."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat(sep="T", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return value


def jsonable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: jsonable(value) for key, value in row.items()} for row in rows]


def count_query(statement: Select) -> Select:
    """Wrap a SELECT in a COUNT(*) sub-query (portable between MySQL & SQLite)."""
    return select(func.count()).select_from(statement.subquery())


def apply_pagination(statement: Select, session, page: int = 1, page_size: int = 20) -> dict[str, Any]:
    """Execute a statement with pagination and return a standard envelope."""
    page = max(1, page)
    page_size = max(1, min(page_size, 200))
    total = session.execute(count_query(statement)).scalar() or 0
    rows = rows_as_dicts(session.execute(statement.limit(page_size).offset((page - 1) * page_size)))
    return {
        "items": jsonable_rows(rows),
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "pages": max(1, -(-int(total) // page_size)),
    }


def integrity_error(exc: IntegrityError, *, entity: str = "record") -> HTTPException:
    """Translate a database integrity error into a readable API error."""
    original = getattr(exc, "orig", exc)
    args = getattr(original, "args", ())
    code = args[0] if args and isinstance(args[0], int) else None
    message = str(original)

    if code == MYSQL_DUPLICATE or "UNIQUE constraint failed" in message or "Duplicate entry" in message:
        detail = f"A {entity} with the same unique value already exists."
        code_out = status.HTTP_409_CONFLICT
    elif code == MYSQL_FOREIGN_KEY or "FOREIGN KEY constraint failed" in message:
        detail = "A referenced record does not exist (invalid foreign key)."
        code_out = status.HTTP_409_CONFLICT
    elif code == MYSQL_ROW_REFERENCED or "is still referenced" in message:
        detail = f"This {entity} is still referenced by other records and cannot be deleted."
        code_out = status.HTTP_409_CONFLICT
    elif code == MYSQL_CHECK_VIOLATION or "CHECK constraint failed" in message:
        detail = "A CHECK constraint rejected the values supplied to the database."
        code_out = status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        detail = f"The database rejected the {entity}: {message}"
        code_out = status.HTTP_400_BAD_REQUEST

    return HTTPException(status_code=code_out, detail=detail)
