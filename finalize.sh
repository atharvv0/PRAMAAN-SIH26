#!/usr/bin/env bash
# =====================================================================
# PRAMAAN — ONE-SHOT repo finalizer
# Run this from the ROOT of your PRAMAAN-SIH26 repo (where .git lives).
# It will:
#   1) remove the old SureViaX scaffold
#   2) create the full folder structure
#   3) write README, .gitignore, LICENSE, .env.example, docker-compose.yml
#   4) write all docs/*.md files
#   5) commit + push everything to origin/main
# =====================================================================
set -e

echo ">> Removing old SureViaX scaffold (if present)..."
rm -rf SureViaX

echo ">> Creating folder structure..."
mkdir -p docs
mkdir -p services/backend/app/api services/backend/app/core services/backend/app/models services/backend/tests
mkdir -p services/orchestrator/planner services/orchestrator/agents services/orchestrator/state_graph services/orchestrator/tools services/orchestrator/tests
mkdir -p services/model_control/registry services/model_control/router services/model_control/adapters services/model_control/benchmarks
mkdir -p services/knowledge/ingestion services/knowledge/ocr_vlm services/knowledge/rag services/knowledge/spreadsheet_engine
mkdir -p services/governance/policy_engine services/governance/rbac services/governance/network_monitor services/governance/audit services/governance/evidence_layer
mkdir -p services/sandbox/runner services/sandbox/policies
mkdir -p services/frontend/src/components services/frontend/src/pages services/frontend/src/evidence_panel services/frontend/public
mkdir -p infra/docker infra/network-policy infra/scripts
mkdir -p data/samples/scanned_reports data/samples/p_and_id data/samples/spreadsheets data/samples/sops data/vectorstore
mkdir -p tests/unit tests/integration tests/evaluation
mkdir -p scripts

echo ">> Writing root files..."
cat > "README.md" << 'PRAMAAN_EOF'
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
```

_(Setup instructions will be filled in as `services/backend` and `infra/docker` come online.)_

## License

See [`LICENSE`](LICENSE).
PRAMAAN_EOF

cat > ".gitignore" << 'PRAMAAN_EOF'
# ---- Environment / secrets ----
.env
*.env.local
*.pem
*.key

# ---- Python ----
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/
.mypy_cache/
.pytest_cache/
.ruff_cache/

# ---- Node / Frontend ----
node_modules/
dist/
build/
.next/
.parcel-cache/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# ---- Docker ----
*.pid

# ---- Models / vector data / large artifacts ----
*.gguf
*.safetensors
*.bin
data/vectorstore/*
!data/vectorstore/.gitkeep
services/model_control/registry/weights/
models/

# ---- Sample data too large to track directly ----
data/samples/**/*.pdf
data/samples/**/*.png
data/samples/**/*.jpg
!data/samples/**/.gitkeep

# ---- Logs / audit trails (generated at runtime) ----
*.log
logs/
audit/*.jsonl

# ---- OS / Editor ----
.DS_Store
Thumbs.db
.vscode/
.idea/
*.swp

# ---- Test / coverage ----
.coverage
htmlcov/
coverage.xml
PRAMAAN_EOF

cat > "LICENSE" << 'PRAMAAN_EOF'
MIT License

Copyright (c) 2026 Team PRAMAAN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
PRAMAAN_EOF

cat > ".env.example" << 'PRAMAAN_EOF'
# ==========================================
# PRAMAAN — environment configuration template
# Copy to .env and fill in real values.
# Never commit the actual .env file.
# ==========================================

# ---- App ----
APP_ENV=development
APP_PORT=8000
LOG_LEVEL=info

# ---- Database (PostgreSQL) ----
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pramaan
POSTGRES_USER=pramaan
POSTGRES_PASSWORD=changeme

# ---- Vector Store (Qdrant) ----
QDRANT_HOST=localhost
QDRANT_PORT=6333

# ---- Model Runtime ----
MODEL_RUNTIME=ollama          # ollama | vllm
MODEL_RUNTIME_HOST=localhost
MODEL_RUNTIME_PORT=11434
REASONING_MODEL_NAME=
CODING_MODEL_NAME=
OCR_MODEL_NAME=
VISION_MODEL_NAME=
EMBEDDING_MODEL_NAME=

# ---- Sandbox (code execution) ----
SANDBOX_RUNTIME=firecracker    # firecracker | docker-fallback
SANDBOX_TIMEOUT_SECONDS=30
SANDBOX_MAX_MEMORY_MB=1024

# ---- Sovereignty / Network Policy ----
EGRESS_POLICY=deny-all
NETWORK_MONITOR_ENABLED=true
AUDIT_LOG_PATH=./audit/events.jsonl

# ---- Auth / RBAC ----
JWT_SECRET=changeme
JWT_EXPIRY_MINUTES=60

# ---- Frontend ----
FRONTEND_PORT=3000
API_BASE_URL=http://localhost:8000
PRAMAAN_EOF

cat > "docker-compose.yml" << 'PRAMAAN_EOF'
version: "3.9"

# PRAMAAN — Level 1 (SIH MVP) infra
# One workstation / server target. Services get real Dockerfiles as each
# module comes online — this is the scaffold contract, not yet runnable.

services:
  backend:
    build: ./services/backend
    env_file: .env
    ports:
      - "${APP_PORT:-8000}:8000"
    depends_on:
      - postgres
      - qdrant
    networks:
      - pramaan-net

  frontend:
    build: ./services/frontend
    env_file: .env
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    depends_on:
      - backend
    networks:
      - pramaan-net

  postgres:
    image: postgres:16
    env_file: .env
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-pramaan}
      POSTGRES_USER: ${POSTGRES_USER:-pramaan}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - pramaan-pgdata:/var/lib/postgresql/data
    networks:
      - pramaan-net

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "${QDRANT_PORT:-6333}:6333"
    volumes:
      - pramaan-qdrant-data:/qdrant/storage
    networks:
      - pramaan-net

  # model-runtime, sandbox, and governance/network-monitor services
  # get added here as those modules are built (Phases 2, 4, 7).

networks:
  pramaan-net:
    driver: bridge
    # NOTE: sovereignty boundary is enforced at the network-policy layer
    # (see infra/network-policy/), not by this compose file alone.

volumes:
  pramaan-pgdata:
  pramaan-qdrant-data:
PRAMAAN_EOF

>> Writing docs/*.md...
cat > "docs/architecture.md" << 'PRAMAAN_EOF'
# PRAMAAN — Architecture

## 1. Reference Architecture

```
 USER / UI  ──▶  ORCHESTRATION  ──▶  MODEL CONTROL  ──▶  SOVEREIGNTY
 Workspaces      Planner/Executor    Registry/Router      Network policy
 Tasks            State graph        Open-weight          Audit/Policy gate
 Evidence          Validation         runtimes
 Approvals
    │                  │                  │                   │
    ▼                  ▼                  ▼                   ▼
MULTIMODAL         KNOWLEDGE            TOOLS               TRUST
OCR | VLM          Qdrant RAG        Files | Excel      Evidence trace
P&ID | scans       SOPs | manuals    Code sandbox       Approval | provenance
                                     local tools
    └──────────────────┴──────────────────┴───────────────────┘
                                  │
                                  ▼
                          DELIVERABLES
              Word / PPT / Excel / Code / Calculations
      Everything remains inside the controlled deployment boundary
```

**Principle:** logical contracts stay stable as infrastructure scales from a single workstation (SIH MVP) to a departmental pilot to a multi-site enterprise deployment — we never rewrite the core contracts, only the infra behind them.

## 2. Layers → Repo Mapping

| Layer | Core modules | Repo path | MVP status |
|---|---|---|---|
| Experience | Workbench UI, Workspaces, Tasks, Evidence, Approvals, Deliverables | `services/frontend/` | MUST |
| Orchestration | Task Engine, Planner, Agent Orchestrator, Validation | `services/orchestrator/` | MUST / SHOULD |
| Model control | Model Registry, Model Router, Runtime adapters | `services/model_control/` | MUST |
| Knowledge | Document Intelligence, OCR, VLM, RAG | `services/knowledge/` | MUST |
| Tools | File tools, Spreadsheet Engine, Code Sandbox | `services/sandbox/` (+ tool code lives alongside `orchestrator/tools`) | MUST |
| Governance | RBAC, Policy Engine, Tool Permissions, Audit | `services/governance/` | MUST / SHOULD |
| Trust | Evidence Layer, Sovereignty Control Plane, Observability | `services/governance/evidence_layer`, `network_monitor` | DIFFERENTIATOR / SHOULD |
| Scale | Evaluation automation, Deployment Manager, K8s-scale infra | `infra/` (future) | POST-SIH |

## 3. Agent Architecture

| Component | Responsibility | Repo path |
|---|---|---|
| Planner / Supervisor | Convert high-level intent into an explicit step graph | `services/orchestrator/planner` |
| Document / Vision Agent | OCR, visual understanding, drawing/scan extraction | `services/knowledge/ocr_vlm` |
| Knowledge / RAG Agent | Retrieve and cite local source evidence | `services/knowledge/rag` |
| Coding / Data Agent | Generate code and invoke deterministic data tools | `services/orchestrator/tools`, `services/sandbox` |
| Validation Agent | Check evidence, numbers and output validity | `services/orchestrator/agents` |
| Report / Deliverable Agent | Assemble final artifacts | `services/orchestrator/agents` |
| Policy layer (not a chat agent) | Gate every tool call by declared permission and policy | `services/governance/policy_engine` |

**Architecture principle:** hybrid Planner/Executor state graph. Deterministic workflows for numeric computation and safety-sensitive operations — agents are not added just to look more "agentic."

## 4. Data Flow (Login → Deliverable)

1. **Login** — Tourist/Client → Firebase-style Auth → ID token (`services/backend`)
2. **Core** — Client → FastAPI (`services/backend`) → routes to orchestration, AI scoring, blockchain-free here (n/a for PRAMAAN — no blockchain layer, unlike the earlier Ignius topic)
3. **Plan** — Orchestrator (`services/orchestrator`) builds a visible step graph from the instruction
4. **Model routing** — Model Router (`services/model_control`) selects models per task capability + security constraints
5. **Knowledge grounding** — RAG Agent (`services/knowledge/rag`) retrieves local SOP/manual evidence with citations
6. **Tool execution** — Spreadsheet Engine / file tools / sandboxed code run deterministically (`services/sandbox`)
7. **Validation** — Validation Agent checks evidence + numeric claims before finalising
8. **Governance gate** — every tool call passes through the Policy Engine (`services/governance/policy_engine`); network egress is deny-by-default (`services/governance/network_monitor`)
9. **Deliverable** — Report/Deliverable Agent assembles the final `.docx`/`.pptx`/`.xlsx`/code artifact
10. **Audit** — full execution, evidence, and policy trail is stored (`services/governance/audit`)

## 5. Security Boundary

| Threat / concern | PRAMAAN control |
|---|---|
| Cloud data leakage | No cloud dependency in the confidential workflow; local model runtime |
| Malicious document / prompt injection | Context separation + least-privilege tool scope + policy gate + containment |
| Generated code risk | Sandbox isolation + no network + resource/time limits + no secrets |
| Unauthorized document access | RBAC + document-level permissions enforced during retrieval |
| Hallucinated claims | Evidence requirement + validation + human approval for sensitive deliverables |
| Network policy breach | Deny-all egress + continuous telemetry + live block demonstration |
| Stale knowledge | Document versioning, superseded flags, citations |

> **Honesty rule:** never claim "100% secure." The defensible claim is that the system structurally limits the blast radius, enforces the sovereignty boundary, and makes violations observable.

## 6. Infra Targets

| Level | Target | Approach |
|---|---|---|
| Level 1 — SIH MVP | One workstation/server, mid-range GPU | Docker Compose, local model runtime, FastAPI, Postgres, Qdrant, local OCR/VLM, sandbox, network policy |
| Level 2 — Pilot | Single department/organisation | Shared local inference, stronger RBAC, production serving, richer observability |
| Level 3 — Enterprise | Multi-user / multi-site | Multi-GPU, Kubernetes-scale deployment, Milvus-scale vector storage where justified |

## 7. Technology Decisions (MVP)

| Area | Choice | Why |
|---|---|---|
| Inference | vLLM (serving) / Ollama (dev) | Production-style local serving + simple dev workflow |
| Orchestration | LangGraph-style explicit state graph | Checkpointing, controlled tool flow, human-in-the-loop support |
| Vector store | Qdrant | Self-hosted simplicity + metadata filtering |
| Backend | FastAPI | Python-native for ML/AI stack, async APIs |
| Database | PostgreSQL | MVP + scale path without early migration |
| Containerisation | Docker Compose | Best fit for single-workstation hackathon MVP |
| OCR + Vision | PaddleOCR-VL + Qwen-VL-class model | Specialised OCR/layout plus general visual reasoning |
| Sandbox | Firecracker/Kata (lighter fallback if hardware constrains) | Strong isolation for untrusted generated code |

Final model/runtime selections remain subject to benchmarking on the team's actual hardware — the architecture is intentionally model-agnostic (Model Registry + adapter pattern, no hard-coding to one model family).
PRAMAAN_EOF

cat > "docs/requirements-mapping.md" << 'PRAMAAN_EOF'
# PRAMAAN — Requirements Mapping

## Source of Truth

The official **SIH26117** description defines the baseline. Product innovation is layered on top of these requirements — never substituted for them.

## Official Requirement → PRAMAAN Interpretation

| Official requirement | PRAMAAN interpretation | Repo path |
|---|---|---|
| Self-hosted / air-gapped | All core processing runs within the organisation-controlled deployment | `infra/network-policy/` |
| Multiple open-weight models | Model Registry + pluggable ModelAdapter interface | `services/model_control/registry`, `adapters` |
| Automatic model selection | Model Router chooses according to task capability and constraints | `services/model_control/router` |
| Add new models without redesign | New model registered via configuration/adapter, not application rewrite | `services/model_control/adapters` |
| Agentic multi-step work | Planner/Executor state graph with tool calls and validation | `services/orchestrator/planner`, `state_graph` |
| Local file read/write | Workspace tools operating inside the sovereign boundary | `services/orchestrator/tools` |
| Sandboxed code execution | Isolated execution, no external network access, resource limits | `services/sandbox/runner` |
| Spreadsheet work | Deterministic computation plus LLM explanation, not LLM arithmetic | `services/knowledge/spreadsheet_engine` |
| Internal document search | Local RAG over manuals, SOPs and correspondence | `services/knowledge/rag` |
| OCR + vision + drawings + handwriting | Local multimodal pipeline for scanned and visual industrial data | `services/knowledge/ocr_vlm` |
| Real deliverables | Word, PPT, Excel, code and calculations — not chat-only responses | `services/orchestrator/agents` (deliverable agent), `services/frontend` |
| Visible proof of no external calls | Network monitor/logging with enforceable egress controls | `services/governance/network_monitor` |

## Acceptance-Test Mindset

- Every official requirement maps to a **visible user behaviour** and an **acceptance test**.
- The final build is judged by whether each requirement can be **demonstrated live**, not whether it exists only in the architecture diagram.
- Where evidence is not yet available, label the item as an **assumption** and validate it on real hardware/data before freezing scope.

## Demo Contract — Six Pillars to Prove Live

These six capabilities are the non-negotiable demo contract:

1. **Model routing** — Task A and Task B automatically routed to different open-weight models.
2. **Genuine agentic execution** — One instruction → visible plan → tools → iteration → validation → result.
3. **Multimodal understanding** — Scanned PDF / image / P&ID → structured, verifiable output.
4. **Coding + verification** — Generated code actually runs in a sandbox and is tested.
5. **Sovereignty proof** — Outbound request visibly blocked and logged.
6. **Real deliverables** — Actual `.docx`/`.pptx`/`.xlsx`/code artifact is produced.

Each pillar needs an owning module (see the table above) and an owning team member (see `team-structure.md`) responsible for making it demo-ready.
PRAMAAN_EOF

cat > "docs/demo-script.md" << 'PRAMAAN_EOF'
# PRAMAAN — Demo Script

## Flagship Use Case

> "Review this confidential package, identify key findings, compare them against the relevant SOP and historical record, and prepare an approval note."

| Step | PRAMAAN behaviour |
|---|---|
| 1. Intent | User uploads scanned report + P&ID + spreadsheet + SOP and gives one instruction |
| 2. Plan | Planner creates a visible step graph |
| 3. Model routing | OCR/VLM, reasoning, and data tools are selected according to capability |
| 4. Knowledge grounding | Relevant SOP/history is retrieved locally with citations |
| 5. Tool execution | Spreadsheet engine recomputes values; document/vision tools extract evidence |
| 6. Validation | Numeric claims and citations are checked before finalisation |
| 7. Human approval | Sensitive approval note requires explicit user approval |
| 8. Deliverable | A real `.docx` approval note is generated |
| 9. Audit | Full execution, evidence, and policy trail is stored |

**Why this works as a demo:**
- Demonstrates several official requirements inside one coherent workflow instead of disconnected feature demos.
- The judge watches the plan, model choices, evidence, tools, and final artifact appear.
- The coding/sandbox task then serves as an independent proof of safe tool execution.

## Recommended 6–7 Minute Demo Timeline

| Time | Moment | Proof |
|---|---|---|
| 0:00–0:45 | Sovereign boundary | Network monitor / blocked external attempt |
| 0:45–1:30 | Model registry + routing | Different tasks visibly use different models |
| 1:30–3:30 | Composite workflow | Scanned report + P&ID + spreadsheet + SOP → plan → evidence |
| 3:30–4:15 | Deliverable | Real approval-note `.docx` with evidence |
| 4:15–5:15 | Coding | Local code generation + sandbox execution + tests |
| 5:15–6:00 | Evidence/audit | Source, model, tool, approval trace |
| 6:00–6:45 | Close | Scale path + why not generic local AI |

## What Must Be Perfect

1. **The composite signature workflow** (the flagship use case above).
2. **The sovereignty-proof moment** (live blocked outbound request).

Everything else can be less polished than these two.

## High-Value Judge Questions — Answer Bank

| Question | Defensible answer |
|---|---|
| How is confidentiality maintained? | Local models + local data + deny-all network egress + tool permissions + sandbox isolation + audit/sovereignty monitoring |
| Why not just use Ollama? | Ollama is an inference component. PRAMAAN adds routing, agents, tools, governance, evidence, deliverables, and sovereignty proof |
| Why is it really agentic? | One high-level instruction produces a plan, tool calls, iteration, validation, and a final artifact without step-by-step prompting |
| How is it different from RAG? | RAG is one module. PRAMAAN executes work across models, vision, files, code, spreadsheets, validation, and deliverables |
| What if the model is manipulated? | Assume manipulation is possible; constrain what the agent can do and contain the blast radius below the model |
| How do you add a new model? | ModelAdapter + Registry: register capabilities and runtime metadata without changing core application logic |
| Why smaller models? | The PS explicitly permits smaller open-weight models when 120B-class hardware is unavailable; the system is model-agnostic |
| What is actually innovative? | The integrated sovereign execution architecture: capability/security-aware routing, observable sovereignty, evidence-linked multimodal work, deterministic computation |
| How will it scale? | Stable service contracts remain the same while infrastructure grows from one workstation to departmental and multi-site deployments |
| Why should MRPL trust a student prototype? | The demo uses public/synthetic data. The goal is to prove the architecture and controls, then validate a controlled pilot pathway |

## The One-Liner

> "Most teams will show a local AI that can answer. We want to show an AI system that can actually do confidential work — and prove where the data stayed, which models/tools were used, and what evidence supports the result."

## Honesty Rule

Do **not** claim "100% secure." The defensible claim: the system structurally limits the blast radius, enforces the sovereignty boundary, and makes violations observable. Never claim prompt injection or model manipulation is impossible.
PRAMAAN_EOF

cat > "docs/roadmap.md" << 'PRAMAAN_EOF'
# PRAMAAN — Implementation Roadmap

## Phases

| Phase | Focus | Exit milestone |
|---|---|---|
| 0 | Official PS validation, sample data, hardware decision | Team-approved requirements + benchmark plan |
| 1 | Core local infrastructure | Air-gapped Docker stack boots and responds |
| 2 | Model registry/runtime | At least two models available through one application interface |
| 3 | Agent orchestration | One instruction completes a multi-step task |
| 4 | Tools + sandbox | Code executes and network access is blocked |
| 5 | Multimodal | Scanned report + P&ID are processed successfully |
| 6 | Knowledge/RAG | Local SOP query returns correct citations |
| 7 | Security/sovereignty | Outbound attempt blocked and shown live |
| 8 | Deliverables + trust | Real `.docx` with evidence trail |
| 9 | UX integration | Signature workflow works through UI |
| 10 | Evaluation | Task suite measured on actual hardware/data |
| 11 | Demo hardening | Full demo runs reliably multiple times |
| 12 | Post-SIH productisation | Pilot-ready architecture and deployment story |

## Parallel Work Strategy

- **Roles 1–2** (AI/Agent Architect, ML Systems/Runtime) build the agent/model layer against stable contracts.
- **Roles 3–4** (Backend/Infrastructure, Security/Governance) build infrastructure/security in parallel from Day 1.
- **Role 5** (Multimodal/ML) validates multimodal pipelines independently using public/synthetic documents.
- **Role 6** (Frontend/UX+Product) integrates continuously against the stable API/event contracts instead of waiting for the end.

## MVP Discipline

| Scope | What belongs here |
|---|---|
| **MUST BUILD** | Model registry/router, planner/executor, file tools, code sandbox, OCR/VLM, RAG, spreadsheet engine, deliverables, audit, sovereignty enforcement |
| **SHOULD BUILD** | Evidence layer, human approval queue, basic RBAC, admin model registration, validation agent |
| **SIGNATURE DIFFERENTIATORS** | Sovereignty Control Plane, click-to-source multimodal evidence, capability/security-aware routing |
| **POST-SIH** | Kubernetes-scale deployment, advanced evaluation automation, multi-site manager, advanced replay/ledger/tool-risk scoring |

## Immediate Next Actions

| Priority | Action | Owner |
|---|---|---|
| P0 | Freeze official PS requirements and acceptance tests | Entire team |
| P0 | Confirm exact demo GPU / workstation hardware | Backend + Runtime |
| P0 | Collect public/synthetic scanned reports, P&IDs, spreadsheet and SOP samples | Multimodal + Product |
| P0 | Benchmark 2–3 local model candidates on the real hardware | Runtime + AI |
| P1 | Lock API contracts: ModelAdapter, ToolAdapter, AgentState, EvidenceRecord, AuditEvent | AI + Backend |
| P1 | Build air-gapped base stack and network policy first | Backend + Security |
| P1 | Prototype the composite signature workflow before polishing UI | AI + Multimodal |
| P1 | Make sovereignty-block demonstration deterministic and repeatable | Security |
| P2 | Add evidence graph, approval queue, and polished workbench UX | Frontend + Multimodal |
| P2 | Run task-suite evaluation and repeated full-demo rehearsals | Entire team |

## Evaluation Framework

| Area | Metrics / checks |
|---|---|
| AI quality | Task completion, groundedness, citation accuracy, OCR/extraction quality, hallucination rate |
| Agent quality | Plan success, tool selection, step efficiency, recovery |
| Routing | Correct model selection, fallback success, resource utilisation |
| Security | Unauthorized tool blocks, outbound blocks, prompt-injection containment |
| Performance | p50/p95/p99 latency, throughput, VRAM/CPU/RAM |
| Product | Audit completeness, reproducibility, deployment reliability |

## Key Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Multimodal accuracy | P&ID/handwriting errors can undermine trust | Benchmark early on representative samples; flag uncertainty; keep human review |
| Demo fragility | Six pillars in a few minutes creates many failure points | Rehearse repeatedly; isolate pipelines; controlled fallback |
| Hardware constraints | VLM + reasoning + coding models compete for VRAM | Quantization, staged loading, routing, actual hardware benchmarks |
| Scope creep | Enterprise features can consume hackathon time | Strict MUST/SHOULD/DIFFERENTIATOR/POST-SIH boundary |
| Security overclaiming | Overclaiming can destroy jury credibility | State the exact security boundary and its limits |
| Integration complexity | Six parallel workstreams can drift | Shared contracts from Day 1; continuous integration |
PRAMAAN_EOF

cat > "docs/team-structure.md" << 'PRAMAAN_EOF'
# PRAMAAN — Team Structure

## Team Principle

Every member owns a **build-critical technical/product area**. There is no "documentation-only" role.

## 6 Roles

| # | Role | Primary ownership | Visible output | Repo path |
|---|---|---|---|---|
| 1 | AI / Agent Architect | Planner, Agent Orchestrator, Model Router, task state | Working multi-step agent loop + routing logic | `services/orchestrator/` |
| 2 | ML Systems / Runtime | Model Registry, vLLM/Ollama integration, offline model loading, hardware benchmark | Model fleet loads, health-checks, and routes | `services/model_control/` |
| 3 | Backend / Infrastructure | FastAPI, Postgres, Qdrant, Docker Compose, service contracts | Entire stack boots locally and APIs integrate | `services/backend/`, `infra/` |
| 4 | Security / Governance | Sovereignty Control Plane, Policy Engine, tool permissions, sandbox isolation | Live blocked network call + audit trail | `services/governance/`, `services/sandbox/` |
| 5 | Multimodal / ML | OCR/VLM, RAG ingestion/retrieval, spreadsheet deterministic engine | Scanned report + P&ID + spreadsheet pipelines | `services/knowledge/` |
| 6 | Frontend / UX + Product | Workbench UI, Evidence Panel, Deliverables, approval flow, demo integration | Complete end-to-end user experience | `services/frontend/` |

**Suggested assignment** (continuity from prior team roles — adjust as needed):

| Role | Member |
|---|---|
| 1. AI / Agent Architect | Atharva |
| 2. ML Systems / Runtime | Niraj |
| 3. Backend / Infrastructure | Arpit |
| 4. Security / Governance | Sahil |
| 5. Multimodal / ML | Aarya |
| 6. Frontend / UX + Product | Atharva (Pawar) |

## Parallel Work Strategy

- **Roles 1–2** build the agent/model layer against stable contracts.
- **Roles 3–4** build infrastructure/security in parallel from Day 1.
- **Role 5** validates multimodal pipelines independently using public/synthetic documents.
- **Role 6** integrates continuously against the stable API/event contracts instead of waiting for the end.

## Team-to-Demo Mapping

| Demo moment | Primary owner | Backup/support |
|---|---|---|
| Model auto-selection | AI Architect + Runtime | Backend |
| Composite multimodal workflow | Multimodal + AI Architect | Frontend |
| Sandbox coding | Security + Backend | Runtime |
| Sovereignty proof | Security | Backend |
| Evidence + approval UX | Frontend/Product | Multimodal |
| Final narrative / jury defence | Entire team | Product lead coordinates |

## Definition of Done (per feature)

Implemented → locally tested → error-handled → API documented → integrated → reviewed → tested with dependent module → no regression → docs updated → demo-ready.
PRAMAAN_EOF

echo ">> Writing scaffold placeholder scripts..."
touch scripts/setup.sh scripts/benchmark.sh

echo ">> Adding .gitkeep to empty directories..."
find . -type d -not -path "./.git*" -empty -exec touch {}/.gitkeep \;

echo ">> Staging, committing, and pushing..."
git add -A
git commit -m "chore: finalize PRAMAAN repo — structure, docs, config (SIH26117)"
git push -u origin main

echo ""
echo "✅ PRAMAAN repo finalized and pushed to GitHub."