# PRAMAAN frontend

The frontend uses `VITE_API_BASE_URL` for the browser-facing API base.

For local Vite development, when `VITE_API_BASE_URL` is relative (the default `/api/v1`),
Vite proxies that API prefix to `VITE_DEV_API_TARGET` (default `http://127.0.0.1:8000`).
This keeps the browser same-origin while preserving the production `/api/v1` contract.

Production Docker deployment continues to use nginx to proxy `/api/` to the backend service.
