-- ==================================================================
-- Experiment 4: String functions on attendee and event data
-- DBMS concept: CONCAT / UPPER / LOWER / LENGTH / CHAR_LENGTH / SUBSTRING / TRIM
-- ==================================================================
--
-- The classic string toolbox applied to real attendee and event rows.
--
-- * In MySQL LENGTH() returns the number of bytes while CHAR_LENGTH() returns the number of characters.
-- * The SQLite development fallback returns the character count for both functions.
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. All string functions in one query
--    One row per attendee with all seven string functions applied.
-- --------------------------------------------------------------------
SELECT
    a.attendee_id,
    CONCAT(a.full_name, ' <', a.email, '>')     AS contact_label,
    UPPER(a.full_name)                          AS name_upper,
    LOWER(a.full_name)                          AS name_lower,
    LENGTH(a.full_name)                         AS name_length,
    CHAR_LENGTH(a.full_name)                    AS name_char_length,
    SUBSTRING(a.full_name, 1, 3)                AS first_three_chars,
    TRIM(a.organization)                        AS trimmed_organization
FROM attendees a
ORDER BY a.attendee_id
LIMIT 15;

-- --------------------------------------------------------------------
-- 2. Normalising event names and trimming descriptions
--    UPPER/LOWER normalise the data, TRIM removes stray spaces, CONCAT builds a label.
-- --------------------------------------------------------------------
SELECT
    e.event_id,
    UPPER(e.event_name)                              AS event_name_upper,
    LOWER(e.event_name)                              AS event_name_lower,
    LENGTH(e.event_name)                             AS event_name_length,
    CHAR_LENGTH(e.event_name)                        AS event_name_char_length,
    SUBSTRING(e.event_name, 1, 12)                  AS event_name_prefix,
    TRIM(e.event_category)                           AS trimmed_category,
    CONCAT(TRIM(e.event_category), ' / ', TRIM(e.event_name)) AS category_and_event
FROM events e
WHERE e.event_status <> 'Cancelled'
ORDER BY e.event_id
LIMIT 15;

-- --------------------------------------------------------------------
-- 3. Extracting the domain from every e-mail address
--    INSTR() finds the '@' and SUBSTRING() cuts out everything behind it.
-- --------------------------------------------------------------------
SELECT
    a.full_name,
    a.email,
    SUBSTRING(a.email, INSTR(a.email, '@') + 1) AS email_domain
FROM attendees a
ORDER BY a.attendee_id
LIMIT 15;
