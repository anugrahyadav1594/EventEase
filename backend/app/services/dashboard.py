"""Dashboard metrics - every number is calculated by the database."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from .helpers import jsonable_rows, rows_as_dicts

COUNTS_SQL = """
SELECT
    (SELECT COUNT(*) FROM organizers)                                      AS total_organizers,
    (SELECT COUNT(*) FROM venues)                                          AS total_venues,
    (SELECT COUNT(*) FROM events)                                          AS total_events,
    (SELECT COUNT(*) FROM events WHERE event_status = 'Upcoming')          AS upcoming_events,
    (SELECT COUNT(*) FROM events WHERE event_status = 'Ongoing')           AS ongoing_events,
    (SELECT COUNT(*) FROM events WHERE event_status = 'Completed')         AS completed_events,
    (SELECT COUNT(*) FROM events WHERE event_status = 'Cancelled')         AS cancelled_events,
    (SELECT COUNT(*) FROM attendees)                                       AS total_attendees,
    (SELECT COUNT(*) FROM registrations)                                   AS total_registrations,
    (SELECT COUNT(*) FROM registrations WHERE registration_status = 'Registered')  AS registered_registrations,
    (SELECT COUNT(*) FROM registrations WHERE registration_status = 'Confirmed')  AS confirmed_registrations,
    (SELECT COUNT(*) FROM registrations WHERE registration_status = 'Cancelled')  AS cancelled_registrations,
    (SELECT COUNT(*) FROM registrations WHERE registration_status = 'Waitlisted') AS waitlisted_registrations,
    (SELECT COUNT(*) FROM registrations WHERE attendance_status = 'Present')      AS present_count,
    (SELECT COUNT(*) FROM registrations WHERE attendance_status = 'Absent')       AS absent_count,
    (SELECT COUNT(*) FROM registrations WHERE attendance_status = 'Not Marked')  AS not_marked_count
"""

REVENUE_SQL = """
SELECT
    COALESCE(SUM(CASE WHEN payment_status = 'Completed' THEN amount ELSE 0 END), 0) AS collected_revenue,
    COALESCE(SUM(CASE WHEN payment_status = 'Pending'   THEN amount ELSE 0 END), 0) AS pending_amount,
    COALESCE(SUM(CASE WHEN payment_status = 'Refunded'  THEN amount ELSE 0 END), 0) AS refunded_amount,
    COUNT(*) AS payment_records
FROM payments
"""

REGISTRATIONS_BY_EVENT_SQL = """
SELECT
    event_id,
    event_name,
    event_category,
    total_registrations,
    confirmed_registrations,
    fill_rate_percent
FROM v_event_registration_summary
ORDER BY total_registrations DESC, event_name
LIMIT 8
"""

REVENUE_BY_CATEGORY_SQL = """
SELECT
    e.event_category,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END), 0) AS revenue,
    COUNT(DISTINCT e.event_id) AS event_count
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
LEFT JOIN payments p      ON p.registration_id = r.registration_id
GROUP BY e.event_category
ORDER BY revenue DESC
"""

ATTENDANCE_BY_EVENT_SQL = """
SELECT
    event_id,
    event_name,
    event_category,
    present_count,
    absent_count,
    total_registrations,
    fill_rate_percent
FROM v_event_registration_summary
WHERE present_count + absent_count > 0
ORDER BY present_count DESC, event_name
LIMIT 8
"""

VENUE_UTILIZATION_SQL = """
SELECT
    venue_id,
    venue_name,
    events_hosted,
    total_registrations,
    utilization_percent
FROM v_venue_utilization
ORDER BY utilization_percent DESC, venue_name
LIMIT 8
"""

POPULAR_EVENTS_SQL = """
SELECT
    s.event_id,
    s.event_name,
    s.event_category,
    s.event_date,
    s.total_registrations,
    s.confirmed_registrations,
    v.gross_revenue AS revenue
FROM v_event_registration_summary s
JOIN v_event_revenue_summary v ON v.event_id = s.event_id
ORDER BY s.total_registrations DESC, s.event_name
LIMIT 5
"""

UPCOMING_SCHEDULE_SQL = """
SELECT
    event_id,
    event_name,
    event_category,
    event_date,
    start_time,
    end_time,
    venue_name,
    organizer_name,
    capacity,
    active_registrations,
    seats_available,
    ticket_price
FROM v_upcoming_events
ORDER BY event_date, start_time
LIMIT 8
"""

CATEGORY_SPLIT_SQL = """
SELECT event_category, COUNT(*) AS event_count
FROM events
GROUP BY event_category
ORDER BY event_count DESC
"""


def _rows(session: Session, sql: str) -> list[dict[str, Any]]:
    return jsonable_rows(rows_as_dicts(session.execute(text(sql))))


def build_dashboard(session: Session) -> dict[str, Any]:
    counts = _rows(session, COUNTS_SQL)[0]
    revenue = _rows(session, REVENUE_SQL)[0]

    present = int(counts.get("present_count") or 0)
    absent = int(counts.get("absent_count") or 0)
    marked = present + absent
    attendance_rate = round(present * 100.0 / marked, 2) if marked else 0.0

    return {
        "metrics": {
            "total_organizers": int(counts.get("total_organizers") or 0),
            "total_venues": int(counts.get("total_venues") or 0),
            "total_events": int(counts.get("total_events") or 0),
            "upcoming_events": int(counts.get("upcoming_events") or 0),
            "ongoing_events": int(counts.get("ongoing_events") or 0),
            "completed_events": int(counts.get("completed_events") or 0),
            "cancelled_events": int(counts.get("cancelled_events") or 0),
            "total_attendees": int(counts.get("total_attendees") or 0),
            "total_registrations": int(counts.get("total_registrations") or 0),
            "registered_registrations": int(counts.get("registered_registrations") or 0),
            "confirmed_registrations": int(counts.get("confirmed_registrations") or 0),
            "cancelled_registrations": int(counts.get("cancelled_registrations") or 0),
            "waitlisted_registrations": int(counts.get("waitlisted_registrations") or 0),
            "present_count": present,
            "absent_count": absent,
            "not_marked_count": int(counts.get("not_marked_count") or 0),
            "average_attendance_rate": attendance_rate,
            "total_revenue": float(Decimal(str(revenue.get("collected_revenue") or 0))),
            "pending_amount": float(Decimal(str(revenue.get("pending_amount") or 0))),
            "refunded_amount": float(Decimal(str(revenue.get("refunded_amount") or 0))),
            "payment_records": int(revenue.get("payment_records") or 0),
        },
        "charts": {
            "registrations_by_event": _rows(session, REGISTRATIONS_BY_EVENT_SQL),
            "revenue_by_category": _rows(session, REVENUE_BY_CATEGORY_SQL),
            "attendance_by_event": _rows(session, ATTENDANCE_BY_EVENT_SQL),
            "venue_utilization": _rows(session, VENUE_UTILIZATION_SQL),
            "events_by_category": _rows(session, CATEGORY_SPLIT_SQL),
        },
        "popular_events": _rows(session, POPULAR_EVENTS_SQL),
        "upcoming_schedule": _rows(session, UPCOMING_SCHEDULE_SQL),
    }
