# PRAMAAN — API Contract

> Owner: Role 3 (Backend/Infrastructure) + Role 1 (Agent Architect, for run/event endpoints).
> The frontend (`services/frontend`) must only ever depend on what's written here —
> never on LangGraph node names or internal orchestrator state. See `docs/architecture.md`
> "Core Architectural Principle" for why.

Base path: `/api/v1`. All responses are JSON. Auth: `Authorization: Bearer <jwt>` (see
`.env.example` `JWT_SECRET`) once `services/governance/rbac` lands — not enforced yet in
the Phase 1–2 skeleton.

## MVP Endpoint Set (P0 — implemented in this scaffold or next)

| Method | Path | Purpose | Status |
|---|---|---|---|
| GET | `/api/v1/health` | Liveness check | **implemented** (`services/backend`) |
| POST | `/api/v1/tasks` | Create a task from a user instruction | **implemented** — in-memory store only, no persistence yet |
| GET | `/api/v1/tasks/{task_id}` | Get task status | **implemented** — in-memory store only |
| POST | `/api/v1/tasks/{task_id}/run` | Run the agent loop for a task | **implemented** — reuses stored AgentState across calls; no cross-restart persistence yet |
| POST | `/api/v1/tasks/{task_id}/approve` | Resume a task paused on `awaiting_approval` | **implemented** |
| GET | `/api/v1/tasks/{task_id}/events` | Full event-log list for a task | **implemented** — plain JSON list, not SSE streaming yet (TODO Phase 11) |
| GET | `/api/v1/runs/{run_id}` | Get run status by run_id | not implemented — `run_id` is currently just a label in each `/run` response, not independently queryable; task_id is the real lookup key |
| GET | `/api/v1/runs/{run_id}/events` | Stream execution trace (SSE) | superseded for now by `GET /tasks/{task_id}/events` above — real SSE is TODO Phase 11 |
| GET | `/api/v1/deliverables/{id}` | Fetch a generated deliverable | TODO Phase 14 |

Full endpoint groups planned (do not implement ahead of the roadmap phase — see
`docs/roadmap.md`): `/tasks`, `/runs`, `/agents`, `/models`, `/tools`, `/workspaces`,
`/documents`, `/knowledge`, `/evidence`, `/approvals`, `/deliverables`, `/health`.

## Example: `GET /api/v1/health`

Response `200`:
```json
{
  "status": "ok",
  "service": "pramaan-backend",
  "version": "0.1.0"
}
```

## Example: `POST /api/v1/tasks` (target shape — not yet implemented)

Request:
```json
{
  "intent": "Review this inspection package and prepare an approval note.",
  "file_ids": ["file_abc123"],
  "sensitivity": "confidential"
}
```

Response `201`:
```json
{
  "task_id": "task_9f2a...",
  "status": "created",
  "created_at": "2026-08-25T10:00:00Z"
}
```

## Example: `POST /api/v1/tasks/{task_id}/approve` (implemented)

Only valid when the task's stored state has `approval_status: "pending"` (set by a
previous `/run` call on a plan step with `requires_approval: true` — the demo
planner branch triggers this for any intent containing "approval"/"approve").
Response `200` shape is identical to `/run`'s `RunResult`, with `status` now
`"completed"` (or `"failed"`) instead of `"awaiting_approval"`. Calling this when
nothing is pending returns `409`.

## Example: `GET /api/v1/tasks/{task_id}/events` (implemented)

Response `200`:
```json
[
  { "type": "TASK_CREATED", "timestamp": "...", "task_id": "..." },
  { "type": "PLAN_CREATED", "timestamp": "...", "step_count": 1 },
  { "type": "STEP_STARTED", "timestamp": "...", "step_id": "...", "capability": "..." },
  { "type": "TASK_FAILED", "timestamp": "...", "step_id": "...", "reason": "PERMISSION_DENIED" }
]
```
Event types match `docs/agent-contract.md` "Task Run Events". The sequence above is
a real captured trace from the sovereignty-proof demo: intent `"test network
access"` routes to a tool that declares network access, gets denied by the Policy
Engine before it ever runs, and the denial + reason are both in this log and in
the `AuditLog` (`services/governance/audit`).

## Example: `POST /api/v1/tasks/{task_id}/run` with a knowledge-search intent (implemented — real RAG, not a demo tool)

Intent containing "sop"/"search the knowledge"/"look up" routes to the real
`knowledge.search` tool (`services/knowledge/rag/`) — genuine offline similarity
search, not a placeholder. Real captured response:
```json
{
  "status": "completed",
  "evidence": [
    {
      "claim": "The inspection was completed on schedule. ... follow-up inspection is recommended within 90 days.",
      "source": "data/samples/demo/sample_note.txt",
      "page_or_region": "chunk_0",
      "tool": "knowledge.search",
      "confidence": 0.4415578896653721,
      "validation_state": "unverified"
    }
  ]
}
```
`confidence` here is a real cosine similarity score, not a fixed placeholder
number. Ingest more documents via `Retriever.ingest_file()` — currently only one
demo sample is pre-seeded (`services/orchestrator/tools/registry_instance.py`).

## Example: `POST /api/v1/tasks/{task_id}/run` (implemented — demo tools only)

Response `200` — this is a real captured response, not a mock:
```json
{
  "run_id": "run_09e2649cbfa1",
  "task_id": "task_6dc71fcda78d",
  "status": "completed",
  "completed_steps": ["step_43b03994", "step_c4314967"],
  "errors": [],
  "evidence": [
    {
      "claim": "Text extracted from source document (placeholder OCR — not real vision/OCR)",
      "source": "/app/data/samples/demo/sample_note.txt",
      "page_or_region": "page_1",
      "model": null,
      "tool": "ocr.process_naive",
      "confidence": 0.5,
      "validation_state": "unverified"
    }
  ],
  "final_output": {
    "task_id": "task_6dc71fcda78d",
    "completed_steps": ["step_43b03994", "step_c4314967"],
    "tool_outputs": [
      { "content": "...", "path": "...", "evidence": [ /* same shape as above */ ] },
      { "summary": "...", "sentence_count": 5 }
    ]
  }
}
```
`status` is one of `"completed" | "failed" | "awaiting_approval"`. `evidence` is
populated automatically by the Executor whenever a tool returns an `evidence[]` key
(see `docs/agent-contract.md` "EvidenceRecord") — the intent-recognition branch for
this example (`"scanned ... p&id ..."` + a file) routes through the demo OCR tool.
The tools behind this response (`file.read`, `text.summarize_naive`,
`ocr.process_naive`) are demo-only placeholders — see
`services/orchestrator/tools/examples.py`. Real tools replace them without changing
this response shape.

## Frontend integration endpoints (MVP)

The current React workbench uses these JSON endpoints in addition to the core task/run lifecycle:
`GET /api/v1/overview`, `GET /api/v1/workspaces`, `GET /api/v1/workspaces/{workspace_id}`, `GET /api/v1/evidence`, `GET /api/v1/evidence/{evidence_id}`, `GET /api/v1/models`, `GET /api/v1/audit`, `GET /api/v1/sovereignty`, `GET /api/v1/network-events`, `GET /api/v1/deliverables`, `GET /api/v1/approvals`, and `POST /api/v1/approvals/decide`. These endpoints are in-process MVP adapters over the same task/run state and are intentionally replaceable by repository-backed services.

## Error Shape (all non-2xx responses)

```json
{
  "error": {
    "code": "TOOL_EXECUTION_ERROR",
    "message": "The document parser could not read this file.",
    "retryable": true
  }
}
```

Never expose stack traces or internal detail in the response body — log those
server-side only (see `services/governance/audit`).

## Status: DRAFT — MVP slice only

This is intentionally thin. Extend it endpoint-by-endpoint as each roadmap phase is
actually implemented, and update the table above so the frontend team always has an
accurate map of what's real vs. planned.
