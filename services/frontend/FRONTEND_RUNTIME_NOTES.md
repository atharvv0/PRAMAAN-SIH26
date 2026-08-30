# PRAMAAN frontend

The frontend uses `VITE_API_BASE_URL` for the browser-facing API base.

For local Vite development, when `VITE_API_BASE_URL` is relative (the default `/api/v1`),
Vite proxies that API prefix to `VITE_DEV_API_TARGET` (default `http://127.0.0.1:8000`).
This keeps the browser same-origin while preserving the production `/api/v1` contract.

Production Docker deployment continues to use nginx to proxy `/api/` to the backend service.


## Local backend identity integration

When using the PRAMAAN local backend with server-side user scoping enabled, the frontend automatically sends the
authenticated local account email as the `X-User-Email` header through the central API client, including multipart
file uploads. The backend uses this identity for auto-provisioning and resource authorization; callers should not
manually add the header per endpoint.
