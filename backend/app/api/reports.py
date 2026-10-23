"""Report endpoints - every report runs a predefined, read-only SQL query."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..services.reports import run_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def list_reports():
    """Overview of all available reports."""
    from ..queries.reports import REPORTS

    return [
        {
            "key": report.key,
            "title": report.title,
            "concept": report.concept,
            "description": report.description,
            "endpoint": f"/api/reports/{report.key}",
        }
        for report in REPORTS.values()
    ]


@router.get("/event-registrations")
def report_event_registrations(session: Session = Depends(get_db)):
    return run_report(session, "event-registrations")


@router.get("/event-revenue")
def report_event_revenue(session: Session = Depends(get_db)):
    return run_report(session, "event-revenue")


@router.get("/venue-utilization")
def report_venue_utilization(session: Session = Depends(get_db)):
    return run_report(session, "venue-utilization")


@router.get("/popular-events")
def report_popular_events(
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_db),
):
    return run_report(session, "popular-events", {"limit": limit})


@router.get("/attendee-history")
def report_attendee_history(session: Session = Depends(get_db)):
    return run_report(session, "attendee-history")


@router.get("/attendance-summary")
def report_attendance_summary(session: Session = Depends(get_db)):
    return run_report(session, "attendance-summary")


@router.get("/events-above-average")
def report_events_above_average(session: Session = Depends(get_db)):
    return run_report(session, "events-above-average")
