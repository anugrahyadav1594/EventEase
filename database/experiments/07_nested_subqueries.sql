-- ==================================================================
-- Experiment 7: Nested and correlated subqueries
-- DBMS concept: Subquery in SELECT / WHERE / HAVING and correlated subqueries
-- ==================================================================
--
-- Sub queries are evaluated first and their result is used by the outer query.
--
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. Events with more registrations than the average event
--    The sub query in the HAVING clause calculates the average number of registrations per event.
-- --------------------------------------------------------------------
SELECT
    e.event_id,
    e.event_name,
    COUNT(r.registration_id) AS registration_count
FROM events e
JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name
HAVING COUNT(r.registration_id) > (
    SELECT AVG(x.total_registrations)
      FROM (SELECT COUNT(r2.registration_id) AS total_registrations
              FROM registrations r2
             GROUP BY r2.event_id) AS x
)
ORDER BY registration_count DESC;

-- --------------------------------------------------------------------
-- 2. Attendees registered for above-average priced events
--    The sub query in the WHERE clause compares the ticket price with the average of all events.
-- --------------------------------------------------------------------
SELECT
    a.attendee_id,
    a.full_name,
    COUNT(DISTINCT r.registration_id) AS premium_registrations
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.ticket_price > (SELECT AVG(ticket_price) FROM events)
GROUP BY a.attendee_id, a.full_name
ORDER BY premium_registrations DESC, a.full_name;

-- --------------------------------------------------------------------
-- 3. Venues that are larger than the average venue
--    The same sub query is used in the SELECT list and in the WHERE condition.
-- --------------------------------------------------------------------
SELECT
    v.venue_id,
    v.venue_name,
    v.location,
    v.capacity,
    (SELECT AVG(capacity) FROM venues) AS average_venue_capacity
FROM venues v
WHERE v.capacity > (SELECT AVG(capacity) FROM venues)
ORDER BY v.capacity DESC;

-- --------------------------------------------------------------------
-- 4. Correlated subquery - registration count per event
--    The inner query refers to the outer row (e.event_id) - that makes it a correlated subquery.
-- --------------------------------------------------------------------
SELECT
    e.event_id,
    e.event_name,
    e.event_date,
    (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.event_id) AS registration_count
FROM events e
WHERE (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.event_id) > (
    SELECT AVG(x.total_registrations)
      FROM (SELECT COUNT(r2.registration_id) AS total_registrations
              FROM registrations r2
             GROUP BY r2.event_id) AS x
)
ORDER BY registration_count DESC;

-- --------------------------------------------------------------------
-- 5. Correlated subquery - attendees with more than one registration
--    For every attendee the number of registrations is calculated twice - once for the list, once for the filter.
-- --------------------------------------------------------------------
SELECT
    a.attendee_id,
    a.full_name,
    (SELECT COUNT(*) FROM registrations r WHERE r.attendee_id = a.attendee_id) AS registration_count
FROM attendees a
WHERE (SELECT COUNT(*) FROM registrations r WHERE r.attendee_id = a.attendee_id) > 1
ORDER BY registration_count DESC, a.full_name;
