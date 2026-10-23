"""The nine mandatory DBMS experiments used by the SQL Lab.

Each experiment is a list of *predefined* statements.  The frontend can only
choose which experiment to run - it can never submit arbitrary SQL, so the
read-only guarantee of the SQL Lab holds.

`native_sql` is used for the set operations when the connected server really
supports INTERSECT / EXCEPT (MySQL >= 8.0.31); otherwise the portable
`EXISTS` / `NOT EXISTS` equivalent is executed and clearly labelled.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LabStatement:
    label: str
    sql: str
    expect: str = "rows"  # rows | error | none
    note: str = ""
    native_sql: str | None = None  # preferred SQL when the server supports it
    cleanup: bool = False


@dataclass
class LabExperiment:
    key: str
    number: int
    title: str
    concept: str
    description: str
    statements: list[LabStatement]
    notes: list[str] = field(default_factory=list)
    transactional: bool = True
    defaults: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Experiment 1 - DDL and DML
# ---------------------------------------------------------------------------
EXPERIMENT_1 = LabExperiment(
    key="ddl-dml",
    number=1,
    title="DDL and DML on a disposable demo table",
    concept="CREATE TABLE / ALTER TABLE / INSERT / UPDATE / SELECT / DELETE / DROP",
    description=(
        "The complete data definition and data manipulation life cycle is demonstrated on the "
        "throw-away table `eventease_demo_scratch`. No EventEase table is ever dropped by the demo."
    ),
    notes=[
        "The scratch table is created, filled, altered, updated, emptied and finally dropped again.",
        "Every statement runs against the live database - the result grid below is the real output.",
    ],
    transactional=False,
    statements=[
        LabStatement(
            label="CREATE TABLE eventease_demo_scratch",
            sql="""
CREATE TABLE eventease_demo_scratch (
    demo_id     INT PRIMARY KEY,
    demo_label  VARCHAR(60) NOT NULL,
    demo_amount DECIMAL(10, 2) NOT NULL,
    CONSTRAINT ck_demo_amount CHECK (demo_amount >= 0)
)
""",
            expect="none",
            note="Creates an isolated table with a PRIMARY KEY, a NOT NULL column and a CHECK constraint.",
        ),
        LabStatement(
            label="INSERT two rows",
            sql="""
INSERT INTO eventease_demo_scratch (demo_id, demo_label, demo_amount)
VALUES (1, 'Inserted Row A', 150.00),
       (2, 'Inserted Row B', 275.50)
""",
            expect="none",
            note="DML: adds two rows to the scratch table.",
        ),
        LabStatement(
            label="SELECT the inserted rows",
            sql="SELECT * FROM eventease_demo_scratch ORDER BY demo_id",
            note="Reads the rows back - this is the state after the INSERT.",
        ),
        LabStatement(
            label="ALTER TABLE ... ADD COLUMN",
            sql="ALTER TABLE eventease_demo_scratch ADD COLUMN demo_note VARCHAR(80) NULL",
            expect="none",
            note="DDL: extends the structure of the table without touching the existing rows.",
        ),
        LabStatement(
            label="UPDATE a single row",
            sql="""
UPDATE eventease_demo_scratch
   SET demo_amount = demo_amount + 25.00,
       demo_note = 'updated by the SQL lab'
 WHERE demo_id = 1
""",
            expect="none",
            note="DML: increases the amount of row 1 by 25.00.",
        ),
        LabStatement(
            label="SELECT after the UPDATE",
            sql="SELECT * FROM eventease_demo_scratch ORDER BY demo_id",
            note="The new value and the new column are visible.",
        ),
        LabStatement(
            label="DELETE one row",
            sql="DELETE FROM eventease_demo_scratch WHERE demo_id = 2",
            expect="none",
            note="DML: removes row 2 again.",
        ),
        LabStatement(
            label="SELECT the remaining rows",
            sql="SELECT COUNT(*) AS rows_remaining FROM eventease_demo_scratch",
            note="Only row 1 is left in the table.",
        ),
        LabStatement(
            label="DROP the disposable table",
            sql="DROP TABLE eventease_demo_scratch",
            expect="none",
            note="DDL: the scratch table is removed again - the EventEase tables are never touched.",
            cleanup=True,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 2 - Constraints
# ---------------------------------------------------------------------------
EXPERIMENT_2 = LabExperiment(
    key="constraints",
    number=2,
    title="Constraint enforcement by the database engine",
    concept="PRIMARY KEY / FOREIGN KEY / UNIQUE / NOT NULL / CHECK",
    description=(
        "Valid statements are accepted, invalid ones are rejected by MySQL itself. "
        "The error message of the engine is shown for every rejected statement."
    ),
    notes=[
        "MySQL enforces PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL and (since 8.0.16) CHECK constraints.",
        "Business rules that need a second table - e.g. 'event capacity <= venue capacity' - cannot be "
        "expressed with a CHECK constraint and are therefore validated by the backend inside a transaction.",
        "The demo rows are removed automatically: the whole experiment runs inside a transaction that is rolled back.",
    ],
    statements=[
        LabStatement(
            label="Valid INSERT with an explicit PRIMARY KEY",
            sql="""
INSERT INTO attendees (attendee_id, full_name, email, phone, organization, registration_date)
VALUES (9001, 'Primary Key Demo', 'lab.primarykey@eventease.edu', '+91-90000-00001', 'SQL Lab', CURRENT_TIMESTAMP)
""",
            expect="none",
            note="The PRIMARY KEY column can also be supplied explicitly - here it proves that the key is unique.",
        ),
        LabStatement(
            label="Invalid INSERT - duplicate PRIMARY KEY (1062)",
            sql="""
INSERT INTO attendees (attendee_id, full_name, email, phone, organization, registration_date)
VALUES (9001, 'Duplicate Key Demo', 'lab.duplicate@eventease.edu', '+91-90000-00002', 'SQL Lab', CURRENT_TIMESTAMP)
""",
            expect="error",
            note="The engine rejects the row because attendee_id 9001 already exists.",
        ),
        LabStatement(
            label="Invalid INSERT - NOT NULL violation (1048)",
            sql="""
INSERT INTO organizers (organizer_name, email, created_at)
VALUES (NULL, 'lab.notnull@eventease.edu', CURRENT_TIMESTAMP)
""",
            expect="error",
            note="organizer_name is declared NOT NULL, so NULL is rejected.",
        ),
        LabStatement(
            label="Invalid INSERT - UNIQUE violation on e-mail (1062)",
            sql="""
INSERT INTO attendees (full_name, email, registration_date)
VALUES ('Duplicate Mail Demo', 'lab.primarykey@eventease.edu', CURRENT_TIMESTAMP)
""",
            expect="error",
            note="attendees.email carries a UNIQUE constraint.",
        ),
        LabStatement(
            label="Invalid INSERT - CHECK violation on capacity (3819)",
            sql="""
INSERT INTO venues (venue_name, location, capacity, venue_type, availability_status)
VALUES ('Negative Capacity Hall', 'SQL Lab', -25, 'Demo', 'Available')
""",
            expect="error",
            note="The CHECK constraint 'capacity > 0' blocks the negative capacity.",
        ),
        LabStatement(
            label="Invalid INSERT - FOREIGN KEY violation (1452)",
            sql="""
INSERT INTO registrations (attendee_id, event_id, registration_date, registration_status, attendance_status, ticket_type, ticket_price)
VALUES (999999, 1, CURRENT_TIMESTAMP, 'Registered', 'Not Marked', 'General', 0)
""",
            expect="error",
            note="attendee_id 999999 does not exist - the FOREIGN KEY to attendees is enforced.",
        ),
        LabStatement(
            label="Invalid INSERT - UNIQUE (attendee_id, event_id) violation",
            sql="""
INSERT INTO registrations (attendee_id, event_id, registration_date, registration_status, attendance_status, ticket_type, ticket_price)
SELECT r.attendee_id, r.event_id, CURRENT_TIMESTAMP, 'Registered', 'Not Marked', 'General', 0
FROM registrations r
LIMIT 1
""",
            expect="error",
            note="A participant can only be registered once per event (composite UNIQUE constraint).",
        ),
        LabStatement(
            label="Valid SELECT - proof that only the legal row survived",
            sql="""
SELECT attendee_id, full_name, email
FROM attendees
WHERE email = 'lab.primarykey@eventease.edu'
""",
            note="Only the valid insert from the beginning of this experiment is present.",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 3 - Set operations
# ---------------------------------------------------------------------------
_TECHNICAL_ATTENDEES = """
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Technical'
"""

_CULTURAL_ATTENDEES = """
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Cultural'
"""

_SPORTS_ATTENDEES = """
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.event_category = 'Sports'
"""

_INTERSECT_NATIVE = (
    _TECHNICAL_ATTENDEES.strip()
    + "\nINTERSECT\n"
    + _SPORTS_ATTENDEES.strip()
    + "\nORDER BY 1"
)

_INTERSECT_PORTABLE = """
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
WHERE EXISTS (SELECT 1
                FROM registrations r
                JOIN events e ON e.event_id = r.event_id
               WHERE r.attendee_id = a.attendee_id
                 AND e.event_category = 'Technical')
  AND EXISTS (SELECT 1
                FROM registrations r
                JOIN events e ON e.event_id = r.event_id
               WHERE r.attendee_id = a.attendee_id
                 AND e.event_category = 'Sports')
ORDER BY 1
"""

_EXCEPT_NATIVE = (
    _TECHNICAL_ATTENDEES.strip()
    + "\nEXCEPT\n"
    + _SPORTS_ATTENDEES.strip()
    + "\nORDER BY 1"
)

_EXCEPT_PORTABLE = """
SELECT a.attendee_id, a.full_name, a.email
FROM attendees a
WHERE EXISTS (SELECT 1
                FROM registrations r
                JOIN events e ON e.event_id = r.event_id
               WHERE r.attendee_id = a.attendee_id
                 AND e.event_category = 'Technical')
  AND NOT EXISTS (SELECT 1
                    FROM registrations r
                    JOIN events e ON e.event_id = r.event_id
                   WHERE r.attendee_id = a.attendee_id
                     AND e.event_category = 'Sports')
ORDER BY a.attendee_id
"""

EXPERIMENT_3 = LabExperiment(
    key="set-operations",
    number=3,
    title="Set operations on attendee groups",
    concept="UNION / UNION ALL / INTERSECT / EXCEPT",
    description=(
        "The attendee groups of the event categories are combined with the four set operators. "
        "The result of UNION (distinct rows) is compared with UNION ALL (rows are kept twice)."
    ),
    notes=[
        "UNION removes duplicate rows, UNION ALL keeps them - compare the row counts of the first two tables.",
        "INTERSECT and EXCEPT are native MySQL operators from version 8.0.31 onwards. On older servers "
        "the equivalent EXISTS / NOT EXISTS query is executed instead and clearly labelled.",
    ],
    statements=[
        LabStatement(
            label="UNION - technical OR cultural attendees (distinct)",
            sql=(
                _TECHNICAL_ATTENDEES.strip()
                + "\nUNION\n"
                + _CULTURAL_ATTENDEES.strip()
                + "\nORDER BY 1"
            ),
            note="Only attendees that appear in both halves are listed once.",
        ),
        LabStatement(
            label="UNION ALL - the same groups, duplicates kept",
            sql=(
                _TECHNICAL_ATTENDEES.strip()
                + "\nUNION ALL\n"
                + _CULTURAL_ATTENDEES.strip()
                + "\nORDER BY 1"
            ),
            note="An attendee that registered for both categories appears twice.",
        ),
        LabStatement(
            label="INTERSECT - attendees in BOTH technical and sports",
            sql=_INTERSECT_PORTABLE,
            native_sql=_INTERSECT_NATIVE,
            note="Portable equivalent using EXISTS: attendees registered for a technical AND a sports event.",
        ),
        LabStatement(
            label="EXCEPT - technical attendees that are NOT sports attendees",
            sql=_EXCEPT_PORTABLE,
            native_sql=_EXCEPT_NATIVE,
            note="Portable equivalent using EXISTS + NOT EXISTS.",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 4 - String functions
# ---------------------------------------------------------------------------
EXPERIMENT_4 = LabExperiment(
    key="string-functions",
    number=4,
    title="String functions on attendee and event data",
    concept="CONCAT / UPPER / LOWER / LENGTH / CHAR_LENGTH / SUBSTRING / TRIM",
    description="The classic string toolbox applied to real attendee and event rows.",
    notes=[
        "In MySQL LENGTH() returns the number of bytes while CHAR_LENGTH() returns the number of characters.",
        "The SQLite development fallback returns the character count for both functions.",
    ],
    statements=[
        LabStatement(
            label="All string functions in one query",
            sql="""
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
LIMIT 15
""",
            note="One row per attendee with all seven string functions applied.",
        ),
        LabStatement(
            label="Normalising event names and trimming descriptions",
            sql="""
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
LIMIT 15
""",
            note="UPPER/LOWER normalise the data, TRIM removes stray spaces, CONCAT builds a label.",
        ),
        LabStatement(
            label="Extracting the domain from every e-mail address",
            sql="""
SELECT
    a.full_name,
    a.email,
    SUBSTRING(a.email, INSTR(a.email, '@') + 1) AS email_domain
FROM attendees a
ORDER BY a.attendee_id
LIMIT 15
""",
            note="INSTR() finds the '@' and SUBSTRING() cuts out everything behind it.",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 5 - Aggregate functions
# ---------------------------------------------------------------------------
EXPERIMENT_5 = LabExperiment(
    key="aggregate-functions",
    number=5,
    title="Aggregate functions over the whole database",
    concept="COUNT / SUM / AVG / MIN / MAX",
    description="Single row answers for the most important numbers of the system.",
    statements=[
        LabStatement(
            label="COUNT - how many rows does every table hold?",
            sql="""
SELECT
    (SELECT COUNT(*) FROM organizers)   AS total_organizers,
    (SELECT COUNT(*) FROM venues)       AS total_venues,
    (SELECT COUNT(*) FROM events)       AS total_events,
    (SELECT COUNT(*) FROM attendees)    AS total_attendees,
    (SELECT COUNT(*) FROM registrations) AS total_registrations,
    (SELECT COUNT(*) FROM payments)      AS total_payments
""",
            note="COUNT(*) counts the rows of every table.",
        ),
        LabStatement(
            label="AVG / MIN / MAX - registrations per event",
            sql="""
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
) AS per_event
""",
            note="The inner query counts the registrations per event, the outer one aggregates them.",
        ),
        LabStatement(
            label="MIN / MAX / AVG - ticket prices",
            sql="""
SELECT
    MIN(ticket_price)              AS lowest_ticket_price,
    MAX(ticket_price)              AS highest_ticket_price,
    ROUND(AVG(ticket_price), 2)    AS average_ticket_price,
    SUM(ticket_price)              AS total_ticket_value
FROM events
""",
            note="The free events (price 0) pull the average down - that is expected.",
        ),
        LabStatement(
            label="SUM - revenue per payment status",
            sql="""
SELECT
    payment_status,
    COUNT(*)        AS payment_count,
    SUM(amount)     AS total_amount,
    ROUND(AVG(amount), 2) AS average_amount,
    MIN(amount)     AS smallest_payment,
    MAX(amount)     AS largest_payment
FROM payments
GROUP BY payment_status
ORDER BY total_amount DESC
""",
            note="Only 'Completed' rows are collected revenue - refunds are listed separately.",
        ),
        LabStatement(
            label="SUM - total collected revenue",
            sql="""
SELECT COALESCE(SUM(amount), 0) AS total_completed_amount
FROM payments
WHERE payment_status = 'Completed'
""",
            note="Refunded payments are not part of this sum, so money is never counted twice.",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 6 - GROUP BY and HAVING
# ---------------------------------------------------------------------------
EXPERIMENT_6 = LabExperiment(
    key="group-by-having",
    number=6,
    title="GROUP BY and HAVING",
    concept="GROUP BY with aggregate functions and HAVING filters",
    description=(
        "GROUP BY condenses the rows of a table into one row per group, HAVING filters those groups "
        "(WHERE filters the rows before the grouping). The thresholds are configurable parameters."
    ),
    defaults={"threshold": 3, "min_events": 1, "venue_threshold": 1},
    statements=[
        LabStatement(
            label="Registrations per event (HAVING > threshold)",
            sql="""
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    COUNT(r.registration_id) AS registration_count
FROM events e
JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name, e.event_category
HAVING COUNT(r.registration_id) > :threshold
ORDER BY registration_count DESC
""",
            note="HAVING works on the grouped result - here only events with more than the given number of registrations.",
        ),
        LabStatement(
            label="Revenue per event (GROUP BY + SUM + HAVING)",
            sql="""
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
ORDER BY revenue DESC
""",
            note="Only events that really collected money survive the HAVING condition.",
        ),
        LabStatement(
            label="Events grouped by category",
            sql="""
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
ORDER BY event_count DESC, e.event_category
""",
            note="One row per event category with the aggregated numbers of the group.",
        ),
        LabStatement(
            label="Events managed by every organizer",
            sql="""
SELECT
    o.organizer_id,
    o.organizer_name,
    o.organization_name,
    COUNT(e.event_id) AS events_managed
FROM organizers o
LEFT JOIN events e ON e.organizer_id = o.organizer_id
GROUP BY o.organizer_id, o.organizer_name, o.organization_name
HAVING COUNT(e.event_id) >= :min_events
ORDER BY events_managed DESC, o.organizer_name
""",
            note="The LEFT JOIN keeps organizers without any event in the result.",
        ),
        LabStatement(
            label="Venues hosting more than the given number of events",
            sql="""
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
ORDER BY events_hosted DESC, v.venue_name
""",
            note="HAVING on a grouped count - venues that are used often enough.",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 7 - Nested subqueries
# ---------------------------------------------------------------------------
EXPERIMENT_7 = LabExperiment(
    key="nested-subqueries",
    number=7,
    title="Nested and correlated subqueries",
    concept="Subquery in SELECT / WHERE / HAVING and correlated subqueries",
    description="Sub queries are evaluated first and their result is used by the outer query.",
    statements=[
        LabStatement(
            label="Events with more registrations than the average event",
            sql="""
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
ORDER BY registration_count DESC
""",
            note="The sub query in the HAVING clause calculates the average number of registrations per event.",
        ),
        LabStatement(
            label="Attendees registered for above-average priced events",
            sql="""
SELECT
    a.attendee_id,
    a.full_name,
    COUNT(DISTINCT r.registration_id) AS premium_registrations
FROM attendees a
JOIN registrations r ON r.attendee_id = a.attendee_id
JOIN events e       ON e.event_id = r.event_id
WHERE e.ticket_price > (SELECT AVG(ticket_price) FROM events)
GROUP BY a.attendee_id, a.full_name
ORDER BY premium_registrations DESC, a.full_name
""",
            note="The sub query in the WHERE clause compares the ticket price with the average of all events.",
        ),
        LabStatement(
            label="Venues that are larger than the average venue",
            sql="""
SELECT
    v.venue_id,
    v.venue_name,
    v.location,
    v.capacity,
    (SELECT AVG(capacity) FROM venues) AS average_venue_capacity
FROM venues v
WHERE v.capacity > (SELECT AVG(capacity) FROM venues)
ORDER BY v.capacity DESC
""",
            note="The same sub query is used in the SELECT list and in the WHERE condition.",
        ),
        LabStatement(
            label="Correlated subquery - registration count per event",
            sql="""
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
ORDER BY registration_count DESC
""",
            note="The inner query refers to the outer row (e.event_id) - that makes it a correlated subquery.",
        ),
        LabStatement(
            label="Correlated subquery - attendees with more than one registration",
            sql="""
SELECT
    a.attendee_id,
    a.full_name,
    (SELECT COUNT(*) FROM registrations r WHERE r.attendee_id = a.attendee_id) AS registration_count
FROM attendees a
WHERE (SELECT COUNT(*) FROM registrations r WHERE r.attendee_id = a.attendee_id) > 1
ORDER BY registration_count DESC, a.full_name
""",
            note="For every attendee the number of registrations is calculated twice - once for the list, once for the filter.",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 8 - Views
# ---------------------------------------------------------------------------
EXPERIMENT_8 = LabExperiment(
    key="views",
    number=8,
    title="Reusable SQL views",
    concept="CREATE VIEW and reading from views",
    description=(
        "Five views encapsulate the recurring reports. The definitions live in "
        "`database/views.sql` and are used by the application itself."
    ),
    notes=[
        "A view behaves like a virtual table: it stores the SQL, not the data.",
        "The application dashboard and the reports page read from exactly these views.",
    ],
    statements=[
        LabStatement(
            label="v_upcoming_events - all events that are still to come",
            sql="SELECT * FROM v_upcoming_events ORDER BY event_date, start_time",
            note="JOIN of events, organizers and venues plus the number of free seats.",
        ),
        LabStatement(
            label="v_event_registration_summary",
            sql="SELECT * FROM v_event_registration_summary ORDER BY total_registrations DESC",
            note="One row per event with the registration and attendance counters.",
        ),
        LabStatement(
            label="v_event_revenue_summary",
            sql="SELECT * FROM v_event_revenue_summary ORDER BY gross_revenue DESC",
            note="Revenue per event - completed, refunded and pending in separate columns.",
        ),
        LabStatement(
            label="v_venue_utilization",
            sql="SELECT * FROM v_venue_utilization ORDER BY utilization_percent DESC",
            note="How busy every venue is.",
        ),
        LabStatement(
            label="v_attendee_registration_history",
            sql="SELECT * FROM v_attendee_registration_history ORDER BY total_registrations DESC, full_name",
            note="Registration history of every attendee including the money they paid.",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Experiment 9 - Joins
# ---------------------------------------------------------------------------
EXPERIMENT_9 = LabExperiment(
    key="joins",
    number=9,
    title="INNER JOIN, LEFT JOIN, multi-table joins and self joins",
    concept="INNER JOIN / LEFT JOIN / multi table joins / self joins",
    description="How the six tables of the schema are connected with each other.",
    statements=[
        LabStatement(
            label="INNER JOIN - events with their organizer and venue",
            sql="""
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
ORDER BY e.event_date, e.event_id
""",
            note="Only rows that exist on both sides are returned.",
        ),
        LabStatement(
            label="LEFT JOIN - events without any registration",
            sql="""
SELECT
    e.event_id,
    e.event_name,
    e.event_category,
    COUNT(r.registration_id) AS registration_count
FROM events e
LEFT JOIN registrations r ON r.event_id = e.event_id
GROUP BY e.event_id, e.event_name, e.event_category
HAVING COUNT(r.registration_id) = 0
ORDER BY e.event_name
""",
            note="The LEFT JOIN keeps the events without registrations - exactly the rows an INNER JOIN would drop.",
        ),
        LabStatement(
            label="Multi table JOIN - registrations with attendee and event",
            sql="""
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
LIMIT 20
""",
            note="Three tables connected in one query.",
        ),
        LabStatement(
            label="Multi table JOIN - payments with registration, attendee and event",
            sql="""
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
LIMIT 20
""",
            note="The payment trail from the money record up to the event.",
        ),
        LabStatement(
            label="Self join - two events in the same venue on different dates",
            sql="""
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
LIMIT 20
""",
            note="A table joined with itself - here to find events that share a venue.",
        ),
        LabStatement(
            label="Self join - attendees registered for more than one event",
            sql="""
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
LIMIT 20
""",
            note="The registration table joined with itself through the attendee.",
        ),
        LabStatement(
            label="LEFT JOIN - attendees that never registered for anything",
            sql="""
SELECT
    a.attendee_id,
    a.full_name,
    a.email,
    a.organization
FROM attendees a
LEFT JOIN registrations r ON r.attendee_id = a.attendee_id
WHERE r.registration_id IS NULL
ORDER BY a.attendee_id
""",
            note="The IS NULL filter turns the LEFT JOIN into an 'anti join'.",
        ),
        LabStatement(
            label="Self join - proof that no venue is double booked",
            sql="""
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
ORDER BY e1.event_date
""",
            note="This query returns no rows - the backend prevents overlapping bookings.",
        ),
    ],
)


EXPERIMENTS: list[LabExperiment] = [
    EXPERIMENT_1,
    EXPERIMENT_2,
    EXPERIMENT_3,
    EXPERIMENT_4,
    EXPERIMENT_5,
    EXPERIMENT_6,
    EXPERIMENT_7,
    EXPERIMENT_8,
    EXPERIMENT_9,
]

EXPERIMENTS_BY_KEY: dict[str, LabExperiment] = {experiment.key: experiment for experiment in EXPERIMENTS}
