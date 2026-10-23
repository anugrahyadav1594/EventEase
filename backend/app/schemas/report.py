"""Response schemas for the report / SQL Lab endpoints."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryMeta(BaseModel):
    """Everything the SQL Lab needs to prove that the SQL really ran."""

    title: str
    concept: str
    explanation: str
    sql: str
    dialect: str
    row_count: int = 0
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class LabStepResult(BaseModel):
    label: str
    sql: str
    status: str = "ok"  # ok | error
    message: str | None = None
    row_count: int = 0
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)


class LabExperiment(BaseModel):
    key: str
    number: int
    title: str
    concept: str
    description: str
    sql: str
    dialect: str
    notes: list[str] = Field(default_factory=list)
    statements: list[LabStepResult] = Field(default_factory=list)
    error: str | None = None
