# API

The magllama API provides endpoints for managing users, projects, roles, permissions, secrets, scan types, scans, and more.

## Key Endpoints

### Projects

- `POST /projects` — Create a new project.
- `GET /projects` — List all projects (optionally include inactive).
- `DELETE /projects/{project_id}` — Mark a project as inactive.
- `POST /project_members` — Add a user to a project with a specific role.
- `GET /project_members/{project_id}` — List all members of a project.

### Scans

- `POST /scans` — Create a new scan for a project.
- `GET /scans` — List all scans (optionally filter by project, user, or scan type).
- `GET /scans/{scan_id}` — Retrieve a scan by ID.
- `PUT /scans/{scan_id}` — Update scan result or metadata.
- `DELETE /scans/{scan_id}` — Mark a scan as inactive (soft delete).

### Scan Types

- `POST /scan_types` — Create a new scan type.
- `GET /scan_types` — List all scan types.
- `GET /scan_types/{scan_type_id}` — Retrieve a scan type by ID.
- `PUT /scan_types/{scan_type_id}` — Update a scan type.
- `DELETE /scan_types/{scan_type_id}` — Delete a scan type.

### Secrets

- `POST /secrets` — Create a new secret (user or project level).
- `GET /secrets/{secret_id}` — Retrieve secret metadata (value not included).
- `POST /secrets/{secret_id}/reveal` — Retrieve decrypted secret value (requires explicit permission).
- `PUT /secrets/{secret_id}` — Update secret (including rotation).
- `POST /secrets/{secret_id}/rotate` — Rotate secret value.
- `POST /secrets/{secret_id}/revoke` — Revoke secret.

### API Keys

- `POST /api_keys/user` — Create a new API key for the authenticated user.
- `POST /api_keys/project` — Create a new API key scoped to a project.
- `DELETE /api_keys/{api_key_id}` — Deactivate (revoke) an API key.

### Roles & Permissions

- `POST /roles` — Create a new role.
- `GET /roles` — List all roles.
- `POST /permissions` — Create a new permission.
- `GET /permissions` — List all permissions.

### Groups and Group-based Project Permissions

- `POST /groups` — Create a new group.
- `GET /groups` — List all groups.
- `POST /user_groups` — Add a user to a group.
- `GET /user_groups/{user_id}` — List all groups for a user.
- `POST /project_group_members` — Assign a group to a project with a specific role.
- `GET /project_group_members/{project_id}` — List all group memberships for a project.

Group membership can be used to grant project access and permissions to all users in a group.

## Security

- All endpoints require authentication and appropriate permissions.
- See the OpenAPI docs at `/docs` for full details.
