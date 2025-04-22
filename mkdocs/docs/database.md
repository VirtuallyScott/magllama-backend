# Database

The magllama project uses PostgreSQL as its primary database.

## Schema Features

- All tables include `active_at` and `inactive_at` timestamp columns for soft-deletion and auditability.
- Records are never physically deleted; instead, they are marked as inactive by setting `inactive_at`.
- The `inactivated_by` column (where present) records the user who performed the inactivation.
- **Groups**: Users can belong to groups, and groups can be assigned to projects with roles, enabling group-based project permissions.

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

## Database Credentials and Permissions for the API

For best security and operational practice:

- **Create a dedicated PostgreSQL user for the API** (see `postgres/README.md` for full details).
- **Grant only the minimum required permissions**: `SELECT`, `INSERT`, and `UPDATE` on all tables, and `USAGE` on the schema and sequences. Do **not** grant `DELETE`, `ALTER`, or `TRUNCATE`.
- **Never use the superuser or default `postgres` user for the application.**
- **Set the `DATABASE_URL` in your `.env` file** to use the dedicated application user, e.g.:
  ```
  DATABASE_URL=postgresql://magllama_app:your_strong_password@db:5432/postgres
  ```
- **All deletes are handled by setting `inactive_at` (soft delete).** The application user should not be able to physically delete or alter tables.

See also the "Creating a Dedicated PostgreSQL User for the Application" section in `postgres/README.md` for SQL commands and further guidance.
