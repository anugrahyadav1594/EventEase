"""Initialise the EventEase database.

Usage (from the repository root):

    python backend/scripts/init_db.py            # create schema + views + demo data
    python backend/scripts/init_db.py --sql      # execute database/*.sql (MySQL)
    python backend/scripts/init_db.py --reset    # drop every table first

The script uses the DATABASE_URL from the environment / `.env` file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text  # noqa: E402

from app.db.base import engine  # noqa: E402
from app.db.init_db import init_database  # noqa: E402
from app.models import metadata  # noqa: E402

DATABASE_DIR = ROOT_DIR / "database"


def split_sql(script: str) -> list[str]:
    """Split a SQL script into single statements.

    The splitter understands single quotes, double quotes, backticks, line
    comments (`--`, `#`) and block comments (`/* ... */`).
    """
    statements: list[str] = []
    current: list[str] = []
    index = 0
    length = len(script)

    while index < length:
        char = script[index]

        if char in ("'", '"', "`"):
            quote = char
            current.append(char)
            index += 1
            while index < length:
                current.append(script[index])
                if script[index] == "\\" and index + 1 < length:
                    index += 1
                    current.append(script[index])
                elif script[index] == quote:
                    if index + 1 < length and script[index + 1] == quote:
                        current.append(script[index + 1])
                        index += 1
                    else:
                        index += 1
                    break
                index += 1
            continue

        if script.startswith("--", index) or char == "#":
            end = script.find("\n", index)
            index = length if end == -1 else end
            continue

        if script.startswith("/*", index):
            end = script.find("*/", index + 2)
            index = length if end == -1 else end + 2
            continue

        if char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            index += 1
            continue

        current.append(char)
        index += 1

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


def run_sql_scripts() -> None:
    """Execute database/schema.sql, database/seed.sql and database/views.sql."""
    files = ["schema.sql", "seed.sql", "views.sql"]
    for file_name in files:
        path = DATABASE_DIR / file_name
        if not path.exists():
            print(f"!! {path} not found - run backend/scripts/generate_sql.py first")
            continue
        script = path.read_text(encoding="utf-8")
        statements = split_sql(script)
        print(f"-> {file_name}: {len(statements)} statements")
        with engine.begin() as connection:
            for statement in statements:
                try:
                    connection.execute(text(statement))
                except Exception as exc:  # pragma: no cover - depends on the server
                    print(f"!! failed statement: {statement[:120]}\n   {exc}")
                    raise
    print("SQL scripts executed successfully.")


def reset_database() -> None:
    print("Dropping every table ...")
    metadata.drop_all(engine)
    print("Tables dropped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialise the EventEase database")
    parser.add_argument("--sql", action="store_true", help="execute database/*.sql instead of the Python bootstrap")
    parser.add_argument("--reset", action="store_true", help="drop all tables before the initialisation")
    parser.add_argument("--no-seed", action="store_true", help="only create the schema and the views")
    args = parser.parse_args()

    print(f"database url : {engine.url}")
    print(f"dialect      : {engine.dialect.name}")

    if args.reset:
        reset_database()

    if args.sql:
        run_sql_scripts()
        return

    result = init_database(seed=not args.no_seed)
    print("schema created:", result["created"])
    print("demo data inserted:", result["seeded"])
    print("row counts:", result["counts"])


if __name__ == "__main__":
    main()
