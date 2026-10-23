# DBMS Experiment Mapping

This document maps every one of the nine mandatory DBMS practical experiments to

* the **SQL file** that contains it,
* the **concrete statements** that are executed,
* the **application feature** that demonstrates it,
* and the **concept** that is being proved.

The SQL files are generated from the Python source of truth
(`backend/app/queries/sql_lab.py`) by `backend/scripts/generate_sql.py`, therefore the text in the
files and the text executed by the API are always identical.

---

## Overview

| # | Experiment | SQL file | Statements | Demonstrated in |
| --- | --- | --- | --- | --- |
| 1 | DDL and DML | `database/experiments/01_ddl_dml.sql` | 9 | SQL Lab → *DDL and DML* |
| 2 | Constraints | `database/experiments/02_constraints.sql` | 8 | SQL Lab → *Constraints* |
| 3 | Set operations | `database/experiments/03_set_operations.sql` | 4 | SQL Lab → *Set operations* |
| 4 | String functions | `database/experiments/04_string_functions.sql` | 3 | SQL Lab → *String functions* |
| 5 | Aggregate functions | `database/experiments/05_aggregate_functions.sql` | 5 | SQL Lab → *Aggregate functions* |
| 6 | GROUP BY and HAVING | `database/experiments/06_group_by_having.sql` | 5 | SQL Lab → *GROUP BY and HAVING* |
| 7 | Nested sub queries | `database/experiments/07_nested_subqueries.sql` | 5 | SQL Lab → *Nested subqueries* |
| 8 | Views | `database/experiments/08_views.sql` | 5 | SQL Lab → *Views*, dashboard, reports |
| 9 | Joins | `database/experiments/09_joins.sql` | 8 | SQL Lab → *Joins* |

---

## Experiment 1 — DDL and DML

**File:** `database/experiments/01_ddl_dml.sql`
**Concept:** `CREATE TABLE` · `ALTER TABLE` · `INSERT` · `UPDATE` · `SELECT` · `DELETE` · `DROP TABLE`

| # | Statement | What it proves |
| --- | --- | --- |
| 1 | `CREATE TABLE eventease_demo_scratch (demo_id INT PRIMARY KEY, demo_label VARCHAR(60) NOT NULL, demo_amount DECIMAL(10,2) NOT NULL, CONSTRAINT ck_demo_amount CHECK (demo_amount >= 0))` | DDL with a primary key, a NOT NULL column and a named CHECK constraint |
| 2 | `INSERT INTO eventease_demo_scratch … VALUES (1, …), (2, …)` | DML: multi-row insert |
| 3 | `SELECT * FROM eventease_demo_scratch ORDER BY demo_id` | reads the rows back |
| 4 | `ALTER TABLE eventease_demo_scratch ADD COLUMN demo_note VARCHAR(80) NULL` | DDL: structural change without data loss |
| 5 | `UPDATE … SET demo_amount = demo_amount + 25.00 WHERE demo_id = 1` | DML: update with an arithmetic expression |
| 6 | `SELECT * …` | shows the effect of the update |
| 7 | `DELETE FROM eventease_demo_scratch WHERE demo_id = 2` | DML: delete a single row |
| 8 | `SELECT COUNT(*) …` | proves that only one row is left |
| 9 | `DROP TABLE eventease_demo_scratch` | DDL: the disposable table is removed again |

**Safety:** only the disposable scratch table is touched — **no EventEase table is ever dropped**.
The runner removes the table again even if the experiment is aborted.

**Application feature:** SQL Lab → experiment *ddl-dml* → button *Run experiment*.

---

## Experiment 2 — Constraints

**File:** `database/experiments/02_constraints.sql`
**Concept:** `PRIMARY KEY` · `FOREIGN KEY` · `UNIQUE` · `NOT NULL` · `CHECK`

| # | Statement | Expected outcome |
| --- | --- | --- |
| 1 | `INSERT INTO attendees (attendee_id, …) VALUES (9001, …)` | accepted — a primary key may be supplied explicitly |
| 2 | same insert with `attendee_id = 9001` again | **rejected** — duplicate primary key (MySQL 1062 / SQLite *UNIQUE constraint failed*) |
| 3 | `INSERT INTO organizers (organizer_name, …) VALUES (NULL, …)` | **rejected** — NOT NULL violation (MySQL 1048) |
| 4 | `INSERT INTO attendees … 'lab.primarykey@eventease.edu'` (duplicate e-mail) | **rejected** — UNIQUE violation (MySQL 1062) |
| 5 | `INSERT INTO venues … capacity = -25` | **rejected** — CHECK violation `capacity > 0` (MySQL 3819) |
| 6 | `INSERT INTO registrations … attendee_id = 999999` | **rejected** — FOREIGN KEY violation (MySQL 1452) |
| 7 | `INSERT INTO registrations … SELECT` an existing attendee/event pair | **rejected** — composite `UNIQUE (attendee_id, event_id)` |
| 8 | `SELECT … WHERE email = 'lab.primarykey@eventease.edu'` | shows that only the legal row survived |

**Which constraints does MySQL enforce?** All five: primary key, foreign key, unique, not null and
(check since **8.0.16**). The SQL Lab shows the *engine's own error message* — the backend does not
fake it.

**Which rules need the backend?** Everything that compares a row with another row:
`event.capacity ≤ venue.capacity`, “no overlapping venue booking”, “event is not full”.
See `backend/app/services/events.py` and `backend/app/services/registrations.py`.

**Application feature:** SQL Lab → experiment *constraints*. The experiment runs inside a
transaction that is rolled back, so the demo rows never survive.

---

## Experiment 3 — Set operations

**File:** `database/experiments/03_set_operations.sql`
**Concept:** `UNION` · `UNION ALL` · `INTERSECT` · `EXCEPT`

| # | Statement | Meaning |
| --- | --- | --- |
| 1 | technical **UNION** cultural attendees | attendees of both categories, duplicates removed |
| 2 | technical **UNION ALL** cultural attendees | the same groups, duplicates kept — the row count is larger than in (1) |
| 3 | technical **INTERSECT** sports attendees | attendees that registered for *both* a technical and a sports event |
| 4 | technical **EXCEPT** sports attendees | technical attendees that did *not* register for a sports event |

**Version note:** MySQL supports `INTERSECT`/`EXCEPT` natively from **8.0.31**. The SQL Lab checks
`SELECT VERSION()` at runtime:

* modern server → the native operator is executed,
* older server → the equivalent `EXISTS` / `NOT EXISTS` query is executed and the output states
  that the native operator is unavailable.

**Application feature:** SQL Lab → experiment *set-operations*.

---

## Experiment 4 — String functions

**File:** `database/experiments/04_string_functions.sql`
**Concept:** `CONCAT` · `UPPER` · `LOWER` · `LENGTH` · `CHAR_LENGTH` · `SUBSTRING` · `TRIM` (+ `INSTR`)

| # | Statement | Result |
| --- | --- | --- |
| 1 | attendee rows with `CONCAT(full_name,' <',email,'>')`, `UPPER`, `LOWER`, `LENGTH`, `CHAR_LENGTH`, `SUBSTRING(full_name,1,3)`, `TRIM(organization)` | one row per attendee with all seven functions applied |
| 2 | the same toolbox on `events` (`event_name`, `event_category`) | normalised labels such as `Technical / Opening Tech Summit 2026` |
| 3 | `SUBSTRING(email, INSTR(email,'@') + 1)` | extracts the e-mail domain |

**Note:** in MySQL `LENGTH()` counts bytes and `CHAR_LENGTH()` counts characters; the SQLite
fallback returns the character count for both. The experiment description mentions this.

**Application feature:** SQL Lab → experiment *string-functions*.

---

## Experiment 5 — Aggregate functions

**File:** `database/experiments/05_aggregate_functions.sql`
**Concept:** `COUNT` · `SUM` · `AVG` · `MIN` · `MAX`

| # | Statement | Result |
| --- | --- | --- |
| 1 | `COUNT(*)` on organizers, venues, events, attendees, registrations, payments | the size of the whole database |
| 2 | `AVG/MIN/MAX(registration_count)` over a derived table | average / lowest / highest registrations per event |
| 3 | `MIN/MAX/AVG/SUM(ticket_price)` | free events pull the average down — a nice observation for the viva |
| 4 | `GROUP BY payment_status` with `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` | completed / pending / refunded money |
| 5 | `SUM(amount) WHERE payment_status = 'Completed'` | the collected revenue (refunds are not part of it) |

**Application feature:** SQL Lab → experiment *aggregate-functions*; the same aggregations feed the
dashboard KPIs.

---

## Experiment 6 — GROUP BY and HAVING

**File:** `database/experiments/06_group_by_having.sql`
**Concept:** `GROUP BY` · `HAVING` · configurable thresholds

| # | Statement | Threshold |
| --- | --- | --- |
| 1 | registrations per event, `HAVING COUNT(...) > :threshold` | `threshold` (default 3) — editable in the UI |
| 2 | revenue per event, `HAVING SUM(...) > 0` | – |
| 3 | events grouped by category (`COUNT`, `COUNT DISTINCT organizer_id`, `MIN/MAX(date)`, `SUM(capacity)`) | – |
| 4 | events per organizer (`LEFT JOIN` keeps organizers without events), `HAVING COUNT(...) >= :min_events` | `min_events` (default 1) |
| 5 | venues hosting more than `:venue_threshold` events | `venue_threshold` (default 1) |

The thresholds are **bound parameters**, never concatenated into the SQL text.

**Application feature:** SQL Lab → experiment *group-by-having*; the same grouping powers the
*events by category* chart and the *venue utilisation* report.

---

## Experiment 7 — Nested sub queries

**File:** `database/experiments/07_nested_subqueries.sql`
**Concept:** sub query in `SELECT` / `WHERE` / `HAVING`, correlated sub queries

| # | Statement | Concept |
| --- | --- | --- |
| 1 | events with more registrations than the average event | nested sub query in `HAVING` |
| 2 | attendees registered for events with an above-average ticket price | sub query in `WHERE` (`> (SELECT AVG(ticket_price) FROM events)`) |
| 3 | venues larger than the average venue | the same sub query twice — in `SELECT` and in `WHERE` |
| 4 | registration count per event via `(SELECT COUNT(*) … WHERE r.event_id = e.event_id)` | **correlated** sub query |
| 5 | attendees with more than one registration via `(SELECT COUNT(*) … WHERE r.attendee_id = a.attendee_id)` | **correlated** sub query |

**Application feature:** SQL Lab → experiment *nested-subqueries*; the same idea produces the report
`/api/reports/events-above-average`.

---

## Experiment 8 — Views

**File:** `database/experiments/08_views.sql`
**Concept:** `CREATE VIEW` and reading from views

| # | Statement | Content |
| --- | --- | --- |
| 1 | `SELECT * FROM v_upcoming_events` | upcoming/ongoing events with venue, organizer and free seats |
| 2 | `SELECT * FROM v_event_registration_summary` | registration, waitlist and attendance counters per event |
| 3 | `SELECT * FROM v_event_revenue_summary` | gross / refunded / pending revenue per event |
| 4 | `SELECT * FROM v_venue_utilization` | events hosted, seats offered, registrations, utilisation |
| 5 | `SELECT * FROM v_attendee_registration_history` | registrations, events attended and money paid per attendee |

The definitions live in `database/views.sql` and are created by the application on start-up
(`backend/app/db/views.py`).

**Application feature:** SQL Lab → experiment *views*; the dashboard charts and the reports page
read from exactly these views.

---

## Experiment 9 — Joins

**File:** `database/experiments/09_joins.sql`
**Concept:** `INNER JOIN` · `LEFT JOIN` · multi-table joins · self joins

| # | Statement | Concept |
| --- | --- | --- |
| 1 | events ⋈ organizers ⋈ venues | INNER JOIN, three tables |
| 2 | events `LEFT JOIN` registrations, `HAVING COUNT(...) = 0` | LEFT JOIN keeps events without registrations |
| 3 | registrations ⋈ attendees ⋈ events | multi-table join |
| 4 | payments ⋈ registrations ⋈ attendees ⋈ events | four-table join (money trail) |
| 5 | events ⋈ events (same venue, different dates) | **self join** |
| 6 | registrations ⋈ registrations (same attendee) | **self join** |
| 7 | attendees `LEFT JOIN` registrations `WHERE r.registration_id IS NULL` | anti join — attendees who never registered |
| 8 | events ⋈ events (same venue, **same** date) | self join that must return **no rows** — proof that no venue is double booked |

**Application feature:** SQL Lab → experiment *joins*.

---

## Where the experiments are implemented

| Concern | File |
| --- | --- |
| Experiment definitions (SQL + labels + notes) | `backend/app/queries/sql_lab.py` |
| Runner (executes the predefined statements, captures rows **and** engine errors) | `backend/app/services/sql_lab.py` |
| REST endpoints | `backend/app/api/sql_lab.py` |
| UI | `frontend/src/pages/SqlLabPage.tsx` |
| Generated `.sql` files | `database/experiments/*.sql` |

**Safety:** the endpoint only accepts the key of one of the nine experiments plus a few numeric
thresholds. SQL text is never taken from the browser, so the SQL Lab can not be used to modify or
destroy data. The only statement that changes anything is the disposable scratch table of
experiment 1 — and it is dropped again immediately.
