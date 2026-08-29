# PRAMAAN — Sovereign AI Workbench

Production React + TypeScript + Vite frontend for the PRAMAAN local backend. The browser talks only to the configured API base URL; no cloud AI provider, analytics, or telemetry service is required by the UI.

## Local development

```bash
npm ci
npm run dev
```

Set `VITE_API_BASE_URL` when the backend is not served through the same origin. The default is `/api/v1`.

## Production build

```bash
npm run build
npm run preview
```

The frontend uses live backend state in production. It does not silently substitute mock/demo data when the API is unavailable.

## Frontend access layer

When the supplied backend has no server-side identity endpoint, the UI uses a browser-local account layer for controlled product testing. User IDs, emails, profile data, and salted PBKDF2 password hashes remain in the current browser; this is not a replacement for enterprise SSO/OIDC or server-side authorization.

The workbench supports light, dark, and system appearance modes. Light is the default for new browser profiles.
