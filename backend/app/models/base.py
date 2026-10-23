"""Shared SQLAlchemy metadata for the EventEase schema.

The project uses SQLAlchemy 2.x *Core* table definitions (instead of the ORM)
so that every query stays explicit and readable for a DBMS practical exam.
"""
from __future__ import annotations

from sqlalchemy import MetaData

metadata = MetaData()
