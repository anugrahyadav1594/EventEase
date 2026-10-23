"""Small compatibility layer for the SQLite development fallback.

EventEase targets MySQL 8.0.  Because MySQL cannot be installed in every
sandbox/CI machine the project also supports a SQLite URL, which is used for
the automated test-suite and for a zero-setup demo run.

SQLite is *not* a drop-in replacement for MySQL, so the handful of MySQL
functions used by the SQL Lab are registered as user defined functions here:

* ``concat(...)``              -> MySQL CONCAT()
* ``char_length(...)``         -> MySQL CHAR_LENGTH()
* ``ifnull(a, b)``             -> MySQL IFNULL()

Everything else in the project uses ANSI SQL that both engines understand.
"""
from __future__ import annotations

import sqlite3
from typing import Any


def _concat(*args: Any) -> Any:
    """MySQL style CONCAT(): NULL propagates, otherwise the values are glued."""
    if any(arg is None for arg in args):
        return None
    return "".join(str(arg) for arg in args)


def _char_length(value: Any) -> Any:
    """MySQL style CHAR_LENGTH(): number of characters (not bytes)."""
    if value is None:
        return None
    return len(str(value))


def _ifnull(value: Any, fallback: Any) -> Any:
    """MySQL style IFNULL()."""
    return fallback if value is None else value


def register_sqlite_functions(dbapi_connection: sqlite3.Connection) -> None:
    """Prepare a raw SQLite connection so that it behaves like MySQL.

    * the MySQL compatibility functions are registered,
    * foreign key enforcement is switched on (SQLite disables it by default),
    * the foreign keys of the schema are not deferred.
    """
    dbapi_connection.create_function("concat", -1, _concat, deterministic=True)
    dbapi_connection.create_function("char_length", 1, _char_length, deterministic=True)
    dbapi_connection.create_function("ifnull", 2, _ifnull, deterministic=True)
    dbapi_connection.execute("PRAGMA foreign_keys=ON")

