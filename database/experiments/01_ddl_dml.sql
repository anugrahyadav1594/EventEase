-- ==================================================================
-- Experiment 1: DDL and DML on a disposable demo table
-- DBMS concept: CREATE TABLE / ALTER TABLE / INSERT / UPDATE / SELECT / DELETE / DROP
-- ==================================================================
--
-- The complete data definition and data manipulation life cycle is demonstrated on the throw-away table `eventease_demo_scratch`. No EventEase table is ever dropped by the demo.
--
-- * The scratch table is created, filled, altered, updated, emptied and finally dropped again.
-- * Every statement runs against the live database - the result grid below is the real output.
--
-- These statements are executed by the SQL Lab of the EventEase
-- application (POST /api/sql-lab/experiments/{key}/run).

-- --------------------------------------------------------------------
-- 1. CREATE TABLE eventease_demo_scratch
--    Creates an isolated table with a PRIMARY KEY, a NOT NULL column and a CHECK constraint.
-- --------------------------------------------------------------------
CREATE TABLE eventease_demo_scratch (
    demo_id     INT PRIMARY KEY,
    demo_label  VARCHAR(60) NOT NULL,
    demo_amount DECIMAL(10, 2) NOT NULL,
    CONSTRAINT ck_demo_amount CHECK (demo_amount >= 0)
);

-- --------------------------------------------------------------------
-- 2. INSERT two rows
--    DML: adds two rows to the scratch table.
-- --------------------------------------------------------------------
INSERT INTO eventease_demo_scratch (demo_id, demo_label, demo_amount)
VALUES (1, 'Inserted Row A', 150.00),
       (2, 'Inserted Row B', 275.50);

-- --------------------------------------------------------------------
-- 3. SELECT the inserted rows
--    Reads the rows back - this is the state after the INSERT.
-- --------------------------------------------------------------------
SELECT * FROM eventease_demo_scratch ORDER BY demo_id;

-- --------------------------------------------------------------------
-- 4. ALTER TABLE ... ADD COLUMN
--    DDL: extends the structure of the table without touching the existing rows.
-- --------------------------------------------------------------------
ALTER TABLE eventease_demo_scratch ADD COLUMN demo_note VARCHAR(80) NULL;

-- --------------------------------------------------------------------
-- 5. UPDATE a single row
--    DML: increases the amount of row 1 by 25.00.
-- --------------------------------------------------------------------
UPDATE eventease_demo_scratch
   SET demo_amount = demo_amount + 25.00,
       demo_note = 'updated by the SQL lab'
 WHERE demo_id = 1;

-- --------------------------------------------------------------------
-- 6. SELECT after the UPDATE
--    The new value and the new column are visible.
-- --------------------------------------------------------------------
SELECT * FROM eventease_demo_scratch ORDER BY demo_id;

-- --------------------------------------------------------------------
-- 7. DELETE one row
--    DML: removes row 2 again.
-- --------------------------------------------------------------------
DELETE FROM eventease_demo_scratch WHERE demo_id = 2;

-- --------------------------------------------------------------------
-- 8. SELECT the remaining rows
--    Only row 1 is left in the table.
-- --------------------------------------------------------------------
SELECT COUNT(*) AS rows_remaining FROM eventease_demo_scratch;

-- --------------------------------------------------------------------
-- 9. DROP the disposable table
--    DDL: the scratch table is removed again - the EventEase tables are never touched.
-- --------------------------------------------------------------------
DROP TABLE eventease_demo_scratch;
