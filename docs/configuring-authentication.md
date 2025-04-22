# Configuring Authentication

magllama supports pluggable authentication with external Identity Providers (IdPs) such as:

- LDAP/Active Directory
- OpenLDAP
- OAuth2
- SAML
- OpenID Connect

## Environment Variables

Set the following environment variables as needed in your `.env` file:

```env
OAUTH2_CLIENT_ID=
OAUTH2_CLIENT_SECRET=
OAUTH2_PROVIDER_URL=
LDAP_URL=
LDAP_BIND_DN=
LDAP_BIND_PASSWORD=
SAML_METADATA_URL=
SECRET_ENCRYPTION_KEY=  # Must be set to a base64-encoded Fernet key
```

## API Endpoints

- `POST /auth/oauth2` - OAuth2 login with token validation.
- `POST /auth/ldap` - LDAP login with username and password.
- `POST /auth/saml` - SAML login with SAML response parsing.

## Notes

- The API is ready for integration with your chosen IdP.
- Implement the authentication logic in `api/security.py` as needed.
- All authentication and authorization is enforced via RBAC and project membership.
