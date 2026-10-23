"""SQL views used by the application.

The views are written in ANSI SQL so that they can be created on MySQL 8 and
on the SQLite development fallback.  `database/views.sql` is generated from
this module (see `backend/scripts/generate_sql.py`) which guarantees that the
SQL script and the running application always use the same definitions.
"""
from __future__ import annotations

VIEW_DEFINITIONS: list[tuple[str, str]] = [
    (
        "v_upcoming_events",
        """
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.event_date,
    e.start_time,
    e.end_time,
    e.capacity,
    e.ticket_price,
    e.event_status,
    o.organizer_name,
    o.organization_name,
    v.venue_name,
    v.location AS venue_location,
    (SELECT COUNT(*)
       FROM registrations r
      WHERE r.event_id = e.event_id
        AND r.registration_status <> 'Cancelled')            AS active_registrations,
    e.capacity - (SELECT COUNT(*)
                     FROM registrations r
                    WHERE r.event_id = e.event_id
                      AND r.registration_status <> 'Cancelled') AS seats_available
FROM events e
JOIN organizers o ON o.organizer_id = e.organizer_id
JOIN venues v     ON v.venue_id     = e.venue_id
WHERE e.event_date >= CURRENT_DATE
  AND e.event_status <> 'Cancelled'
""",
    ),
    (
        "v_event_registration_summary",
        """
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.event_date,
    e.event_status,
    e.capacity,
    COUNT(DISTINCT r.registration_id) AS total_registrations,
    SUM(CASE WHEN r.registration_status = 'Registered'  THEN 1 ELSE 0 END) AS registered_registrations,
    SUM(CASE WHEN r.registration_status = 'Confirmed'  THEN 1 ELSE 0 END) AS confirmed_registrations,
    SUM(CASE WHEN r.registration_status = 'Cancelled'  THEN 1 ELSE 0 END) AS cancelled_registrations,
    SUM(CASE WHEN r.registration_status = 'Waitlisted' THEN 1 ELSE 0 END) AS waitlisted_registrations,
    SUM(CASE WHEN r.attendance_status = 'Present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN r.attendance_status = 'Absent'  THEN 1 ELSE 0 END) AS absent_count,
    ROUND(COUNT(DISTINCT r.registration_id) * 100.0 / e.capacity, 2) AS fill_rate_percent
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name, e.event_category, e.event_date, e.event_status, e.capacity
""",
    ),
    (
        "v_event_revenue_summary",
        """
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.ticket_price,
    COUNT(DISTINCT r.registration_id) AS total_registrations,
    SUM(CASE WHEN r.registration_status <> 'Cancelled' THEN 1 ELSE 0 END) AS active_registrations,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END), 0) AS gross_revenue,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Refunded'  THEN p.amount ELSE 0 END), 0) AS refunded_amount,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Pending'   THEN p.amount ELSE 0 END), 0) AS pending_amount
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
LEFT JOIN payments p      ON p.registration_id = r.registration_id
GROUP BY e.event_id, e.event_name, e.event_category, e.ticket_price
""",
    ),
    (
        "v_venue_utilization",
        """
SELECT
    v.venue_id,
    v.venue_name,
    v.location,
    v.capacity,
    v.venue_type,
    v.availability_status,
    COUNT(DISTINCT e.event_id) AS events_hosted,
    COALESCE(SUM(e.capacity), 0) AS total_seats_offered,
    COUNT(DISTINCT r.registration_id) AS total_registrations,
    CASE
        WHEN COALESCE(SUM(e.capacity), 0) > 0
        THEN ROUND(COUNT(DISTINCT r.registration_id) * 100.0 / SUM(e.capacity), 2)
        ELSE 0
    END AS utilization_percent
FROM venues v
LEFT JOIN events e        ON e.venue_id = v.venue_id AND e.event_status <> 'Cancelled'
LEFT JOIN registrations r ON r.event_id = e.event_id  AND r.registration_status <> 'Cancelled'
GROUP BY v.venue_id, v.venue_name, v.location, v.capacity, v.venue_type, v.availability_status
""",
    ),
    (
        "v_attendee_registration_history",
        """
SELECT
    a.attendee_id,
    a.full_name,
    a.email,
    a.organization,
    COUNT(DISTINCT r.registration_id) AS total_registrations,
    COUNT(DISTINCT CASE WHEN r.attendance_status = 'Present' THEN r.event_id END) AS events_attended,
    COUNT(DISTINCT CASE WHEN r.registration_status = 'Cancelled' THEN r.registration_id END) AS cancelled_registrations,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END), 0) AS total_paid
FROM attendees a
LEFT JOIN registrations r ON r.attendee_id = a.attendee_id
LEFT JOIN payments p      ON p.registration_id = r.registration_id
GROUP BY a.attendee_id, a.full_name, a.email, a.organization
""",
    ),
]


def create_views(connection) -> None:
    """Create (or replace) every view of the schema.

    MySQL understands ``CREATE OR REPLACE VIEW``; SQLite needs the view to be
    dropped first, therefore the statement is chosen depending on the dialect.
    """
    from sqlalchemy import text

    dialect = connection.dialect.name
    for name, body in VIEW_DEFINITIONS:
        if dialect == "sqlite":
            connection.execute(text(f"DROP VIEW IF EXISTS {name}"))
            connection.execute(text(f"CREATE VIEW {name} AS {body.strip()}"))
        else:
            connection.execute(text(f"CREATE OR REPLACE VIEW {name} AS {body.strip()}"))
