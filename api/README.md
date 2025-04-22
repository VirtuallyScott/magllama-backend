# Identity Provider Integration Readiness

This API is designed to support pluggable external Identity Providers (IdPs) such as LDAP/Active Directory, OpenLDAP, OAuth2, SAML, and OpenID Connect.

## Database Support

- The `users` table includes `external_id` and `idp_provider` columns to store references to external identities.
- Added `api_keys` table for secure API key management with user-level and project-level keys.

## Authentication Endpoints

The following placeholder endpoints are available for future implementation of IdP authentication:

- `POST /auth/oauth2` - OAuth2 login with token validation.
- `POST /auth/ldap` - LDAP login with username and password.
- `POST /auth/saml` - SAML login with SAML response parsing.

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
```

## Next Steps

Implement the authentication logic in the placeholder endpoints in `security.py` to integrate with your chosen IdPs.

````
