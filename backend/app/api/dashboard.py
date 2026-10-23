"""Dashboard endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..services.dashboard import build_dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(session: Session = Depends(get_db)) -> dict:
    """Live metrics, charts and the upcoming schedule."""
    return build_dashboard(session)
