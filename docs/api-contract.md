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
| POST | `/api/v1/tasks/{task_id}/run` | Run the agent loop for a task, synchronously | **implemented** — see below; no persistence, no async/event streaming yet |
| GET | `/api/v1/runs/{run_id}` | Get run status by run_id | TODO — current `/run` response is the terminal result; no separate lookup-by-run_id yet |
| GET | `/api/v1/runs/{run_id}/events` | Stream execution trace (SSE) | TODO Phase 11 |
| POST | `/api/v1/runs/{run_id}/approve` | Approve/reject a pending step | TODO Phase 13 — executor already pauses and sets `approval_status: pending`, but there's no endpoint yet to resume it |
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
