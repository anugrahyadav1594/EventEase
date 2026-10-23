-- ==================================================================
-- Experiment 2: Constraint enforcement by the database engine
-- DBMS concept: PRIMARY KEY / FOREIGN KEY / UNIQUE / NOT NULL / CHECK
-- ==================================================================
--
-- Valid statements are accepted, invalid ones are rejected by MySQL itself. The error message of the engine is shown for every rejected statement.
--
-- * MySQL enforces PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL and (since 8.0.16) CHECK constraints.
-- * Business rules that need a second table - e.g. 'event capacity <= venue capacity' - cannot be expressed with a CHECK constraint and are therefore validated by the backend inside a transaction.
-- * The demo rows are removed automatically: the whole experiment runs inside a transaction that is rolled back.
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. Valid INSERT with an explicit PRIMARY KEY
--    The PRIMARY KEY column can also be supplied explicitly - here it proves that the key is unique.
-- --------------------------------------------------------------------
INSERT INTO attendees (attendee_id, full_name, email, phone, organization, registration_date)
VALUES (9001, 'Primary Key Demo', 'lab.primarykey@eventease.edu', '+91-90000-00001', 'SQL Lab', CURRENT_TIMESTAMP);

-- --------------------------------------------------------------------
-- 2. Invalid INSERT - duplicate PRIMARY KEY (1062)
--    The engine rejects the row because attendee_id 9001 already exists.
-- --------------------------------------------------------------------
INSERT INTO attendees (attendee_id, full_name, email, phone, organization, registration_date)
VALUES (9001, 'Duplicate Key Demo', 'lab.duplicate@eventease.edu', '+91-90000-00002', 'SQL Lab', CURRENT_TIMESTAMP);

-- --------------------------------------------------------------------
-- 3. Invalid INSERT - NOT NULL violation (1048)
--    organizer_name is declared NOT NULL, so NULL is rejected.
-- --------------------------------------------------------------------
INSERT INTO organizers (organizer_name, email, created_at)
VALUES (NULL, 'lab.notnull@eventease.edu', CURRENT_TIMESTAMP);

-- --------------------------------------------------------------------
-- 4. Invalid INSERT - UNIQUE violation on e-mail (1062)
--    attendees.email carries a UNIQUE constraint.
-- --------------------------------------------------------------------
INSERT INTO attendees (full_name, email, registration_date)
VALUES ('Duplicate Mail Demo', 'lab.primarykey@eventease.edu', CURRENT_TIMESTAMP);

-- --------------------------------------------------------------------
-- 5. Invalid INSERT - CHECK violation on capacity (3819)
--    The CHECK constraint 'capacity > 0' blocks the negative capacity.
-- --------------------------------------------------------------------
INSERT INTO venues (venue_name, location, capacity, venue_type, availability_status)
VALUES ('Negative Capacity Hall', 'SQL Lab', -25, 'Demo', 'Available');

-- --------------------------------------------------------------------
-- 6. Invalid INSERT - FOREIGN KEY violation (1452)
--    attendee_id 999999 does not exist - the FOREIGN KEY to attendees is enforced.
-- --------------------------------------------------------------------
INSERT INTO registrations (attendee_id, event_id, registration_date, registration_status, attendance_status, ticket_type, ticket_price)
VALUES (999999, 1, CURRENT_TIMESTAMP, 'Registered', 'Not Marked', 'General', 0);

-- --------------------------------------------------------------------
-- 7. Invalid INSERT - UNIQUE (attendee_id, event_id) violation
--    A participant can only be registered once per event (composite UNIQUE constraint).
-- --------------------------------------------------------------------
INSERT INTO registrations (attendee_id, event_id, registration_date, registration_status, attendance_status, ticket_type, ticket_price)
SELECT r.attendee_id, r.event_id, CURRENT_TIMESTAMP, 'Registered', 'Not Marked', 'General', 0
FROM registrations r
LIMIT 1;

-- --------------------------------------------------------------------
-- 8. Valid SELECT - proof that only the legal row survived
--    Only the valid insert from the beginning of this experiment is present.
-- --------------------------------------------------------------------
SELECT attendee_id, full_name, email
FROM attendees
WHERE email = 'lab.primarykey@eventease.edu';
