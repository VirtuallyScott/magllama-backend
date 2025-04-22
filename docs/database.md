# Database

The magllama project uses PostgreSQL as its primary database.

## Schema Features

- All tables include `active_at` and `inactive_at` timestamp columns for soft-deletion and auditability.
- Records are never physically deleted; instead, they are marked as inactive by setting `inactive_at`.
- The `inactivated_by` column (where present) records the user who performed the inactivation.

## CRUD Operations

- **Create:** Insert a new record with `active_at` set to the current timestamp (default).
- **Read:** Filter with `WHERE inactive_at IS NULL` to get only active records.
- **Update:** Update fields as needed; do not change `active_at` or `inactive_at` unless inactivating.
- **Delete (Soft Delete):** Set `inactive_at` to the current timestamp and, if available, set `inactivated_by` to the user performing the action.

## Example Queries

- Get all active projects:
  ```sql
  SELECT * FROM projects WHERE inactive_at IS NULL;
  ```

- Mark a scan as inactive:
  ```sql
  UPDATE scans SET inactive_at = NOW(), inactivated_by = '<user_id>' WHERE id = '<scan_id>';
  ```

- Get all active scan types:
  ```sql
  SELECT * FROM scan_types WHERE inactive_at IS NULL;
  ```

## Initialization

To initialize the database schema:

```bash
psql -U postgres -h <db-host> -d <db-name> -f postgres/init.sql
```
