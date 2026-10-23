"""Pytest configuration.

The test-suite never touches a developer's real database: a separate SQLite
file in the temporary directory is created and filled with the demo data.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# The DATABASE_URL has to be set before `app.db.base` creates the engine.
TEST_DB_PATH = Path(tempfile.gettempdir()) / "eventease_test_suite.db"
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ.pop("AUTO_INIT_DB", None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db.base import SessionLocal, engine  # noqa: E402
from app.db.init_db import init_database  # noqa: E402
from app.main import app  # noqa: E402
from app.models import metadata  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def prepared_database() -> None:
    """Create an isolated test database with the demo data."""
    metadata.drop_all(engine)
    init_database(engine, seed=True)
    yield
    metadata.drop_all(engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture()
def db_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
