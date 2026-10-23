"""Execution of the report queries (read-only SQL)."""
from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..queries.reports import REPORTS
from .helpers import jsonable_rows, rows_as_dicts


def available_reports() -> list[str]:
    return list(REPORTS.keys())


def run_report(session: Session, key: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute one predefined report and return metadata + rows."""
    report = REPORTS.get(key)
    if report is None:
        raise KeyError(key)

    bind_params = dict(report.params)
    bind_params.update({k: v for k, v in (params or {}).items() if v is not None})

    result = session.execute(text(report.sql), bind_params)
    rows = jsonable_rows(rows_as_dicts(result))
    columns = list(result.keys())

    return {
        "key": report.key,
        "title": report.title,
        "concept": report.concept,
        "description": report.description,
        "explanation": report.explanation,
        "sql": report.sql.strip(),
        "params": bind_params,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
    }
