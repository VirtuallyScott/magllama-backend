# Identity Provider Integration Readiness

This API is designed to support pluggable external Identity Providers (IdPs) such as LDAP/Active Directory, OpenLDAP, OAuth2, SAML, and OpenID Connect.

## Database Support

- The `users` table includes `external_id` and `idp_provider` columns to store references to external identities.
- Added `api_keys` table for secure API key management with user-level and project-level keys.
- Added `secrets` table for secure encrypted secrets management with full lifecycle tracking.

## Authentication Endpoints

The following placeholder endpoints are available for future implementation of IdP authentication:

- `POST /auth/oauth2` - OAuth2 login with token validation.
- `POST /auth/ldap` - LDAP login with username and password.
- `POST /auth/saml` - SAML login with SAML response parsing.

## Secrets Management Endpoints

- `POST /secrets` - Create a new secret (user or project level).
- `GET /secrets/{secret_id}` - Retrieve secret metadata (value not included).
- `POST /secrets/{secret_id}/reveal` - Retrieve decrypted secret value (requires explicit permission).
- `PUT /secrets/{secret_id}` - Update secret (including rotation).
- `POST /secrets/{secret_id}/rotate` - Rotate secret value.
- `POST /secrets/{secret_id}/revoke` - Revoke secret.

## Secrets Security Practices

- Secrets are encrypted at rest using Fernet symmetric encryption.
- Encryption key is loaded from environment variable `SECRET_ENCRYPTION_KEY`.
- Access control enforced via RBAC and project membership.
- Audit logging for all secret operations.
- Secret values never returned unless explicitly requested and authorized.
- Support for expiration, rotation, revocation, and metadata.

## API Key Management Endpoints

- `POST /api_keys/user` - Create a new API key for the authenticated user. Returns the API key only once.
- `POST /api_keys/project` - Create a new API key scoped to a project (requires appropriate permissions).
- `DELETE /api_keys/{api_key_id}` - Deactivate (revoke) an API key.

## API Key Security Practices

- API keys are never stored in plaintext; only SHA-256 hashes are stored.
- API keys must be sent in the `X-API-Key` HTTP header.
- API keys can be revoked via the deactivate endpoint (soft delete).
- All API key usage updates the `last_used_at` timestamp.
- API key creation and revocation are logged for audit purposes.
- API keys are returned only once at creation time; clients must store them securely.

## Security Best Practices (OWASP REST Security Cheat Sheet)

- Enforce HTTPS for all API traffic.
- Require API keys in headers, never in URLs.
- Implement rate limiting (to be added).
- Use soft delete for API key revocation.
- Log all API key related activities.
- Set security headers in API responses:
  - `Cache-Control: no-store`
  - `Content-Security-Policy: frame-ancestors 'none'`
  - `Content-Type: application/json`
  - `Strict-Transport-Security`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
- Validate all inputs with Pydantic models.
- Return generic error messages with appropriate HTTP status codes.
- Restrict HTTP methods to those defined by FastAPI routes.
- Enable CORS only if necessary and restrict allowed origins.

## SQL Query Parameterization

- All SQL queries in this API use asyncpg's parameterized query style with placeholders (`$1`, `$2`, etc.).
- No user input is ever directly interpolated or concatenated into SQL strings.
- Dynamic SQL fragments are controlled internally and do not include user input directly.
- This approach fully complies with the OWASP Query Parameterization Cheat Sheet.
- Developers must continue to use parameterized queries for all future database interactions.
- Periodic code reviews and static analysis are recommended to ensure ongoing compliance.

## Configuration

Environment variables should be set to configure the IdP integrations, for example:

```yaml
environment:
  - OAUTH2_CLIENT_ID=
  - OAUTH2_CLIENT_SECRET=
  - OAUTH2_PROVIDER_URL=
  - LDAP_URL=
  - LDAP_BIND_DN=
  - LDAP_BIND_PASSWORD=
  - SAML_METADATA_URL=
  - SECRET_ENCRYPTION_KEY=  # Must be set to a base64-encoded Fernet key
```

## Next Steps

Implement the authentication logic in the placeholder endpoints in `security.py` to integrate with your chosen IdPs.

Implement secret management client logic to securely store and rotate secrets.

````
