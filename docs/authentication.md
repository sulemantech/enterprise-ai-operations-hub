# Hellō sign-in and organisation membership

For local development, the browser offers **Enter local demo**. It creates a fixed synthetic manager session for `ORG-DEMO` and does not contact Hellō or require a membership row. This endpoint and identity are accepted only when `APP_ENV=development`; they are not a production authentication option. Set `APP_ENV=production` for a deployed environment and use the OIDC setup below.

The app uses Hellō as its OpenID Connect provider. The browser starts authorization-code login with PKCE at FastAPI (`/auth/login`); FastAPI handles the callback, validates the OIDC response, and stores only the verified issuer and subject in a signed, HTTP-only session cookie. React calls the API through Vite's same-origin `/api` proxy in development. Provider tokens are not stored in the browser session.

Authentication identifies a person; it does not grant access to an organisation. FastAPI resolves an active `(issuer, subject)` row in `user_organisation_memberships` on each protected request. A user with multiple memberships selects one using `X-Organisation-ID`. `viewer` is read-only; `manager` may create, edit, and approve follow-up drafts.

## Local Hellō setup

In the Hellō Developer Console, configure a **Web** application and add this development redirect URI (the existing `http://localhost:*` wildcard also covers it):

```text
http://localhost:8000/auth/callback
```

Copy the application's **Client ID** to the root `.env` file. It is a public identifier, not a secret. Do not create or expose a client secret for this PKCE public-client flow. Set a random local `SESSION_SECRET` too; PowerShell can generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set these values in `.env` (see `.env.example`):

```text
HELLO_CLIENT_ID=your-Hello-application-client-id
HELLO_REDIRECT_URI=http://localhost:8000/auth/callback
HELLO_FRONTEND_URL=http://localhost:5173/
SESSION_SECRET=your-random-local-session-secret
APP_ENV=development
```

Restart FastAPI and Vite, then open `http://localhost:5173` and choose **Sign in with Hellō**. The provider returns to FastAPI, not directly to the frontend. `http://localhost` and `http://127.0.0.1` are different cookie hosts; use `localhost` consistently for both browser and frontend URL.

## Provision a local membership

After signing in, an unprovisioned user sees their verified issuer and subject. Apply migrations, then an administrator can add the account to the synthetic local tenant. Verify the identity before running this SQL; use the exact issuer and subject shown by the app:

```sql
INSERT INTO user_organisation_memberships
    (issuer, subject, organisation_id, role, active)
VALUES
    ('https://issuer.hello.coop', 'verified-subject', 'ORG-DEMO', 'manager', TRUE);
```

The subject is an identifier, not a credential. Do not provision users from self-asserted request headers or email alone. Production provisioning needs an audited administrator workflow.

## Deployment requirements and limits

For deployment, set `APP_ENV=production`, a strong unique `SESSION_SECRET`, and HTTPS redirect/frontend URLs. Register the exact production callback URL in the Hellō Console. Keep the client ID in server configuration. Cookie `Secure` is enabled outside development. Logout clears the local session; provider-wide logout and token refresh are not implemented.

This establishes login and role checks; it does not make the app production-ready. Add CSRF protection for cookie-authenticated state-changing routes, rate limits, secure secret management, audited membership administration, operational monitoring, and a security review. Review/enforce tenant ownership across all records and retrieval before real multi-tenant use. The tests mock the provider and do not constitute an end-to-end Hellō integration test.
