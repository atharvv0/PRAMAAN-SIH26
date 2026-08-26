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

## Current status (Phase 2)

- `adapters/base.py` — `ModelAdapter` interface + `ModelResponse`, per
  `docs/agent-contract.md` "ModelAdapter"
- `adapters/ollama_adapter.py` — real HTTP adapter against a live Ollama server
  (`/api/generate`, `/api/tags`); returns real completions when a model is pulled
  and reachable, `health_check()` returns `False` otherwise
- `adapters/demo_adapter.py` — deterministic offline fallback (no network), always
  healthy, so the router never dead-ends with zero candidates
- `registry/registry.py` + `registry/registry_instance.py` — `ModelRegistry`,
  wired from `.env.example`'s `MODEL_RUNTIME_HOST`/`PORT` and
  `REASONING_MODEL_NAME`/`CODING_MODEL_NAME`/`OCR_MODEL_NAME`/`VISION_MODEL_NAME`
  (blank var = no live adapter registered for that capability; the offline
  fallback still is)
- `router/router.py` — `select_model(registry, capability, modality,
  security_classification, latency_budget_ms)`, capability-driven, health-checked
  with automatic fallback
- Consumed by `services/orchestrator/tools/model_backed.py`
  (`SummarizeTextModelTool`, id `text.summarize_model`)
- `latency_budget_ms`-aware ranking is not implemented yet — see `router.py`'s
  NOTE — needs real numbers from `benchmarks/` first
- vLLM production adapter not built yet — no hardware benchmark has picked a
  runtime target; see `adapters/ollama_adapter.py` docstring

## Contract to implement

See `docs/agent-contract.md` → "ModelAdapter". Router must never hard-code
`if task == "coding": return qwen` — capability-driven selection only.

## Run its tests (once you've written some)

```bash
pip install -r requirements.txt
pytest services/model_control/tests
```

## Definition of Done (Phase 2, see docs/roadmap.md)

- [x] At least two models available through one `ModelAdapter` interface (real
      Ollama adapter + offline demo fallback; a second *real* model needs a
      `*_MODEL_NAME` env var set once Ollama + a pulled model are available)
- [x] `select_model()` implemented and capability-driven, not hard-coded
- [x] Health-check + fallback model behavior implemented
