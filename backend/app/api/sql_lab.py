"""SQL Lab - runs the nine predefined DBMS experiments.

The endpoint never accepts SQL from the client.  It only accepts the key of
one of the nine experiments (and optional numeric thresholds), so no
destructive statement can ever be executed from the frontend.
"""
from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException, Query, status

from ..services.sql_lab import list_experiments, run_experiment

router = APIRouter(prefix="/sql-lab", tags=["sql-lab"])


@router.get("/experiments")
def experiments():
    """List the nine experiments with their concept and description."""
    return list_experiments()


@router.post("/experiments/{key}/run")
def run(
    key: str,
    params: dict | None = Body(default=None),
    prefer_native: bool = Query(default=True),
):
    """Execute one predefined experiment against the live database."""
    try:
        return run_experiment(key, params=params or {}, prefer_native=prefer_native)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown experiment '{key}'.")
