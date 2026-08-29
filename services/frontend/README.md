# services/frontend — PRAMAAN Workbench UI

The production frontend is the React + TypeScript + Vite application in this directory.
It is intentionally separated from the backend and other Python services.

## Structure

- `src/` — application routes, pages, components, API client, types and state
- `public/` — static assets
- `nginx.conf` — production reverse proxy; `/api/` is forwarded to the backend container
- `Dockerfile` — two-stage Vite build + nginx runtime

## API mode

The final integration uses `VITE_API_MODE=http`. The browser talks to `/api/v1`, and nginx proxies those requests to the backend. The deterministic mock adapter remains in `src/mocks/` for local UI development/tests, but the production/demo path must use the live backend.

## Run locally

```bash
npm ci
npm run dev
```

## Production container

From the repository root:

```bash
docker compose up --build frontend backend
```

The workbench should be reachable at the frontend port configured in the root `.env`.

## Final integration checklist

- [ ] Task creation uses `POST /api/v1/tasks`
- [ ] Run view uses the live run/task event endpoints
- [ ] Evidence page uses live evidence responses
- [ ] Approval UI uses live approval endpoints
- [ ] Deliverables page uses live deliverable responses
- [ ] Models page shows actual Model Control registry data
- [ ] Sovereignty page shows actual policy/network data
- [ ] `VITE_API_MODE=http` in the production/demo build
