-- ==================================================================
-- Experiment 8: Reusable SQL views
-- DBMS concept: CREATE VIEW and reading from views
-- ==================================================================
--
-- Five views encapsulate the recurring reports. The definitions live in `database/views.sql` and are used by the application itself.
--
-- * A view behaves like a virtual table: it stores the SQL, not the data.
-- * The application dashboard and the reports page read from exactly these views.
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. v_upcoming_events - all events that are still to come
--    JOIN of events, organizers and venues plus the number of free seats.
-- --------------------------------------------------------------------
SELECT * FROM v_upcoming_events ORDER BY event_date, start_time;

-- --------------------------------------------------------------------
-- 2. v_event_registration_summary
--    One row per event with the registration and attendance counters.
-- --------------------------------------------------------------------
SELECT * FROM v_event_registration_summary ORDER BY total_registrations DESC;

-- --------------------------------------------------------------------
-- 3. v_event_revenue_summary
--    Revenue per event - completed, refunded and pending in separate columns.
-- --------------------------------------------------------------------
SELECT * FROM v_event_revenue_summary ORDER BY gross_revenue DESC;

-- --------------------------------------------------------------------
-- 4. v_venue_utilization
--    How busy every venue is.
-- --------------------------------------------------------------------
SELECT * FROM v_venue_utilization ORDER BY utilization_percent DESC;

-- --------------------------------------------------------------------
-- 5. v_attendee_registration_history
--    Registration history of every attendee including the money they paid.
-- --------------------------------------------------------------------
SELECT * FROM v_attendee_registration_history ORDER BY total_registrations DESC, full_name;
