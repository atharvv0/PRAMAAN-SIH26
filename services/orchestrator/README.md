# PRAMAAN Orchestrator

The orchestrator is responsible for planning and controlled execution. The current final path is:

`Task → Model-backed Planner (Ollama via Model Control) → validated Plan → Policy-gated Executor → Tools → Evidence → Deliverable`

The deterministic planner remains available for unit tests only. Production/demo planning uses the configured local reasoning model.

## Tool routes

- `ocr.process` — local Ollama vision/document processing
- `knowledge.search` — local Qdrant retrieval with local Ollama embeddings
- `text.summarize_model` / `model.reason` — local reasoning model
- `code.generate_model` — local coding-capable model route
- `code.execute` — local restricted Python sandbox subprocess
- `network.fetch_demo` — intentionally blocked sovereignty test tool

## Safety

Every tool invocation goes through the Policy Engine. Network-capable tools are denied in sovereign mode and the decision is recorded. Model output is validated before it can become an execution plan.
