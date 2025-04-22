# Identity Provider Integration Readiness

This API is designed to support pluggable external Identity Providers (IdPs) such as LDAP/Active Directory, OpenLDAP, OAuth2, SAML, and OpenID Connect.

## Database Support

- The `users` table includes `external_id` and `idp_provider` columns to store references to external identities.

## Authentication Endpoints

The following placeholder endpoints are available for future implementation of IdP authentication:

- `POST /auth/oauth2` - OAuth2 login with token validation.
- `POST /auth/ldap` - LDAP login with username and password.
- `POST /auth/saml` - SAML login with SAML response parsing.

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
