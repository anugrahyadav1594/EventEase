# EventEase — Event Management System (DBMS Mini Project)

> A full-stack event management system for colleges, clubs and event organisers, built around a
> **real relational database**. Every number that appears in the dashboard is calculated by SQL —
> nothing is hard coded, nothing is faked.

EventEase demonstrates the DBMS concepts of a college practical in one coherent application:
DDL & DML, constraints, set operations, string functions, aggregate functions, `GROUP BY` / `HAVING`,
nested sub queries, views and joins.

---

## Table of contents

1. [Introduction & problem statement](#1-introduction--problem-statement)
2. [Objectives and scope](#2-objectives-and-scope)
3. [Features](#3-features)
4. [Technology stack](#4-technology-stack)
5. [Architecture](#5-architecture)
6. [Database design](#6-database-design)
7. [The nine DBMS experiments](#7-the-nine-dbms-experiments)
8. [Installation & setup](#8-installation--setup)
9. [Running the project](#9-running-the-project)
10. [API reference](#10-api-reference)
11. [Testing](#11-testing)
12. [Project structure](#12-project-structure)
13. [Troubleshooting](#13-troubleshooting)
14. [Faculty viva demonstration guide](#14-faculty-viva-demonstration-guide)
15. [Verification status & limitations](#15-verification-status--limitations)

---

## 1. Introduction & problem statement

### Problem statement

Colleges, clubs and small event companies usually run their events with spreadsheets and chat
messages. That leads to four recurring problems:

| Problem | Consequence |
| --- | --- |
| Registrations are kept in a spreadsheet | Duplicate registrations, lost attendees, no audit trail |
| Venue bookings are made over chat | Two events in the same hall at the same time, unhappy organisers |
| Payments are noted in a notebook | Wrong revenue figures, refunds double counted |
| Nobody can answer simple questions | “How many people came to the sports day?”, “Which venue is under used?” |

### Solution

EventEase replaces the spreadsheet with a normalised **MySQL 8.0** database and a FastAPI +
React dashboard:

* every business rule is either a **database constraint** (primary key, foreign key, unique, not
  null, check) or a **transactional backend check** (capacity, double booking),
* every report is a **read-only SQL query** whose text is shown in the UI,
* the **SQL Lab** executes the nine mandatory DBMS experiments against the live database and shows
  the real result of every statement — including the error messages produced by the engine when a
  constraint is violated.

---

## 2. Objectives and scope

### Objectives

1. Design and implement a normalised relational schema with primary keys, foreign keys, `UNIQUE`,
   `NOT NULL`, `CHECK` constraints and useful indexes.
2. Implement CRUD operations for organizers, venues, events, attendees, registrations and payments
   through a documented REST API with proper status codes and readable error messages.
3. Enforce the business rules that a `CHECK` constraint cannot express:
   * event capacity ≤ venue capacity,
   * no overlapping bookings for the same venue and time slot,
   * no duplicate registration of the same attendee for the same event,
   * no registration beyond the event capacity (transactional, with a row lock).
4. Provide reports for events, venues, attendees, revenue and attendance — all calculated by SQL.
5. Demonstrate the nine DBMS practical experiments on the *live* database.
6. Keep the project simple enough to explain in a viva and to run on a laptop.

### Scope

**In scope:** event catalogue, venues, organizers, attendees, registrations, attendance, ticket
types, payment records (Cash / UPI / Card / Bank Transfer), revenue reporting, SQL laboratory.

**Out of scope (deliberately):** a real payment gateway, e-mail delivery, authentication/roles,
seat maps, mobile apps. Payment data is *recorded* in the database — no money is moved.

---

## 3. Features

| Area | Features |
| --- | --- |
| **Dashboard** | 8 live KPIs, registrations-by-event chart, revenue-by-category doughnut, attendance-by-event chart, venue-utilisation chart, upcoming schedule, most popular events |
| **Events** | Search, filter by category/status/organizer/venue, pagination, create/edit/view/delete, capacity indicator, venue & organizer details |
| **Venues** | Search, availability filter, create/edit/delete, scheduled events per venue, capacity and utilisation |
| **Organizers** | Search by name/organisation, create/edit/delete, number of managed events and registrations |
| **Attendees** | Search by name/e-mail, create/edit/delete, registration history, events attended, money paid |
| **Registrations** | Register attendee → event, duplicate protection, capacity protection, status transitions (Registered/Confirmed/Waitlisted/Cancelled), attendance (Present/Absent), filters |
| **Payments** | Record payments, status transitions (Pending/Completed/Refunded), method filters, collected / pending / refunded totals |
| **Reports** | 7 read-only reports, each showing the **executed SQL**, the result set and an explanation |
| **SQL Lab** | The 9 DBMS experiments, executed statement by statement, with the engine's own error messages for constraint violations |

---

## 4. Technology stack

| Layer | Technology | Version |
| --- | --- | --- |
| Database | MySQL | 8.0 (InnoDB, `utf8mb4`) |
| DB access | SQLAlchemy Core + explicit SQL | 2.x |
| Driver | PyMySQL | 1.1+ |
| Backend | FastAPI + Uvicorn | 0.115+ / 0.30+ |
| Validation | Pydantic v2 | 2.9+ |
| Frontend | React + TypeScript + Vite | 18 / 5.x / 6.x |
| Charts | Recharts | 2.x |
| Routing | React Router | 6.x |
| Styling | Hand-written CSS design system (dark navy + neutral) | – |
| Tests | pytest + FastAPI TestClient | 8+ |

---

## 5. Architecture

```
┌────────────────────┐        ┌─────────────────────┐        ┌──────────────────────┐
│  React 18 + Vite   │  HTTP  │   FastAPI (REST)    │  SQL   │   MySQL 8.0          │
│  TypeScript, CSS   │ ─────► │  Pydantic validation│ ─────► │  6 tables + 5 views  │
│  Recharts          │  JSON  │  SQLAlchemy Core    │        │  constraints+indexes │
└────────────────────┘        └─────────────────────┘        └──────────────────────┘
        │                              │
        │  /api proxy (Vite)          │  read-only SQL only
        └────────────────────────────►│  SQL Lab executes predefined scripts
```

* The **database is the single source of truth** — the frontend never computes a metric itself.
* The **SQL Lab** can only execute the nine predefined experiment scripts; it never accepts SQL
  from the browser.
* All user input reaches the database through **bound parameters** — no string concatenation of
  untrusted input.

---

## 6. Database design

### 6.1 ER diagram

```mermaid
erDiagram
    ORGANIZERS ||--o{ EVENTS : organises
    VENUES     ||--o{ EVENTS : hosts
    ATTENDEES  ||--o{ REGISTRATIONS : "registers for"
    EVENTS     ||--o{ REGISTRATIONS : "receives"
    REGISTRATIONS ||--o{ PAYMENTS : "is paid by"

    ORGANIZERS {
        int organizer_id PK
        varchar organizer_name "NOT NULL"
        varchar email UK "NOT NULL, UNIQUE"
        varchar phone
        varchar organization_name
        datetime created_at "DEFAULT CURRENT_TIMESTAMP"
    }

    VENUES {
        int venue_id PK
        varchar venue_name "NOT NULL"
        varchar location "NOT NULL"
        int capacity "CHECK capacity > 0"
        varchar venue_type
        enum availability_status "Available|Unavailable|Maintenance"
    }

    EVENTS {
        int event_id PK
        varchar event_name "NOT NULL"
        text description
        varchar event_category "NOT NULL, indexed"
        int organizer_id FK "RESTRICT"
        int venue_id FK "RESTRICT"
        date event_date "indexed"
        time start_time
        time end_time "CHECK end_time > start_time"
        int capacity "CHECK capacity > 0"
        decimal ticket_price "CHECK ticket_price >= 0"
        enum event_status "Upcoming|Ongoing|Completed|Cancelled"
        datetime created_at
    }

    ATTENDEES {
        int attendee_id PK
        varchar full_name "NOT NULL"
        varchar email UK "NOT NULL, UNIQUE"
        varchar phone
        varchar organization
        datetime registration_date
    }

    REGISTRATIONS {
        int registration_id PK
        int attendee_id FK "RESTRICT, UNIQUE(attendee_id,event_id)"
        int event_id FK "RESTRICT"
        datetime registration_date
        enum registration_status "Registered|Confirmed|Cancelled|Waitlisted"
        enum attendance_status "Not Marked|Present|Absent"
        varchar ticket_type
        decimal ticket_price "CHECK ticket_price >= 0"
    }

    PAYMENTS {
        int payment_id PK
        int registration_id FK "RESTRICT"
        decimal amount "CHECK amount >= 0"
        enum payment_method "Cash|UPI|Card|Bank Transfer"
        enum payment_status "Pending|Completed|Refunded"
        varchar transaction_reference UK "NULL allowed"
        datetime payment_date
    }
```

### 6.2 Tables, constraints and indexes

| Table | Primary key | Foreign keys | Unique | Check | Not null | Indexes |
| --- | --- | --- | --- | --- | --- | --- |
| `organizers` | `organizer_id` | – | `email` | – | name, email, created_at | organization_name |
| `venues` | `venue_id` | – | – | `capacity > 0` | name, location, capacity, availability_status | availability_status, venue_name |
| `events` | `event_id` | `organizer_id → organizers`, `venue_id → venues` (both `ON DELETE RESTRICT`) | – | `capacity > 0`, `ticket_price >= 0`, `end_time > start_time` | name, category, dates, times, capacity, price, status | event_date, event_category, event_status, organizer_id, venue_id |
| `attendees` | `attendee_id` | – | `email` | – | name, email, registration_date | full_name |
| `registrations` | `registration_id` | `attendee_id → attendees`, `event_id → events` (`RESTRICT`) | `(attendee_id, event_id)` | `ticket_price >= 0` | all columns except phone/ticket_type | event_id, attendee_id, registration_status, attendance_status |
| `payments` | `payment_id` | `registration_id → registrations` (`RESTRICT`) | `transaction_reference` | `amount >= 0` | amount, method, status, date | registration_id, payment_status |

**Referential actions:** every foreign key uses `ON DELETE RESTRICT`. An event with registrations,
a venue with events or an organizer with events can therefore never be deleted by accident — the
API turns the database error into a readable `409 Conflict` message.

### 6.3 Business rules that a CHECK constraint cannot express

| Rule | Where it is enforced | How |
| --- | --- | --- |
| Event capacity ≤ venue capacity | Backend | `services/events.py::assert_capacity_within_venue` — reads the venue capacity before the insert |
| No overlapping venue booking | Backend + transaction | `assert_venue_available` — compares `start_time < other.end_time AND end_time > other.start_time` for the same venue and date |
| No duplicate registration | **Database** (`UNIQUE`) *and* backend | `UNIQUE (attendee_id, event_id)` + a pre-check inside the same transaction for a friendly message |
| No registration beyond capacity | Backend + transaction | `SELECT … FOR UPDATE` on the event row, then count the active registrations |
| Payment status transitions | Backend | Allowed-transition table in `services/payments.py` |
| Revenue calculation | Database | Only `payment_status = 'Completed'` counts; a refund flips the row to `Refunded` so it can never be counted twice |

### 6.4 The five views

| View | Purpose |
| --- | --- |
| `v_upcoming_events` | Upcoming/ongoing events with venue, organizer and free seats |
| `v_event_registration_summary` | Registration, confirmation, waitlist and attendance counters per event |
| `v_event_revenue_summary` | Gross / refunded / pending revenue per event |
| `v_venue_utilization` | Events hosted, seats offered, registrations and utilisation per venue |
| `v_attendee_registration_history` | Registrations, events attended and money paid per attendee |

The dashboard, the reports and the SQL Lab all read from these views — the view definitions live in
`database/views.sql` and are generated from `backend/app/db/views.py`.

### 6.5 Demo dataset

`backend/app/db/seed_data.py` is the single source of truth for the demo data; the Python seeder
and `database/seed.sql` are generated from it and therefore always contain the same rows with the
same primary keys (organizers 1–6, venues 1–10, events 1–20, attendees 1–37, registrations 1–82,
payments 1–66).

| Entity | Rows | What the data demonstrates |
| --- | --- | --- |
| Organizers | 6 | Six different organisations/clubs |
| Venues | 10 | Auditorium, hall, lab, open ground … different capacities |
| Events | 20 | 5 categories, all four statuses (9 completed, 1 ongoing, 9 upcoming, 1 cancelled), free **and** paid events, two events without a single registration |
| Attendees | 37 | 34 with registrations, 3 without (they make the "never registered" report meaningful) |
| Registrations | 82 | Registered / Confirmed / Cancelled / Waitlisted, attendance Present / Absent / Not Marked |
| Payments | 66 | 42 completed, 20 pending, 4 refunded — every status and every method is represented |

No venue is booked twice at the same time and no attendee is registered twice for the same event.

---

## 7. The nine DBMS experiments

| # | Experiment | File | SQL concepts | Where in the app |
| --- | --- | --- | --- | --- |
| 1 | DDL and DML | `database/experiments/01_ddl_dml.sql` | `CREATE`, `ALTER`, `INSERT`, `UPDATE`, `SELECT`, `DELETE`, `DROP` | SQL Lab → *DDL and DML* (disposable scratch table) |
| 2 | Constraints | `database/experiments/02_constraints.sql` | `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK` | SQL Lab → *Constraints* (valid + rejected statements) |
| 3 | Set operations | `database/experiments/03_set_operations.sql` | `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT` | SQL Lab → *Set operations* |
| 4 | String functions | `database/experiments/04_string_functions.sql` | `CONCAT`, `UPPER`, `LOWER`, `LENGTH`, `CHAR_LENGTH`, `SUBSTRING`, `TRIM`, `INSTR` | SQL Lab → *String functions* |
| 5 | Aggregate functions | `database/experiments/05_aggregate_functions.sql` | `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` | SQL Lab → *Aggregate functions* |
| 6 | GROUP BY and HAVING | `database/experiments/06_group_by_having.sql` | `GROUP BY`, `HAVING`, configurable thresholds | SQL Lab → *GROUP BY and HAVING* |
| 7 | Nested sub queries | `database/experiments/07_nested_subqueries.sql` | sub query in `SELECT`/`WHERE`/`HAVING`, correlated sub query | SQL Lab → *Nested subqueries* |
| 8 | Views | `database/experiments/08_views.sql` | `CREATE VIEW`, reading from views | SQL Lab → *Views*, dashboard, reports |
| 9 | Joins | `database/experiments/09_joins.sql` | `INNER JOIN`, `LEFT JOIN`, multi-table joins, self joins | SQL Lab → *Joins* |

The detailed mapping (statement by statement) is in
[`DBMS_EXPERIMENT_MAPPING.md`](DBMS_EXPERIMENT_MAPPING.md).

> **INTERSECT / EXCEPT:** MySQL supports them natively from **8.0.31** onwards. The SQL Lab detects
> the server version at runtime: on a modern MySQL it runs the native operator, on an older server
> it runs the equivalent `EXISTS` / `NOT EXISTS` query and says so in the output.

---

## 8. Installation & setup

### 8.1 MySQL 8.0

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y mysql-server
sudo service mysql start

# macOS (Homebrew)
brew install mysql && brew services start mysql
```

Create the database and the application user:

```sql
CREATE DATABASE eventease CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'eventease'@'localhost' IDENTIFIED BY 'eventease';
GRANT ALL PRIVILEGES ON eventease.* TO 'eventease'@'localhost';
FLUSH PRIVILEGES;
```

Load the schema, the demo data and the views:

```bash
mysql -u eventease -p eventease < database/schema.sql
mysql -u eventease -p eventease < database/seed.sql
mysql -u eventease -p eventease < database/views.sql
```

> `database/schema.sql` contains `CREATE DATABASE …; USE eventease;` as well, so it can also be run
> with `mysql -u eventease -p < database/schema.sql`.

### 8.2 Python environment

```bash
git clone <this repository> eventease && cd eventease
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 8.3 Frontend

```bash
cd frontend
npm install
```

### 8.4 Configuration

```bash
cp .env.example .env
```

| Variable | Default | Meaning |
| --- | --- | --- |
| `DATABASE_URL` | `mysql+pymysql://eventease:eventease@127.0.0.1:3306/eventease` | SQLAlchemy connection URL |
| `SQL_ECHO` | `false` | Log every SQL statement |
| `AUTO_INIT_DB` | `false` | Create schema + demo data when the API starts |
| `CORS_ORIGINS` | `http://localhost:5173,…` | Allowed browser origins |
| `VITE_API_BASE_URL` | *(empty)* | API base URL of the frontend (empty = use the Vite proxy) |
| `VITE_PROXY_TARGET` | `http://127.0.0.1:8000` | Proxy target of the Vite dev server |

---

## 9. Running the project

Two terminals:

```bash
# Terminal 1 – backend  (http://127.0.0.1:8000, docs at /docs)
source .venv/bin/activate
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

```bash
# Terminal 2 – frontend (http://localhost:5173)
cd frontend
npm run dev
```

### Initialising the database

```bash
# option A – the Python bootstrap (portable, works with MySQL and SQLite)
python backend/scripts/init_db.py

# option B – execute the SQL scripts from database/ (MySQL)
python backend/scripts/init_db.py --sql

# option C – start from scratch (drops every table first)
python backend/scripts/init_db.py --reset
```

### Regenerating the SQL files

`database/schema.sql`, `database/seed.sql`, `database/views.sql` and the nine experiment files are
generated from the Python source of truth:

```bash
python backend/scripts/generate_sql.py
```

### Checking the SQL scripts without a MySQL server

`backend/scripts/validate_sql_scripts.py` parses `database/schema.sql` and `database/seed.sql` and
verifies — without a database server — that every foreign key of the sample data points to an
existing row, that no `UNIQUE` column contains a duplicate, and that every `CHECK` constraint of the
schema is satisfied:

```bash
python backend/scripts/validate_sql_scripts.py
# ✓ schema.sql, seed.sql and views.sql are consistent
```

### Running without a MySQL server (demo / CI)

Set `DATABASE_URL=sqlite:///./eventease.db` and `AUTO_INIT_DB=true`. The application then creates
the schema, the views and the demo data on the first start. This fallback exists so that the
project can be demonstrated on a machine without MySQL — the MySQL scripts remain the reference
implementation.

---

## 10. API reference

Interactive documentation: **http://127.0.0.1:8000/docs** (Swagger UI) and `/redoc`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Liveness probe + row counts + server version |
| `GET` | `/api/dashboard` | KPIs, charts, popular events, upcoming schedule |
| `GET` | `/api/organizers` | List (search, pagination) |
| `POST` | `/api/organizers` | Create |
| `PUT` | `/api/organizers/{id}` | Update |
| `DELETE` | `/api/organizers/{id}` | Delete (409 if events exist) |
| `GET` | `/api/venues` | List (search, availability, pagination) |
| `POST` | `/api/venues` | Create |
| `PUT` | `/api/venues/{id}` | Update |
| `DELETE` | `/api/venues/{id}` | Delete (409 if events exist) |
| `GET` | `/api/venues/{id}/events` | Schedule of a venue |
| `GET` | `/api/events` | List (search, category, status, organizer, venue, dates, pagination) |
| `GET` | `/api/events/{id}` | Detail incl. registration counters |
| `POST` | `/api/events` | Create (capacity & double-booking checks) |
| `PUT` | `/api/events/{id}` | Update (same checks) |
| `DELETE` | `/api/events/{id}` | Delete (409 if registrations exist) |
| `GET` | `/api/attendees` | List (search, pagination) |
| `GET` | `/api/attendees/{id}` | Detail |
| `GET` | `/api/attendees/{id}/registrations` | Registration history |
| `POST` | `/api/attendees` | Create |
| `PUT` | `/api/attendees/{id}` | Update |
| `DELETE` | `/api/attendees/{id}` | Delete (409 if registrations exist) |
| `GET` | `/api/registrations` | List (event, attendee, status, attendance, search) |
| `POST` | `/api/registrations` | Register an attendee (duplicate + capacity checks) |
| `PATCH` | `/api/registrations/{id}/status` | Change the registration status |
| `PATCH` | `/api/registrations/{id}/attendance` | Mark Present / Absent |
| `GET` | `/api/payments` | List + revenue summary (status, method, event) |
| `POST` | `/api/payments` | Record a payment |
| `PATCH` | `/api/payments/{id}/status` | Complete / refund a payment |
| `GET` | `/api/reports` | Overview of the seven reports |
| `GET` | `/api/reports/event-registrations` | Registrations per event |
| `GET` | `/api/reports/event-revenue` | Revenue per event |
| `GET` | `/api/reports/venue-utilization` | Venue utilisation |
| `GET` | `/api/reports/popular-events` | Top-N events (`?limit=`) |
| `GET` | `/api/reports/attendee-history` | Registration history per attendee |
| `GET` | `/api/reports/attendance-summary` | Attendance per completed event |
| `GET` | `/api/reports/events-above-average` | Events above the average registration count |
| `GET` | `/api/sql-lab/experiments` | The nine experiments |
| `POST` | `/api/sql-lab/experiments/{key}/run` | Execute one predefined experiment |

### Error handling

| Situation | Status | Message (example) |
| --- | --- | --- |
| Duplicate e-mail / registration | `409` | *A attendee with the same unique value already exists.* |
| Unknown foreign key | `404` | *Attendee 987654 was not found.* |
| Capacity larger than the venue | `422` | *Event capacity (9999) cannot exceed the capacity of Design Studio (45 seats).* |
| Double booking | `409` | *Venue is already booked on 2026-11-02 for 'X' (10:00 - 16:00).* |
| Event full | `409` | *This event is full: 60 of 60 seats are taken.* |
| Delete with dependents | `409` | *This organizer is still referenced by other records.* |
| Invalid payload | `422` | Pydantic validation message |

---

## 11. Testing

```bash
source .venv/bin/activate
cd backend && python -m pytest tests -q
```

The test-suite **never touches a developer database**: `backend/tests/conftest.py` creates an
isolated SQLite database in the temp directory, fills it with the demo data and removes it
afterwards.

Covered scenarios:

* health check and dashboard endpoint,
* create / read / update / delete for events, venues, organizers and attendees,
* duplicate attendee e-mail is rejected,
* duplicate registration is rejected,
* registration beyond the event capacity is rejected,
* overlapping venue booking is rejected,
* invalid foreign keys are rejected (404),
* invalid time window and negative amounts are rejected (422),
* payment status transitions (including the illegal `Refunded → Completed`),
* revenue counts only completed payments and never counts a refund twice,
* all seven reports return the documented shape,
* all nine SQL Lab experiments execute; the constraint experiment really produces database errors
  and leaves no rows behind.

Frontend checks:

```bash
cd frontend
npm run typecheck     # TypeScript without emitting
npm run build         # production build
```

---

## 12. Project structure

```
eventease/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers (one per resource)
│   │   ├── db/             # engine, schema metadata, seed data, views
│   │   ├── models/         # SQLAlchemy Core table definitions
│   │   ├── queries/        # report SQL + the nine SQL Lab experiments
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # business rules (capacity, booking, payments)
│   │   ├── config.py       # environment configuration
│   │   └── main.py         # application entry point
│   ├── scripts/
│   │   ├── init_db.py      # database bootstrap (Python or SQL scripts)
│   │   ├── generate_sql.py # regenerates database/*.sql
│   │   └── validate_sql_scripts.py # static FK/UNIQUE/CHECK check of the SQL
│   ├── tests/              # pytest suite
│   └── requirements.txt
├── database/
│   ├── schema.sql          # MySQL 8 DDL (tables, constraints, indexes)
│   ├── seed.sql            # demo data
│   ├── views.sql           # the five views
│   └── experiments/        # 01_ddl_dml.sql … 09_joins.sql
├── frontend/
│   ├── src/
│   │   ├── components/     # layout, tables, forms, charts, SQL block, toasts
│   │   ├── pages/          # dashboard, events, venues, organizers, attendees,
│   │   │                   # registrations, payments, reports, SQL lab
│   │   ├── services/       # typed API client
│   │   ├── types/          # TypeScript types
│   │   └── styles.css      # design system
│   └── package.json
├── .env.example
├── DBMS_EXPERIMENT_MAPPING.md
└── README.md
```

---

## 13. Troubleshooting

| Symptom | Cause | Solution |
| --- | --- | --- |
| `Can't connect to local MySQL server` | MySQL is not running | `sudo service mysql start` |
| `Access denied for user 'eventease'` | Wrong credentials in `.env` | Recreate the user as shown in §8.1 |
| `Unknown database 'eventease'` | Schema not loaded | `mysql -u eventease -p eventease < database/schema.sql` |
| Frontend shows “database offline” | Backend not running / wrong `DATABASE_URL` | Start uvicorn, check `GET /api/health` |
| CORS error in the browser console | Frontend origin not allowed | Add the origin to `CORS_ORIGINS` |
| `Table 'eventease.venues' doesn't exist'` | Views need the tables | Run `database/schema.sql` before `database/views.sql` |
| `CHECK constraint failed` on insert | The demo data violates a constraint | Only happens when the schema was changed by hand |
| Port 5173/8000 already in use | Another process | `npm run dev -- --port 5174` / `uvicorn … --port 8001` and adapt `VITE_PROXY_TARGET` |

---

## 14. Faculty viva demonstration guide

A 10-minute walkthrough that touches every DBMS concept:

1. **Setup (30 s)** – Show `database/schema.sql` (DDL with `PRIMARY KEY`, `FOREIGN KEY … ON DELETE
   RESTRICT`, `UNIQUE`, `CHECK`) and `database/views.sql`.
2. **Dashboard (60 s)** – Every KPI comes from SQL; open the browser console/network tab and show
   that `/api/dashboard` is one `GET` request; mention the views that feed the charts.
3. **Create an event (60 s)** – Enter a capacity of 9999 for a 45-seat venue → the API answers
   *“Event capacity cannot exceed the capacity of Design Studio”*. Then book the same venue at an
   overlapping time → *“Venue is already booked”*. Explain that a `CHECK` constraint can not look
   into another table, therefore this is a transactional backend check.
4. **Register an attendee (60 s)** – Register the same attendee twice → *“already registered”*;
   fill an event to the last seat → *“This event is full”*. Point at the
   `UNIQUE (attendee_id, event_id)` constraint and the `SELECT … FOR UPDATE` in the code.
5. **Payments (60 s)** – Complete a payment → the revenue KPI grows; refund it → the refunded
   amount is shown but the collected revenue shrinks again. Explain that only `Completed` counts.
6. **Reports (90 s)** – Open *Reports → Revenue per event*; point at the SQL block: it is exactly
   the statement the backend executed, with the `CASE` expression that separates completed,
   refunded and pending money.
7. **SQL Lab (3 min)** – Run experiment 2 (constraints): valid inserts succeed, the invalid ones
   are rejected by the engine and the MySQL error code/message is displayed. Then run experiment 9
   (joins) and show the self join that proves that no venue is double booked (empty result).
8. **Closing (30 s)** – Open `DBMS_EXPERIMENT_MAPPING.md` and show that each of the nine
   experiments maps to a SQL file, to concrete queries and to a feature of the running application.

Questions that are usually asked:

* *Why `RESTRICT` and not `CASCADE`?* — `CASCADE` would silently delete registrations and payments
  (and their money records) when a venue is deleted. `RESTRICT` protects the history; the API
  turns the error into a friendly message.
* *How do you prevent double booking?* — A `CHECK` constraint can not compare two rows, so the
  overlap check (`start < other.end AND end > other.start`) runs inside a transaction together with
  the insert.
* *How is revenue calculated?* — `SUM(amount)` restricted to `payment_status = 'Completed'`; a
  refund changes the status, therefore the money is never counted twice.
* *Why are the SQL Lab queries not editable?* — To keep the SQL Lab read-only. Only the nine
  predefined scripts can be executed; the browser can never send SQL to the server.

---

## 15. Verification status & limitations

### What was verified in this environment

| Check | Result |
| --- | --- |
| Backend test-suite (`pytest`) | **58 passed** |
| Frontend type check + production build (`tsc -b && vite build`) | **passed** |
| All REST endpoints (CRUD, filters, pagination) | **exercised** |
| All 7 reports | **executed, results verified against the database** |
| All 9 SQL Lab experiments | **executed, output and constraint errors verified** |
| Static check of the MySQL scripts (`validate_sql_scripts.py`) | **passed** (FK, UNIQUE and CHECK constraints of the seed data) |
| Frontend ↔ backend integration (Vite proxy) | **working end to end** |

### Limitation — MySQL could not be installed in the development sandbox

The sandbox used to build this project only allows outbound connections to PyPI, npm and GitHub;
the Debian package mirrors and `dev.mysql.com` are unreachable, so **no MySQL server could be
installed or started here**. The following therefore still needs to be executed once on a machine
with MySQL 8.0:

```bash
mysql -u eventease -p eventease < database/schema.sql   # DDL
mysql -u eventease -p eventease < database/seed.sql     # demo data
mysql -u eventease -p eventease < database/views.sql    # views
cd backend && python -m pytest tests -q                  # same suite, now against MySQL
```

Everything else was executed against the **SQLite fallback** of the same application (same schema,
same constraints, same SQL). Two dialect differences are handled transparently by the application
and are marked in the UI:

* `INTERSECT` / `EXCEPT` — native in MySQL ≥ 8.0.31 and in SQLite; on older MySQL servers the SQL
  Lab falls back to `EXISTS` / `NOT EXISTS` and says so.
* `LENGTH()` returns bytes in MySQL and characters in SQLite — the SQL Lab notes this in the
  experiment description.

### Other limitations

* No authentication — every visitor can change the data (acceptable for a lab project, not for
  production).
* No real payment gateway: payments are *records*, no money is transferred.
* The demo data is fictional; e-mail addresses use the reserved `.edu`/example domains.

---

## License

Educational project — free to use for college submissions and demonstrations.
