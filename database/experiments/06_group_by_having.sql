-- ==================================================================
-- Experiment 6: GROUP BY and HAVING
-- DBMS concept: GROUP BY with aggregate functions and HAVING filters
-- ==================================================================
--
-- GROUP BY condenses the rows of a table into one row per group, HAVING filters those groups (WHERE filters the rows before the grouping). The thresholds are configurable parameters.
--
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. Registrations per event (HAVING > threshold)
--    HAVING works on the grouped result - here only events with more than the given number of registrations.
-- --------------------------------------------------------------------
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    COUNT(r.registration_id) AS registration_count
FROM events e
JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name, e.event_category
HAVING COUNT(r.registration_id) > :threshold
ORDER BY registration_count DESC;

-- --------------------------------------------------------------------
-- 2. Revenue per event (GROUP BY + SUM + HAVING)
--    Only events that really collected money survive the HAVING condition.
-- --------------------------------------------------------------------
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END) AS revenue
FROM events e
JOIN registrations r ON r.event_id = e.event_id
JOIN payments p      ON p.registration_id = r.registration_id
GROUP BY e.event_id, e.event_name, e.event_category
HAVING SUM(CASE WHEN p.payment_status = 'Completed' THEN p.amount ELSE 0 END) > 0
ORDER BY revenue DESC;

-- --------------------------------------------------------------------
-- 3. Events grouped by category
--    One row per event category with the aggregated numbers of the group.
-- --------------------------------------------------------------------
SELECT
    e.event_category,
    COUNT(*)                    AS event_count,
    COUNT(DISTINCT e.organizer_id) AS organizer_count,
    MIN(e.event_date)           AS first_event_date,
    MAX(e.event_date)           AS last_event_date,
    SUM(e.capacity)             AS total_capacity
FROM events e
GROUP BY e.event_category
HAVING COUNT(*) > 0
ORDER BY event_count DESC, e.event_category;

-- --------------------------------------------------------------------
-- 4. Events managed by every organizer
--    The LEFT JOIN keeps organizers without any event in the result.
-- --------------------------------------------------------------------
SELECT
    o.organizer_id,
    o.organizer_name,
    o.organization_name,
    COUNT(e.event_id) AS events_managed
FROM organizers o
LEFT JOIN events e ON e.organizer_id = o.organizer_id
GROUP BY o.organizer_id, o.organizer_name, o.organization_name
HAVING COUNT(e.event_id) >= :min_events
ORDER BY events_managed DESC, o.organizer_name;

-- --------------------------------------------------------------------
-- 5. Venues hosting more than the given number of events
--    HAVING on a grouped count - venues that are used often enough.
-- --------------------------------------------------------------------
SELECT
    v.venue_id,
    v.venue_name,
    v.location,
    v.capacity,
    COUNT(e.event_id) AS events_hosted
FROM venues v
JOIN events e ON e.venue_id = v.venue_id
GROUP BY v.venue_id, v.venue_name, v.location, v.capacity
HAVING COUNT(e.event_id) > :venue_threshold
ORDER BY events_hosted DESC, v.venue_name;
