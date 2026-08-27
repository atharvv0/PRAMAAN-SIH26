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
