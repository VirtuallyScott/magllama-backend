# PostgreSQL Schema and CRUD Operations

## Overview

This directory contains the database schema and initialization scripts for the magllama API. The schema is designed to support robust auditability and soft-deletion for all records.

## Table Design

- All tables include `active_at` and `inactive_at` timestamp columns.
- Records are **never physically deleted** from the database. Instead, they are marked as inactive by setting the `inactive_at` column (and optionally `inactivated_by`).
- The `active_at` column records when the record became active.
- The `inactive_at` column records when the record was marked as inactive (soft-deleted).
- The `inactivated_by` column (where present) records the user who performed the inactivation.
- **Indices**: All major tables have indices on `inactive_at` and other frequently queried columns (such as foreign keys and unique fields) to improve query performance.

## CRUD Operations

### Create

- Insert a new record with `active_at` set to the current timestamp (default).
- The record is considered active as long as `inactive_at` is `NULL`.

### Read

- To fetch only active records, always filter with `WHERE inactive_at IS NULL`.
- To fetch all records (including inactive), omit this filter.

### Update

- Update fields as needed. Updates do not affect the `active_at` or `inactive_at` columns unless the record is being inactivated.

### Delete (Soft Delete)

- **No physical DELETE is performed.**
- To "delete" a record, set `inactive_at` to the current timestamp and, if available, set `inactivated_by` to the user performing the action.
- Example:
  ```sql
  UPDATE projects SET inactive_at = NOW(), inactivated_by = '<user_id>' WHERE id = '<project_id>';
  ```
- **Preventing Physical Deletes:**  
  There is no built-in PostgreSQL feature to prevent `DELETE` at the table level, but you can enforce this at the application level (never use `DELETE FROM ...` in your code).  
  For extra safety, you can add a trigger to each table to raise an exception if a `DELETE` is attempted.  
  Example trigger:
  ```sql
  CREATE OR REPLACE FUNCTION prevent_delete() RETURNS trigger AS $$
  BEGIN
    RAISE EXCEPTION 'Physical DELETEs are not allowed. Use soft-delete (inactive_at) instead.';
    RETURN NULL;
  END;
  $$ LANGUAGE plpgsql;

  -- Add to a table, e.g. projects:
  CREATE TRIGGER projects_no_delete
    BEFORE DELETE ON projects
    FOR EACH ROW EXECUTE FUNCTION prevent_delete();
  ```
  Repeat for each table as needed.

### Reactivation

- If you wish to reactivate a record, set `inactive_at` and `inactivated_by` back to `NULL` and update `active_at` as needed.

## Example Query Patterns

- **Get all active projects:**
  ```sql
  SELECT * FROM projects WHERE inactive_at IS NULL;
  ```

- **Mark a scan as inactive:**
  ```sql
  UPDATE scans SET inactive_at = NOW(), inactivated_by = '<user_id>' WHERE id = '<scan_id>';
  ```

- **Get all active scan types:**
  ```sql
  SELECT * FROM scan_types WHERE inactive_at IS NULL;
  ```

## Notes

- This approach ensures a full audit trail and supports regulatory compliance.
- All application-level "delete" operations should use this soft-delete pattern.
- Never use `DELETE FROM ...` in application code.
- For extra safety, you can add a trigger to each table to prevent physical deletes (see above).
