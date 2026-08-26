# PRAMAAN — Architecture

> Referenced from `README.md`. This is the canonical logical architecture. Individual
> service READMEs describe implementation detail; this document describes the contracts
> between layers and must not drift without a team-wide decision (see `docs/agent-contract.md`
> and `docs/api-contract.md` for the frozen interfaces).

## Logical Flow

```text
USER
  |
  v
FRONTEND / WORKBENCH            (services/frontend)
  |
  v
CORE API — FastAPI              (services/backend)
  |
  v
TASK ENGINE                     (services/backend)
  |
  v
AGENT ORCHESTRATOR              (services/orchestrator)
  |
  +---------------+
  v               v
PLANNER       AGENT STATE       (services/orchestrator)
  |
  v
MODEL / TOOL SELECTION
  |
  +---------------+----------------+
  v               v                v
MODEL ROUTER   TOOL REGISTRY   KNOWLEDGE/RAG
(model_control) (orchestrator/  (knowledge)
                 tools)
  |               |                |
  v               v                v
MODEL RUNTIME   POLICY CHECK      QDRANT
(model_control) (governance)
  |
  v
EXECUTION
  |
  v
VALIDATION
  |
  v
HUMAN APPROVAL (when required)
  |
  v
DELIVERABLE
  |
  v
AUDIT / EVIDENCE / TASK TRACE   (services/governance)
```

## Core Principle: Separation of Concerns

The Agent Layer does **not** contain implementation logic for every subsystem.

| Layer | Decides |
|---|---|
| Agent (`orchestrator`) | *What* needs to happen |
| Tool (`orchestrator/tools` + tool implementations in owning services) | *How* an action is executed |
| Model Router (`model_control`) | *Which* model handles a capability |
| Policy Engine (`governance`) | *Whether* an action is allowed |
| Database layer (`backend` repositories) | *Where* state/data is persisted |
| Agent Orchestrator (`orchestrator`) | *What happens next* |

**Hard rule:** `Agent -> Tool` directly is forbidden. The real path is always
`Agent -> Tool Request -> Policy Engine -> ALLOW/DENY -> Tool`.

## Repository -> Architecture Layer Mapping

| Architecture layer | Repo path | Owning role (see `docs/team-structure.md`) |
|---|---|---|
| Experience | `services/frontend/` | Role 6 — Frontend/UX + Product |
| Orchestration | `services/orchestrator/` | Role 1 — AI/Agent Architect |
| Core API | `services/backend/` | Role 3 — Backend/Infrastructure |
| Model control | `services/model_control/` | Role 2 — ML Systems/Runtime |
| Knowledge | `services/knowledge/` | Role 5 — Multimodal/ML |
| Tools + Sandbox | `services/orchestrator/tools/`, `services/sandbox/` | Role 1 (registry) + Role 4 (isolation) |
| Governance | `services/governance/` | Role 4 — Security/Governance |

## Deployment Topology (SIH MVP — Level 1)

Only `backend` and `frontend` are containerized services in `docker-compose.yml` for the MVP.
`orchestrator`, `model_control`, `knowledge`, `governance`, and `sandbox` are Python packages
imported by `backend` in-process — this avoids premature microservice overhead while keeping
the module boundaries (and their contracts) intact so they can be split into separate
containers post-SIH without rewriting logic. `postgres` and `qdrant` run as their own
containers from Day 1.

See `docs/agent-contract.md` for the internal object contracts and `docs/api-contract.md`
for the external HTTP contract the frontend integrates against.
