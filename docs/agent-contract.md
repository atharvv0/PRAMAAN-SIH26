# PRAMAAN — Agent Contract

> The most important interface document for the team. These object contracts are how
> `services/orchestrator`, `services/backend`, `services/model_control`, `services/knowledge`,
> `services/governance`, and `services/sandbox` talk to each other without depending on each
> other's internals. **Change these only with a team-wide decision** — everyone codes against
> this document, not against someone else's source file.
>
> Owner: Role 1 (AI/Agent Architect) + Role 3 (Backend), per `services/orchestrator/README.md`
> and `services/backend/README.md`. Reference implementations of the schemas below live in
> `services/orchestrator/planner/schemas.py` and `services/orchestrator/state_graph/agent_state.py`.

## TaskDefinition

```text
task_id: str (UUID)
user_id: str
intent: str                 # raw user instruction
files: list[FileRef]
sensitivity: str            # e.g. "public" | "confidential" | "restricted"
created_at: datetime
```

## Plan / PlanStep

```text
Plan:
  task_id: str
  goal: str
  steps: list[PlanStep]

PlanStep:
  id: str
  capability: str            # e.g. "document_analysis", "spreadsheet_compute"
  tool: str | None           # tool id from the Tool Registry, if known at plan time
  inputs: dict
  depends_on: list[str]      # ids of steps that must complete first
  requires_approval: bool
  status: str                # "pending" | "running" | "done" | "failed" | "skipped"
```

## AgentState

```text
task_id: str
user_id: str
intent: str
plan: Plan | None
current_step: str | None
completed_steps: list[str]
files: list[FileRef]
evidence: list[EvidenceRecord]
tool_calls: list[ToolCall]
model_calls: list[ModelCall]
validation_results: list[ValidationResult]
errors: list[AgentError]
approval_status: str        # "not_required" | "pending" | "approved" | "rejected"
final_output: dict | None
```

## ModelAdapter (implemented by `services/model_control`)

```text
id: str
capabilities: list[str]     # e.g. ["reasoning", "coding", "ocr", "vision"]
invoke(prompt, **kwargs) -> ModelResponse
health_check() -> bool
metadata() -> dict
```

## ToolAdapter (implemented by tool owners; registered via `services/orchestrator/tools`)

```text
id: str
required_permissions: list[str]
declares_network_access: bool
invoke(inputs: dict) -> ToolResult
```

## EvidenceRecord

```text
claim: str
source: str
page_or_region: str | None
retrieval_event: str
model: str
tool: str
confidence: float
validation_state: str       # "unverified" | "verified" | "flagged"
```

## AuditEvent (implemented by `services/governance/audit`)

```text
actor: str
action: str
target: str
decision: str                # "allow" | "deny"
policy_reason: str | None
timestamp: datetime
```

## Task Run Events (streamed to frontend — see `docs/api-contract.md`)

```text
TASK_CREATED, PLAN_CREATED, STEP_STARTED, MODEL_SELECTED, TOOL_STARTED,
TOOL_COMPLETED, EVIDENCE_ADDED, VALIDATION_STARTED, VALIDATION_COMPLETED,
APPROVAL_REQUIRED, APPROVED, DELIVERABLE_CREATED, TASK_COMPLETED, TASK_FAILED
```

## Error Classes

```text
PlannerError, ModelUnavailableError, ToolExecutionError, PermissionDeniedError,
ValidationError, HumanApprovalRequired, TaskTimeoutError, AgentLoopLimitError,
DeliverableGenerationError
```

Every error carries: `code` (machine-readable), `message` (user-readable),
`detail` (internal, never sent to frontend as a raw stack trace), `retryable: bool`,
`next_action: str | None`.

## Status: DRAFT

These schemas are frozen enough to build against for Phase 2–4, but are **not final** —
expect additions as Phase 5 (multimodal) and Phase 7 (security) come online. Propose
changes via PR against this file, not silently in code.
