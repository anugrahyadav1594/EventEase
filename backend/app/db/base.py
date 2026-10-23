"""Database engine / session management."""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from .compat import register_sqlite_functions

connect_args: dict = {}
engine_kwargs: dict = {"echo": settings.sql_echo, "future": True}

if settings.is_sqlite:
    # SQLite needs this for the FastAPI thread pool and for the test-suite.
    connect_args["check_same_thread"] = False
    engine_kwargs["pool_pre_ping"] = False
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = settings.db_pool_size
    engine_kwargs["pool_max_overflow"] = settings.db_max_overflow
    engine_kwargs["pool_recycle"] = 3600

engine: Engine = create_engine(settings.database_url, connect_args=connect_args, **engine_kwargs)


if settings.is_sqlite:

    @event.listens_for(engine, "connect")
    def _on_sqlite_connect(dbapi_connection, _connection_record):  # pragma: no cover - trivial
        register_sqlite_functions(dbapi_connection)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def dialect_name() -> str:
    return engine.dialect.name


def version_sql(dialect: str) -> str:
    """The statement that returns the server version for a given dialect."""
    return "SELECT sqlite_version()" if dialect == "sqlite" else "SELECT VERSION()"


def server_version(connection=None) -> str:
    """Return the raw server version string (e.g. ``8.0.36``)."""
    if connection is not None:
        return str(connection.execute(text(version_sql(connection.dialect.name))).scalar() or "")
    with engine.connect() as conn:
        return str(conn.execute(text(version_sql(conn.dialect.name))).scalar() or "")


def supports_intersect() -> bool:
    """MySQL only supports INTERSECT / EXCEPT from 8.0.31 onwards.

    SQLite has supported both operators for a long time, therefore the SQL Lab
    can always run the native set operations on the development fallback.
    """
    name = dialect_name()
    if name == "sqlite":
        return True
    if name != "mysql":
        return False
    version = server_version()
    try:
        parts = [int(p) for p in version.split("-")[0].split(".")[:3]]
    except ValueError:  # pragma: no cover - unexpected server banner
        return False
    major, minor, patch = (parts + [0, 0, 0])[:3]
    return (major, minor, patch) >= (8, 0, 31)
