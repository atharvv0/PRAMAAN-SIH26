# services/model_control — Model Registry + Router

**Owner:** Role 2 — ML Systems/Runtime (per `docs/team-structure.md`)

## What belongs here

- `registry/` — registered models + their capabilities/metadata (no redesign needed
  to add a new model, per the official PS requirement)
- `router/` — `select_model(task_type, modality, complexity, security_classification,
  latency_budget, available_resources) -> selected_model` (see `docs/agent-contract.md`
  "ModelAdapter" for the interface every model must implement)
- `adapters/` — one `ModelAdapter` implementation per runtime (vLLM, Ollama, ...)
- `benchmarks/` — scripts/results for choosing real model candidates on actual hardware

## What does NOT belong here

- Agent/planning logic → `services/orchestrator`
- This package is a workspace only — **no implementation has been added on your
  behalf**. Implement `ModelAdapter` per `docs/agent-contract.md` and register your
  models here.

## Contract to implement

See `docs/agent-contract.md` → "ModelAdapter". Router must never hard-code
`if task == "coding": return qwen` — capability-driven selection only.

## Run its tests (once you've written some)

```bash
pip install -r requirements.txt
pytest services/model_control/tests
```

## Definition of Done (Phase 2, see docs/roadmap.md)

- [ ] At least two models available through one `ModelAdapter` interface
- [ ] `select_model()` implemented and capability-driven, not hard-coded
- [ ] Health-check + fallback model behavior implemented
