-- ==================================================================
-- Experiment 3: Set operations on attendee groups
-- DBMS concept: UNION / UNION ALL / INTERSECT / EXCEPT
-- ==================================================================
--
-- The attendee groups of the event categories are combined with the four set operators. The result of UNION (distinct rows) is compared with UNION ALL (rows are kept twice).
--
-- * UNION removes duplicate rows, UNION ALL keeps them - compare the row counts of the first two tables.
-- * INTERSECT and EXCEPT are native MySQL operators from version 8.0.31 onwards. On older servers the equivalent EXISTS / NOT EXISTS query is executed instead and clearly labelled.
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. UNION - technical OR cultural attendees (distinct)
--    Only attendees that appear in both halves are listed once.
-- --------------------------------------------------------------------
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Technical'
UNION
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Cultural'
ORDER BY 1;

-- --------------------------------------------------------------------
-- 2. UNION ALL - the same groups, duplicates kept
--    An attendee that registered for both categories appears twice.
-- --------------------------------------------------------------------
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Technical'
UNION ALL
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Cultural'
ORDER BY 1;

-- --------------------------------------------------------------------
-- 3. INTERSECT - attendees in BOTH technical and sports
--    Portable equivalent using EXISTS: attendees registered for a technical AND a sports event.
--    MySQL >= 8.0.31 executes the native set operator; on older servers the
--    application runs the equivalent EXISTS / NOT EXISTS query instead.
-- --------------------------------------------------------------------
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Technical'
INTERSECT
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Sports'
ORDER BY 1;

-- --------------------------------------------------------------------
-- 4. EXCEPT - technical attendees that are NOT sports attendees
--    Portable equivalent using EXISTS + NOT EXISTS.
--    MySQL >= 8.0.31 executes the native set operator; on older servers the
--    application runs the equivalent EXISTS / NOT EXISTS query instead.
-- --------------------------------------------------------------------
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Technical'
EXCEPT
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Sports'
ORDER BY 1;
