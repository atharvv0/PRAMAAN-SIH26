# services/backend — Core API

**Owner:** Role 3 — Backend/Infrastructure (per `docs/team-structure.md`)

## What belongs here

- FastAPI app (`app/main.py`) and routers (`app/api/`)
- Request/response schemas for the HTTP layer (`app/models/`) — these mirror, but are
  not the same object as, the internal contracts in `docs/agent-contract.md`
- Config (`app/core/config.py`) — all env-driven, never hard-coded
- Persistence repositories (not yet added — Phase 3, coordinate with the data owner
  before adding raw SQL anywhere in this service)

## What does NOT belong here

- Planning/agent logic → `services/orchestrator`
- Model selection logic → `services/model_control`
- Policy/permission decisions → `services/governance`
- Business logic embedded directly in route handlers — keep handlers thin, push logic
  into services/orchestrator via a clean call, not inline

## Status of this scaffold

`GET /api/v1/health`, `POST/GET /api/v1/tasks`, `POST /api/v1/tasks/{task_id}/run`,
`POST /api/v1/tasks/{task_id}/approve`, and `GET /api/v1/tasks/{task_id}/events` are
implemented and tested — the run/approve endpoints wire the real
`services/orchestrator` Planner + Executor + ToolRegistry (now policy-gated and
audit-logged, see `services/governance`) into the API and return genuine execution
results, including populated `evidence[]` for multimodal-shaped intents and full
lifecycle event traces (verified live end-to-end, not just unit-tested — see
`docs/api-contract.md` for real captured responses). `AgentState` is kept alive in
backend's process memory between calls (so approval-resume actually works), but
task/state storage is still not persisted to Postgres — a restart loses everything.

## Run it

This service imports `services/orchestrator` directly, so it needs the **repo
root** on `PYTHONPATH`, not just its own directory:

```bash
# from repo root
python -m venv .venv && source .venv/bin/activate
pip install -r services/backend/requirements.txt -r services/orchestrator/requirements.txt
PYTHONPATH=. uvicorn app.main:app --app-dir services/backend --reload --port 8000
# or: docker compose up backend   (Dockerfile already builds with repo root as context)
```

## Test it

```bash
# from repo root
pytest services/backend/tests
# or the whole repo's suite: pytest
```

## Definition of Done (this phase — Phase 2/3, see docs/roadmap.md)

- [x] Service boots and responds on `/api/v1/health`
- [x] `docker compose up --build` succeeds for this service
- [x] `/tasks/{task_id}/run` executes a real plan through the orchestrator's Executor
- [x] `/tasks/{task_id}/approve` genuinely resumes a paused run
- [x] `/tasks/{task_id}/events` exposes the full lifecycle event log
- [ ] `/tasks` backed by a real repository instead of the in-memory dict
- [ ] `/runs/{run_id}` as its own lookup, not just the terminal `/run` response
- [ ] Every endpoint in `docs/api-contract.md` marked "implemented" has a passing test
