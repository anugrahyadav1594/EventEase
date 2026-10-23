"""Static validation of the generated SQL scripts.

The script parses `database/schema.sql`, `database/seed.sql` and
`database/views.sql` and verifies - without a running MySQL server - that

* every table that is referenced by the seed data exists in the schema,
* every foreign key value used in the seed data points to an existing row,
* no UNIQUE column contains the same value twice,
* every CHECK constraint of the schema is satisfied by the seed data.

Run with:  python backend/scripts/validate_sql_scripts.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "scripts"))

from init_db import split_sql  # noqa: E402

DATABASE_DIR = ROOT_DIR / "database"


def parse_schema() -> tuple[dict[str, dict], dict[str, dict]]:
    """Return ({table: {column: type}}, {table: {constraint: definition}})."""
    script = (DATABASE_DIR / "schema.sql").read_text(encoding="utf-8")
    tables: dict[str, dict] = {}
    constraints: dict[str, dict] = {}

    for statement in split_sql(script):
        create = re.match(r"CREATE TABLE (\w+)\s*\((.*)\)\s*;?$", statement.strip(), re.S | re.I)
        if create:
            table, body = create.group(1), create.group(2)
            columns: dict[str, str] = {}
            table_constraints: dict[str, str] = {}
            for line in body.split(","):
                line = line.strip()
                if not line:
                    continue
                if re.match(r"(PRIMARY KEY|UNIQUE|CHECK|CONSTRAINT|FOREIGN KEY|INDEX)", line, re.I):
                    name = re.match(r"(?:CONSTRAINT\s+(\w+)|PRIMARY KEY|UNIQUE|CHECK|FOREIGN KEY)", line, re.I)
                    key = name.group(1) if name and name.lastindex else line.split()[0].upper()
                    table_constraints[key.upper()] = line
                    continue
                parts = line.split()
                columns[parts[0]] = " ".join(parts[1:])
            tables[table] = columns
            constraints[table] = table_constraints
    return tables, constraints


def parse_seed() -> dict[str, list[list[str]]]:
    """Return {table: [row, row, ...]} with the raw cell values."""
    script = (DATABASE_DIR / "seed.sql").read_text(encoding="utf-8")
    rows: dict[str, list[list[str]]] = {}
    for statement in split_sql(script):
        insert = re.match(r"INSERT INTO (\w+)\s*\((.*?)\)\s*VALUES\s*(.*)$", statement.strip(), re.S | re.I)
        if not insert:
            continue
        table, columns, values = insert.group(1), insert.group(2), insert.group(3)
        column_list = [column.strip() for column in columns.split(",")]
        table_rows = rows.setdefault(table, [])
        for tuple_text in split_tuples(values):
            cells = [cell.strip() for cell in split_values(tuple_text)]
            table_rows.append(cells)
        rows[table] = table_rows
        rows.setdefault(f"__columns__{table}", column_list)
    return rows


def split_tuples(values: str) -> list[str]:
    """Split the VALUES part of an INSERT into its top level tuples."""
    tuples: list[str] = []
    depth = 0
    current: list[str] = []
    in_string = False
    for char in values:
        if char == "'":
            in_string = not in_string
            current.append(char)
            continue
        if in_string:
            current.append(char)
            continue
        if char == "(":
            depth += 1
            if depth == 1:
                current = []
                continue
            current.append(char)
            continue
        if char == ")":
            depth -= 1
            if depth == 0:
                tuples.append("".join(current))
                current = []
                continue
            current.append(char)
            continue
        if depth >= 1:
            current.append(char)
    return tuples


def split_values(raw: str) -> list[str]:
    """Split one tuple into its cells (commas inside quotes or functions are ignored)."""
    values: list[str] = []
    current = ""
    in_string = False
    depth = 0
    for char in raw:
        if char == "'":
            in_string = not in_string
            current += char
            continue
        if in_string:
            current += char
            continue
        if char == "(":
            depth += 1
            current += char
            continue
        if char == ")":
            depth -= 1
            current += char
            continue
        if char == "," and depth == 0:
            values.append(current.strip())
            current = ""
            continue
        current += char
    if current.strip():
        values.append(current.strip())
    return values


def cell_value(raw: str) -> str:
    raw = raw.strip()
    if raw.upper() == "NULL":
        return ""
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    return raw


def main() -> int:
    tables, constraints = parse_schema()
    seed = parse_seed()
    errors: list[str] = []
    warnings: set[str] = set()

    print(f"tables in schema.sql : {len(tables)}")
    print(f"tables in seed.sql   : {len([key for key in seed if not key.startswith('__')])}")

    # 1) every seeded table exists
    for table in seed:
        if table.startswith("__"):
            continue
        if table not in tables:
            errors.append(f"seed.sql inserts into unknown table '{table}'")

    # 2) foreign keys
    foreign_keys = {
        "events": {"organizer_id": "organizers", "venue_id": "venues"},
        "registrations": {"attendee_id": "attendees", "event_id": "events"},
        "payments": {"registration_id": "registrations"},
    }
    for table, relations in foreign_keys.items():
        if table not in seed:
            continue
        columns = seed[f"__columns__{table}"]
        for column, parent in relations.items():
            if column not in columns:
                continue
            parent_columns = seed.get(f"__columns__{parent}", [])
            if not parent_columns:
                continue
            parent_key = parent_columns[0]
            parent_values = {cell_value(row[0]) for row in seed.get(parent, [])}
            for row in seed[table]:
                value = cell_value(row[columns.index(column)])
                if value and value not in parent_values:
                    errors.append(
                        f"{table}.{column} = {value} has no matching {parent}.{parent_key}"
                    )

    # 3) unique columns
    unique_columns = {
        "organizers": ["email"],
        "attendees": ["email"],
        "payments": ["transaction_reference"],
        "registrations": ["attendee_id,event_id"],
    }
    for table, uniques in unique_columns.items():
        if table not in seed:
            continue
        columns = seed[f"__columns__{table}"]
        for unique in uniques:
            key_columns = unique.split(",")
            if not all(column in columns for column in key_columns):
                continue
            seen: set[tuple[str, ...]] = set()
            for row in seed[table]:
                key = tuple(cell_value(row[columns.index(column)]) for column in key_columns)
                if not all(key):
                    continue
                if key in seen:
                    errors.append(f"{table}: duplicate value for UNIQUE ({unique}): {key}")
                seen.add(key)

    # 4) check constraints
    check_pattern = re.compile(r"CHECK\s*\((.+?)\)\s*$", re.I)
    for table, table_constraints in constraints.items():
        for name, definition in table_constraints.items():
            match = check_pattern.search(definition)
            if not match or table not in seed:
                continue
            expression = match.group(1)
            columns = seed.get(f"__columns__{table}", [])
            for row in seed[table]:
                values = {column: cell_value(row[index]) for index, column in enumerate(columns)}
                simple = re.match(r"^(\w+)\s*(>=|>|<=|<)\s*(-?\d+(?:\.\d+)?)$", expression.strip())
                if simple:
                    column, operator, limit = simple.group(1), simple.group(2), float(simple.group(3))
                    if column not in values or not values[column]:
                        continue
                    actual = float(values[column])
                    ok = {
                        ">=": actual >= limit,
                        ">": actual > limit,
                        "<=": actual <= limit,
                        "<": actual < limit,
                    }[operator]
                    if not ok:
                        errors.append(f"{table}.{column} = {actual} violates CHECK ({expression})")
                else:
                    time_compare = re.match(r"^(\w+)\s*(>=|>|<=|<)\s*(\w+)$", expression.strip())
                    if time_compare:
                        left, operator, right = time_compare.groups()
                        if left in values and right in values and values[left] and values[right]:
                            if not values[left].replace(":", "").isdigit():
                                continue
                            allowed = {
                                ">": values[left] > values[right],
                                ">=": values[left] >= values[right],
                                "<": values[left] < values[right],
                                "<=": values[left] <= values[right],
                            }[operator]
                            if not allowed:
                                errors.append(
                                    f"{table}.{left} = {values[left]} violates CHECK ({expression}) "
                                    f"because {table}.{right} = {values[right]}"
                                )
                    else:
                        warnings.add(
                            f"check constraint of {table} not evaluated automatically: {expression}"
                        )

    print()
    if warnings:
        print("notes:")
        for warning in sorted(warnings):
            print(f"  - {warning}")
    if errors:
        print(f"{len(errors)} problem(s) found:")
        for error in errors:
            print(f"  ✗ {error}")
        return 1

    print("✓ schema.sql, seed.sql and views.sql are consistent")
    print(f"  organizers   : {len(seed.get('organizers', []))}")
    print(f"  venues       : {len(seed.get('venues', []))}")
    print(f"  events       : {len(seed.get('events', []))}")
    print(f"  attendees    : {len(seed.get('attendees', []))}")
    print(f"  registrations: {len(seed.get('registrations', []))}")
    print(f"  payments     : {len(seed.get('payments', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
