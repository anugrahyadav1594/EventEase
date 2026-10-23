-- ==================================================================
-- Experiment 9: INNER JOIN, LEFT JOIN, multi-table joins and self joins
-- DBMS concept: INNER JOIN / LEFT JOIN / multi table joins / self joins
-- ==================================================================
--
-- How the six tables of the schema are connected with each other.
--
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. INNER JOIN - events with their organizer and venue
--    Only rows that exist on both sides are returned.
-- --------------------------------------------------------------------
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    e.event_date,
    o.organizer_name,
    o.organization_name,
    v.venue_name,
    v.location AS venue_location
FROM events e
INNER JOIN organizers o ON o.organizer_id = e.organizer_id
INNER JOIN venues v     ON v.venue_id     = e.venue_id
ORDER BY e.event_date, e.event_id;

-- --------------------------------------------------------------------
-- 2. LEFT JOIN - events without any registration
--    The LEFT JOIN keeps the events without registrations - exactly the rows an INNER JOIN would drop.
-- --------------------------------------------------------------------
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    COUNT(r.registration_id) AS registration_count
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name, e.event_category
HAVING COUNT(r.registration_id) = 0
ORDER BY e.event_name;

-- --------------------------------------------------------------------
-- 3. Multi table JOIN - registrations with attendee and event
--    Three tables connected in one query.
-- --------------------------------------------------------------------
SELECT
    r.registration_id,
    a.full_name,
    a.email,
    e.event_name,
    e.event_category,
    r.registration_status,
    r.attendance_status,
    r.ticket_type,
    r.ticket_price
FROM registrations r
INNER JOIN attendees a ON a.attendee_id = r.attendee_id
INNER JOIN events e   ON e.event_id   = r.event_id
ORDER BY r.registration_id
LIMIT 20;

-- --------------------------------------------------------------------
-- 4. Multi table JOIN - payments with registration, attendee and event
--    The payment trail from the money record up to the event.
-- --------------------------------------------------------------------
SELECT
    p.payment_id,
    a.full_name,
    e.event_name,
    p.amount,
    p.payment_method,
    p.payment_status,
    p.transaction_reference,
    p.payment_date
FROM payments p
INNER JOIN registrations r ON r.registration_id = p.registration_id
INNER JOIN attendees a    ON a.attendee_id    = r.attendee_id
INNER JOIN events e      ON e.event_id       = r.event_id
ORDER BY p.payment_id
LIMIT 20;

-- --------------------------------------------------------------------
-- 5. Self join - two events in the same venue on different dates
--    A table joined with itself - here to find events that share a venue.
-- --------------------------------------------------------------------
SELECT
    e1.venue_id,
    v.venue_name,
    e1.event_id   AS event_id_1,
    e1.event_name AS event_1,
    e1.event_date AS date_1,
    e2.event_id   AS event_id_2,
    e2.event_name AS event_2,
    e2.event_date AS date_2
FROM events e1
INNER JOIN events e2
        ON e1.venue_id = e2.venue_id
       AND e1.event_id < e2.event_id
       AND e1.event_date <> e2.event_date
INNER JOIN venues v ON v.venue_id = e1.venue_id
ORDER BY v.venue_name, e1.event_date
LIMIT 20;

-- --------------------------------------------------------------------
-- 6. Self join - attendees registered for more than one event
--    The registration table joined with itself through the attendee.
-- --------------------------------------------------------------------
SELECT
    a.attendee_id,
    a.full_name,
    e1.event_name AS event_1,
    e2.event_name AS event_2
FROM registrations r1
INNER JOIN registrations r2
        ON r1.attendee_id = r2.attendee_id
       AND r1.registration_id < r2.registration_id
INNER JOIN attendees a ON a.attendee_id = r1.attendee_id
INNER JOIN events e1   ON e1.event_id   = r1.event_id
INNER JOIN events e2   ON e2.event_id   = r2.event_id
ORDER BY a.attendee_id, e1.event_name
LIMIT 20;

-- --------------------------------------------------------------------
-- 7. LEFT JOIN - attendees that never registered for anything
--    The IS NULL filter turns the LEFT JOIN into an 'anti join'.
-- --------------------------------------------------------------------
SELECT
    a.attendee_id,
    a.full_name,
    a.email,
    a.organization
FROM attendees a
LEFT JOIN registrations r ON r.attendee_id = a.attendee_id
WHERE r.registration_id IS NULL
ORDER BY a.attendee_id;

-- --------------------------------------------------------------------
-- 8. Self join - proof that no venue is double booked
--    This query returns no rows - the backend prevents overlapping bookings.
-- --------------------------------------------------------------------
SELECT
    v.venue_name,
    e1.event_name AS event_1,
    e2.event_name AS event_2,
    e1.event_date
FROM events e1
INNER JOIN events e2
        ON e1.venue_id = e2.venue_id
       AND e1.event_id < e2.event_id
       AND e1.event_date = e2.event_date
INNER JOIN venues v ON v.venue_id = e1.venue_id
ORDER BY e1.event_date;
