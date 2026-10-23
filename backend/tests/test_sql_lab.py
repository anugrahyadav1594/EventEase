"""The SQL Lab runs all nine experiments against the live database."""
from __future__ import annotations

import pytest

EXPERIMENT_KEYS = [
    "ddl-dml",
    "constraints",
    "set-operations",
    "string-functions",
    "aggregate-functions",
    "group-by-having",
    "nested-subqueries",
    "views",
    "joins",
]


def test_experiment_overview(client):
    response = client.get("/api/sql-lab/experiments")
    assert response.status_code == 200
    experiments = response.json()
    assert len(experiments) == 9
    assert [item["number"] for item in experiments] == list(range(1, 10))
    assert {item["key"] for item in experiments} == set(EXPERIMENT_KEYS)


@pytest.mark.parametrize("key", EXPERIMENT_KEYS)
def test_every_experiment_runs(client, key):
    response = client.post(f"/api/sql-lab/experiments/{key}/run", json={})
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["key"] == key
    assert payload["title"]
    assert payload["concept"]
    assert payload["statements"]

    for statement in payload["statements"]:
        assert statement["sql"].strip()
        assert statement["status"] in {"ok", "error"}
        if statement["status"] == "ok":
            assert statement["message"]


def test_unknown_experiment_returns_404(client):
    response = client.post("/api/sql-lab/experiments/not-an-experiment/run", json={})
    assert response.status_code == 404


def test_constraint_experiment_shows_database_errors(client):
    payload = client.post("/api/sql-lab/experiments/constraints/run", json={}).json()
    errors = [step for step in payload["statements"] if step["status"] == "error"]
    assert len(errors) >= 5
    messages = " ".join(step["message"].lower() for step in errors)
    assert "unique" in messages
    assert "not null" in messages or "null" in messages
    assert "check" in messages
    assert "foreign key" in messages


def test_ddl_experiment_removes_its_scratch_table(client):
    from sqlalchemy import text

    from app.db.base import engine

    client.post("/api/sql-lab/experiments/ddl-dml/run", json={})
    with engine.connect() as connection:
        exists = connection.execute(
            text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='eventease_demo_scratch'")
        ).scalar()
    assert exists == 0


def test_constraint_experiment_does_not_leave_rows_behind(client, db_session):
    from sqlalchemy import text

    client.post("/api/sql-lab/experiments/constraints/run", json={})
    demo_rows = db_session.execute(
        text("SELECT COUNT(*) FROM attendees WHERE email = 'lab.primarykey@eventease.edu'")
    ).scalar()
    assert demo_rows == 0


def test_set_operation_experiment_returns_rows(client):
    payload = client.post("/api/sql-lab/experiments/set-operations/run", json={}).json()
    union_step = payload["statements"][0]
    union_all_step = payload["statements"][1]
    assert union_step["row_count"] > 0
    # UNION removes duplicates, UNION ALL keeps them -> at least as many rows.
    assert union_all_step["row_count"] >= union_step["row_count"]


def test_view_experiment_reads_from_the_views(client):
    payload = client.post("/api/sql-lab/experiments/views/run", json={}).json()
    assert len(payload["statements"]) == 5
    for statement in payload["statements"]:
        assert statement["status"] == "ok"
        assert statement["row_count"] > 0
