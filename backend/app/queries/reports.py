"""Readable SQL behind the `/api/reports/*` endpoints.

Every report is a single, self contained SQL statement.  The exact SQL string
is sent to the frontend together with the result set so that the SQL Lab can
prove which query produced the numbers.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReportQuery:
    key: str
    title: str
    concept: str
    description: str
    sql: str
    explanation: str
    params: dict = field(default_factory=dict)


REPORTS: dict[str, ReportQuery] = {
    "event-registrations": ReportQuery(
        key="event-registrations",
        title="Registrations per event",
        concept="LEFT JOIN + GROUP BY + aggregate functions",
        description=(
            "Every event with the number of registrations it received, split by status, "
            "together with the fill rate against the event capacity."
        ),
        sql="""
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.event_date,
    e.event_status,
    e.capacity,
    COUNT(DISTINCT r.registration_id)                        AS total_registrations,
    SUM(CASE WHEN r.registration_status = 'Registered'  THEN 1 ELSE 0 END) AS registered_registrations,
    SUM(CASE WHEN r.registration_status = 'Confirmed'  THEN 1 ELSE 0 END) AS confirmed_registrations,
    SUM(CASE WHEN r.registration_status = 'Cancelled'  THEN 1 ELSE 0 END) AS cancelled_registrations,
    SUM(CASE WHEN r.registration_status = 'Waitlisted' THEN 1 ELSE 0 END) AS waitlisted_registrations,
    SUM(CASE WHEN r.attendance_status = 'Present' THEN 1 ELSE 0 END)       AS present_count,
    ROUND(COUNT(DISTINCT r.registration_id) * 100.0 / e.capacity, 2)        AS fill_rate_percent
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name, e.event_category, e.event_date, e.event_status, e.capacity
ORDER BY total_registrations DESC, e.event_date DESC
""",
        explanation=(
            "The LEFT JOIN keeps events without any registration in the result - that is exactly "
            "why the query starts with the events table. GROUP BY folds the registration rows into "
            "one row per event and the CASE expressions split the total into registration states."
        ),
    ),
    "event-revenue": ReportQuery(
        key="event-revenue",
        title="Revenue per event",
        concept="Multi-table JOIN + SUM + CASE + revenue rules",
        description=(
            "Gross, refunded, pending and net revenue for every event. Only payments in the "
            "'Completed' state are counted as collected money, refunded payments are never counted twice."
        ),
        sql="""
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.ticket_price,
    COUNT(DISTINCT r.registration_id) AS total_registrations,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END), 0) AS gross_revenue,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Refunded'  THEN p.amount ELSE 0 END), 0) AS refunded_amount,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Pending'   THEN p.amount ELSE 0 END), 0) AS pending_amount,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END), 0)
      - COALESCE(SUM(CASE WHEN p.payment_status = 'Refunded' THEN p.amount ELSE 0 END), 0) AS net_revenue
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
LEFT JOIN payments p      ON p.registration_id = r.registration_id
GROUP BY e.event_id, e.event_name, e.event_category, e.ticket_price
ORDER BY net_revenue DESC
""",
        explanation=(
            "The query joins three tables (events -> registrations -> payments). Because a payment "
            "only counts once, revenue uses SUM(CASE WHEN payment_status = 'Completed' ...). "
            "Net revenue subtracts the refunded amount, so a refunded ticket is never counted twice."
        ),
    ),
    "venue-utilization": ReportQuery(
        key="venue-utilization",
        title="Venue utilisation",
        concept="LEFT JOIN + GROUP BY + calculated utilisation percentage",
        description="How intensively every venue is used: events hosted, seats offered and registrations.",
        sql="""
SELECT
    v.venue_id,
    v.venue_name,
    v.location,
    v.capacity,
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
GROUP BY v.venue_id, v.venue_name, v.location, v.capacity, v.availability_status
ORDER BY utilization_percent DESC
""",
        explanation=(
            "A venue with no events still appears in the list (LEFT JOIN). Cancelled events are "
            "excluded in the JOIN condition so that they do not distort the utilisation figure."
        ),
    ),
    "popular-events": ReportQuery(
        key="popular-events",
        title="Most popular events",
        concept="JOIN + GROUP BY + ORDER BY + LIMIT (top-N query)",
        description="The events with the highest number of registrations, ranked by popularity.",
        sql="""
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.event_date,
    e.capacity,
    COUNT(DISTINCT r.registration_id) AS registration_count,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END), 0) AS revenue
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
LEFT JOIN payments p      ON p.registration_id = r.registration_id
WHERE e.event_status <> 'Cancelled'
GROUP BY e.event_id, e.event_name, e.event_category, e.event_date, e.capacity
ORDER BY registration_count DESC, revenue DESC
LIMIT :limit
""",
        explanation=(
            "The classic 'top N' query: group by event, count the registrations, order the result and "
            "cut it with LIMIT. The limit is passed as a bound parameter - the SQL is never built by "
            "concatenating user input."
        ),
        params={"limit": 10},
    ),
    "attendee-history": ReportQuery(
        key="attendee-history",
        title="Attendee registration history",
        concept="GROUP BY with conditional aggregation across three tables",
        description="How many events every attendee registered for, how many they attended and how much they paid.",
        sql="""
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
ORDER BY total_registrations DESC, a.full_name
""",
        explanation=(
            "Conditional aggregation: COUNT(DISTINCT CASE WHEN ... THEN ... END) counts only the rows "
            "that match the condition, while the LEFT JOINs keep attendees without registrations."
        ),
    ),
    "attendance-summary": ReportQuery(
        key="attendance-summary",
        title="Attendance summary per completed event",
        concept="CASE inside SUM + calculated attendance rate",
        description="Present / absent / not marked counts and the attendance rate for every finished event.",
        sql="""
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.event_date,
    SUM(CASE WHEN r.attendance_status = 'Present'   THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN r.attendance_status = 'Absent'    THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN r.attendance_status = 'Not Marked' THEN 1 ELSE 0 END) AS not_marked_count,
    COUNT(DISTINCT r.registration_id) AS total_registrations,
    CASE
        WHEN SUM(CASE WHEN r.attendance_status IN ('Present', 'Absent') THEN 1 ELSE 0 END) > 0
        THEN ROUND(SUM(CASE WHEN r.attendance_status = 'Present' THEN 1 ELSE 0 END) * 100.0 /
                   SUM(CASE WHEN r.attendance_status IN ('Present', 'Absent') THEN 1 ELSE 0 END), 2)
        ELSE 0
    END AS attendance_rate
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
WHERE e.event_status = 'Completed'
GROUP BY e.event_id, e.event_name, e.event_category, e.event_date
ORDER BY attendance_rate DESC
""",
        explanation=(
            "The attendance rate only divides by the registrations whose attendance was actually "
            "marked, otherwise events that never started would show a misleading 0 %."
        ),
    ),
    "events-above-average": ReportQuery(
        key="events-above-average",
        title="Events above the average registration count",
        concept="Nested subquery in the HAVING clause",
        description="Events that received more registrations than the average event of the whole system.",
        sql="""
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.event_date,
    COUNT(r.registration_id) AS registration_count,
    (SELECT AVG(event_registrations.total_registrations)
       FROM (SELECT COUNT(r2.registration_id) AS total_registrations
               FROM registrations r2
              GROUP BY r2.event_id) AS event_registrations) AS average_registrations
FROM events e
JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name, e.event_category, e.event_date
HAVING COUNT(r.registration_id) > (
    SELECT AVG(event_registrations.total_registrations)
      FROM (SELECT COUNT(r3.registration_id) AS total_registrations
              FROM registrations r3
             GROUP BY r3.event_id) AS event_registrations
)
ORDER BY registration_count DESC
""",
        explanation=(
            "The inner query calculates the registrations of every single event, the middle query "
            "averages them and the outer query keeps only the events that are above that average. "
            "The derived table needs an alias in MySQL."
        ),
    ),
}
