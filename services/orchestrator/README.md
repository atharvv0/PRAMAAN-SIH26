# services/orchestrator — Agentic Intelligence Layer

**Owner:** Role 1 — AI/Agent Architect (per `docs/team-structure.md`)

## What belongs here

- `planner/` — turns a `TaskDefinition.intent` into a `Plan` (`docs/agent-contract.md`)
- `state_graph/` — `AgentState` and the LangGraph execution graph (checkpointing,
  step transitions, human-in-the-loop pause points)
- `tools/` — the `ToolAdapter` interface and `ToolRegistry`. Concrete tool
  *implementations* (document reader, spreadsheet engine, OCR, sandboxed code exec)
  belong to their owning service and register themselves here — this package only
  owns the interface + registry, not every tool's business logic.
- `agents/` — sub-agent role stubs (Document/Vision, Knowledge/RAG, Coding/Data,
  Validation, Deliverable) as thin coordination wrappers. The actual document parsing,
  RAG retrieval, etc. lives in `services/knowledge`, `services/sandbox`, etc. — this
  package just orchestrates calling them in the right order per the plan.

## What does NOT belong here

- HTTP routing → `services/backend`
- Model invocation/selection logic → `services/model_control`
- Policy/permission decisions → `services/governance` (this package must call the
  Policy Engine before every tool execution, never bypass it — see
  `docs/architecture.md` "Core Principle")

## Import path note

This package is imported as `services.orchestrator.*` (there's a `services/__init__.py`
at repo root for this reason) — run its tests from the **repo root**, not from inside
`services/orchestrator/`:

```bash
# from repo root
pip install -r services/orchestrator/requirements.txt
pytest services/orchestrator/tests
```

## Status of this scaffold

`Plan`/`PlanStep`, `AgentState`, `ToolAdapter`/`ToolRegistry`, the error classes
(`errors.py`), and a working **Executor** (`state_graph/executor.py`) are implemented
and tested against `docs/agent-contract.md`. The executor walks a plan in dependency
order, respects the human-approval pause point, enforces a hard `max_steps` ceiling
(never `while True: agent.run()`), retries a failed step once before giving up, and
passes each step's output to whatever step depends on it.

`planner.create_plan()` does real (if simple) branching — it produces a genuine
2-step read-then-summarize plan when given a file + a "summarize" intent, a
2-step OCR-then-summarize plan for a multimodal-shaped intent (e.g. "review this
scanned p&id drawing"), and falls back to a placeholder plan otherwise. It is
**not yet model-backed** — that's Phase 3/5, once `services/model_control` exists.
Three demo-only tools (`tools/examples.py`: `file.read`, `text.summarize_naive`,
`ocr.process_naive`) exist solely to prove the loop end-to-end; they are not
production tools — `ocr.process_naive` in particular is a stand-in for the real
OCR/VLM pipeline (see `services/knowledge/README.md` — that module is now also
this project's owner's to implement, not just a workspace for a teammate).

The Executor also populates `AgentState.evidence` automatically whenever a tool
returns an `evidence[]` key shaped per `docs/agent-contract.md` "EvidenceRecord" —
this is what backs the "click a claim -> exact source region" differentiator in
`docs/architecture.md`, and it's surfaced all the way through the API response
(`docs/api-contract.md`).

**Verified live, not just unit-tested:** creating a task via the backend API with
either a summarize intent or a "scanned ... drawing" intent, then calling `/run`,
produces a real multi-step result — including populated evidence for the
multimodal path — through the full API → Executor → ToolRegistry → demo tools path.

## Definition of Done (this phase — Phase 3, see docs/roadmap.md)

- [x] `Plan`/`PlanStep`/`AgentState` match `docs/agent-contract.md`
- [x] `ToolRegistry` register/get round-trip tested
- [x] Executor: plan -> execute step -> next step, with dependency ordering
- [x] Human-approval pause point implemented (executor stops, sets `approval_status`)
- [x] Hard step-count ceiling (`AgentLoopLimitError`) implemented and tested
- [x] One instruction -> multi-step plan -> tool use -> completed result, proven live
      via the backend API (master prompt section 29's "first genuine agentic loop")
- [x] Multimodal-shaped plan branch (OCR-then-summarize) + evidence population,
      proven live end-to-end with a demo OCR placeholder tool
- [ ] `create_plan()` backed by a real model call via `services/model_control`
- [ ] Real OCR/VLM/RAG pipeline replacing `ocr.process_naive` (services/knowledge —
      now also this project owner's responsibility)
- [ ] Executor calls tools only through Policy Engine (`services/governance`) —
      not wired yet, that module doesn't exist
- [ ] LangGraph itself (currently a hand-rolled loop, not yet using the LangGraph
      library — swap in once checkpointing/HITL primitives are actually needed)
