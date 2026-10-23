"""Runner for the nine DBMS experiments (predefined statements only)."""
from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from ..db.base import engine as default_engine, supports_intersect
from ..db.views import create_views
from ..queries.sql_lab import EXPERIMENTS, EXPERIMENTS_BY_KEY, LabExperiment, LabStatement
from .helpers import jsonable_rows, rows_as_dicts

CLEANUP_SQL = "DROP TABLE IF EXISTS eventease_demo_scratch"


def list_experiments() -> list[dict[str, Any]]:
    return [
        {
            "key": experiment.key,
            "number": experiment.number,
            "title": experiment.title,
            "concept": experiment.concept,
            "description": experiment.description,
            "statement_count": len(experiment.statements),
            "notes": experiment.notes,
            "defaults": experiment.defaults,
        }
        for experiment in EXPERIMENTS
    ]


def _execute(connection, statement: LabStatement, params: dict[str, Any]) -> dict[str, Any]:
    step: dict[str, Any] = {
        "label": statement.label,
        "sql": statement.sql.strip(),
        "status": "ok",
        "message": None,
        "row_count": 0,
        "columns": [],
        "rows": [],
        "note": statement.note,
    }
    try:
        result = connection.execute(text(statement.sql), params)
        if statement.expect == "none" or not result.returns_rows:
            step["message"] = "Statement executed successfully."
        else:
            step["columns"] = list(result.keys())
            step["rows"] = jsonable_rows(rows_as_dicts(result))
            step["row_count"] = len(step["rows"])
            step["message"] = f"{step['row_count']} row(s) returned."
    except SQLAlchemyError as exc:  # the database refused the statement
        original = getattr(exc, "orig", exc)
        step["status"] = "error"
        step["message"] = str(original)
    return step


def run_experiment(
    key: str,
    *,
    params: dict[str, Any] | None = None,
    engine: Engine | None = None,
    prefer_native: bool = True,
) -> dict[str, Any]:
    """Run one predefined experiment and return every intermediate result."""
    experiment: LabExperiment | None = EXPERIMENTS_BY_KEY.get(key)
    if experiment is None:
        raise KeyError(key)

    engine = engine or default_engine
    # Only the parameters that the experiment declares are accepted - the
    # client can never inject anything into the SQL text.
    bind_params: dict[str, Any] = dict(experiment.defaults)
    for key_name, value in (params or {}).items():
        if key_name in experiment.defaults and value is not None:
            try:
                bind_params[key_name] = int(value)
            except (TypeError, ValueError):
                continue

    steps: list[dict[str, Any]] = []
    notes = list(experiment.notes)

    with engine.connect() as connection:
        # The views must exist before experiment 8 can read from them.
        try:
            create_views(connection)
            if connection.in_transaction():
                connection.commit()
        except SQLAlchemyError:  # pragma: no cover - defensive
            if connection.in_transaction():
                connection.rollback()

        def execute_steps() -> list[dict[str, Any]]:
            collected: list[dict[str, Any]] = []
            for statement in experiment.statements:
                sql = statement.sql
                if statement.native_sql and prefer_native:
                    if supports_intersect():
                        sql = statement.native_sql
                        notes.append(
                            "Native set operator executed - the connected server supports "
                            f"INTERSECT / EXCEPT ({engine.dialect.name})."
                        )
                    else:
                        notes.append(
                            "The connected server (MySQL < 8.0.31) does not support INTERSECT / EXCEPT "
                            "natively, therefore the equivalent EXISTS / NOT EXISTS query was executed."
                        )
                collected.append(_execute(connection, _with_sql(statement, sql), bind_params))
            return collected

        if experiment.transactional:
            # Everything happens inside a transaction that is rolled back at the
            # end - the demo rows never reach the database.
            transaction = connection.begin()
            try:
                steps = execute_steps()
            finally:
                try:
                    transaction.rollback()
                except Exception:  # pragma: no cover - transaction already closed
                    if connection.in_transaction():
                        connection.rollback()
        else:
            steps = execute_steps()
            if connection.in_transaction():
                connection.commit()
            # The disposable table must never survive the demonstration.
            try:
                connection.execute(text(CLEANUP_SQL))
                if connection.in_transaction():
                    connection.commit()
            except SQLAlchemyError:  # pragma: no cover - defensive
                if connection.in_transaction():
                    connection.rollback()

    # remove duplicated notes while keeping the order
    notes = list(dict.fromkeys(notes))

    return {
        "key": experiment.key,
        "number": experiment.number,
        "title": experiment.title,
        "concept": experiment.concept,
        "description": experiment.description,
        "sql": "\n\n".join(statement.sql.strip() for statement in experiment.statements),
        "dialect": engine.dialect.name,
        "notes": notes,
        "params": bind_params,
        "statements": steps,
    }


def _with_sql(statement: LabStatement, sql: str) -> LabStatement:
    if sql == statement.sql:
        return statement
    return LabStatement(
        label=statement.label,
        sql=sql,
        expect=statement.expect,
        note=statement.note,
        native_sql=statement.native_sql,
        cleanup=statement.cleanup,
    )
