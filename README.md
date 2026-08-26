# PRAMAAN

**Sovereign On-Premise Agentic AI Workbench**
SIH 2026 | Problem Statement **SIH26117** | PS Given by **Mangalore Refinery and Petrochemicals Limited (MRPL)** | Category: Software / Smart Automation

> Confidential industrial work should be delegable to AI without surrendering control of the data — with every model, tool, source and network boundary observable and auditable.

## What is PRAMAAN?

PRAMAAN is a **self-hosted, air-gapped, multi-model agentic workbench** that lets confidential industrial organisations delegate multimodal, multi-step knowledge work to open-weight AI — with provable sovereignty and evidence-linked deliverables.

It is not a chatbot, not a basic RAG app, and not a cloud AI wrapper.

## Core Capabilities

| Pillar | What it does |
|---|---|
| Model Intelligence | Tasks auto-routed to different open-weight models by capability |
| Agentic Execution | One instruction → visible plan → tools → iteration → validation → result |
| Multimodal Intelligence | Scanned PDF / image / P&ID → structured, verifiable output |
| Coding + Verification | Generated code runs in a sandbox and is tested |
| Sovereignty Proof | Outbound network requests visibly blocked and logged |
| Real Deliverable | Actual `.docx` / `.pptx` / `.xlsx` / code artifact is produced |

## Architecture

```
User / UI → Orchestration (Planner/Executor) → Model Control (Registry/Router) → Sovereignty (Network policy/Audit)
                ↓                    ↓                    ↓                          ↓
           Multimodal           Knowledge              Tools                     Trust
        (OCR/VLM, P&ID)      (RAG over SOPs)     (Files, Sandbox)         (Evidence, Provenance)
                └────────────────────┴────────────────────┴──────────────────────────┘
                                              ↓
                                    Deliverables (Word/PPT/Excel/Code)
                         Everything stays inside the controlled deployment boundary
```

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown.

## Repository Structure

```
services/
├── backend/         # FastAPI core — auth, APIs, service contracts
├── orchestrator/     # Planner/Executor, agent state graph, tool calls
├── model_control/    # Model Registry, Router, runtime adapters
├── knowledge/         # OCR/VLM, RAG ingestion & retrieval, spreadsheet engine
├── governance/         # Policy Engine, RBAC, network monitor, audit, evidence layer
├── sandbox/             # Isolated code execution (no network access)
└── frontend/             # Workbench UI, Evidence Panel, approval flow

infra/     # Docker, network policy, deployment scripts
data/      # Sample/synthetic docs for demo (scanned reports, P&ID, SOPs, spreadsheets)
tests/     # Unit, integration, and evaluation suites
docs/      # Architecture, requirements mapping, demo script, roadmap
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5/CSS3/JS, Bootstrap, PWA |
| Backend | FastAPI (Python) |
| Orchestration | LangGraph-style explicit state graph |
| Database | PostgreSQL |
| Vector Store | Qdrant |
| OCR + Vision | PaddleOCR-VL + Qwen-VL-class model |
| Inference | vLLM (serving) / Ollama (dev) |
| Sandbox | Firecracker/Kata (or lighter fallback) |
| Containerisation | Docker Compose |

## Team

| Role | Owns |
|---|---|
| AI / Agent Architect | Planner, Agent Orchestrator, Model Router |
| ML Systems / Runtime | Model Registry, vLLM/Ollama integration, benchmarking |
| Backend / Infrastructure | FastAPI, Postgres, Qdrant, Docker Compose |
| Security / Governance | Sovereignty Control Plane, Policy Engine, sandbox isolation |
| Multimodal / ML | OCR/VLM, RAG, spreadsheet deterministic engine |
| Frontend / UX + Product | Workbench UI, Evidence Panel, deliverables, demo integration |

## Getting Started

```bash
cp .env.example .env
docker compose up --build
curl http://localhost:8000/api/v1/health
```

This boots `backend` (FastAPI), `frontend` (placeholder page), `postgres`, and
`qdrant`. The first genuine agentic loop is already working — Planner → Executor →
ToolRegistry, over demo-only tools — try it:

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"intent": "summarize this file", "demo_file_path": "/app/data/samples/demo/sample_note.txt"}'
# -> {"task_id": "task_..."}

curl -X POST http://localhost:8000/api/v1/tasks/<task_id>/run
# -> {"status": "completed", "final_output": {...}}
```

Full setup, per-module dev loops, and conventions: see
[`docs/developer-setup.md`](docs/developer-setup.md). Each `services/<name>/README.md`
has that module's own scope, contract, and Definition of Done — start there.

## License

See [`LICENSE`](LICENSE).
