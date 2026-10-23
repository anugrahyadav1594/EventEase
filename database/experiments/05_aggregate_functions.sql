-- ==================================================================
-- Experiment 5: Aggregate functions over the whole database
-- DBMS concept: COUNT / SUM / AVG / MIN / MAX
-- ==================================================================
--
-- Single row answers for the most important numbers of the system.
--
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. COUNT - how many rows does every table hold?
--    COUNT(*) counts the rows of every table.
-- --------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM organizers)   AS total_organizers,
    (SELECT COUNT(*) FROM venues)       AS total_venues,
    (SELECT COUNT(*) FROM events)       AS total_events,
    (SELECT COUNT(*) FROM attendees)    AS total_attendees,
    (SELECT COUNT(*) FROM registrations) AS total_registrations,
    (SELECT COUNT(*) FROM payments)      AS total_payments;

-- --------------------------------------------------------------------
-- 2. AVG / MIN / MAX - registrations per event
--    The inner query counts the registrations per event, the outer one aggregates them.
-- --------------------------------------------------------------------
SELECT
    COUNT(*)                AS event_count,
    AVG(registration_count) AS average_registrations_per_event,
    MIN(registration_count) AS lowest_registration_count,
    MAX(registration_count) AS highest_registration_count
FROM (
    SELECT e.event_id, COUNT(r.registration_id) AS registration_count
    FROM events e
    LEFT JOIN registrations r ON r.event_id = e.event_id
    GROUP BY e.event_id
) AS per_event;

-- --------------------------------------------------------------------
-- 3. MIN / MAX / AVG - ticket prices
--    The free events (price 0) pull the average down - that is expected.
-- --------------------------------------------------------------------
SELECT
    MIN(ticket_price)              AS lowest_ticket_price,
    MAX(ticket_price)              AS highest_ticket_price,
    ROUND(AVG(ticket_price), 2)    AS average_ticket_price,
    SUM(ticket_price)              AS total_ticket_value
FROM events;

-- --------------------------------------------------------------------
-- 4. SUM - revenue per payment status
--    Only 'Completed' rows are collected revenue - refunds are listed separately.
-- --------------------------------------------------------------------
SELECT
    payment_status,
    COUNT(*)        AS payment_count,
    SUM(amount)     AS total_amount,
    ROUND(AVG(amount), 2) AS average_amount,
    MIN(amount)     AS smallest_payment,
    MAX(amount)     AS largest_payment
FROM payments
GROUP BY payment_status
ORDER BY total_amount DESC;

-- --------------------------------------------------------------------
-- 5. SUM - total collected revenue
--    Refunded payments are not part of this sum, so money is never counted twice.
-- --------------------------------------------------------------------
SELECT COALESCE(SUM(amount), 0) AS total_completed_amount
FROM payments
WHERE payment_status = 'Completed';
