# services/frontend — Workbench UI

**Owner:** Role 6 — Frontend/UX + Product (per `docs/team-structure.md`)

## What belongs here

- `src/pages/` — Task creation, Run view, Evidence panel, Approval queue, Deliverables
- `src/components/` — shared UI pieces
- `src/evidence_panel/` — click-to-source multimodal evidence view (a signature
  differentiator per `docs/architecture.md`)
- `public/` — static assets

## What does NOT belong here

- Any assumption about internal agent/LangGraph state. This app talks **only** to
  `docs/api-contract.md` — Task, TaskStep, AgentRun, ToolCall, Evidence, Approval,
  Deliverable. If an endpoint you need isn't in that doc, that's a signal to raise it
  with Role 1/3, not to reach around the API.

## Status of this scaffold

`public/index.html` + `Dockerfile` are a **placeholder only** — a static "coming soon"
page so `docker compose up --build` boots this service end-to-end today. No real UI has
been built. Stack choice (plain HTML/CSS/JS/Bootstrap/PWA per the dossier, or a
framework) is yours to decide.

## Run it

```bash
docker compose up frontend
# -> http://localhost:3000 (placeholder page)
```

## Definition of Done (Phase 9, see docs/roadmap.md)

- [ ] Task creation form wired to `POST /api/v1/tasks`
- [ ] Live run/event view wired to `GET /api/v1/runs/{run_id}/events`
- [ ] Evidence panel: click a claim -> see exact source region
- [ ] Approval queue UI wired to `POST /api/v1/runs/{run_id}/approve`
