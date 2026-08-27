# PRAMAAN — Implementation Roadmap

## Phases

| Phase | Focus                                                  | Exit milestone                                                  |
| ----- | ------------------------------------------------------ | --------------------------------------------------------------- |
| 0     | Official PS validation, sample data, hardware decision | Team-approved requirements + benchmark plan                     |
| 1     | Core local infrastructure                              | Air-gapped Docker stack boots and responds                      |
| 2     | Model registry/runtime                                 | At least two models available through one application interface |
| 3     | Agent orchestration                                    | One instruction completes a multi-step task                     |
| 4     | Tools + sandbox                                        | Code executes and network access is blocked                     |
| 5     | Multimodal                                             | Scanned report + P&ID are processed successfully                |
| 6     | Knowledge/RAG                                          | Local SOP query returns correct citations                       |
| 7     | Security/sovereignty                                   | Outbound attempt blocked and shown live                         |
| 8     | Deliverables + trust                                   | Real `.docx` with evidence trail                                |
| 9     | UX integration                                         | Signature workflow works through UI                             |
| 10    | Evaluation                                             | Task suite measured on actual hardware/data                     |
| 11    | Demo hardening                                         | Full demo runs reliably multiple times                          |
| 12    | Post-SIH productisation                                | Pilot-ready architecture and deployment story                   |

## Parallel Work Strategy

- **Roles 1–2** (AI/Agent Architect, ML Systems/Runtime) build the agent/model layer against stable contracts.
- **Roles 3–4** (Backend/Infrastructure, Security/Governance) build infrastructure/security in parallel from Day 1.
- **Role 5** (Multimodal/ML) validates multimodal pipelines independently using public/synthetic documents.
- **Role 6** (Frontend/UX+Product) integrates continuously against the stable API/event contracts instead of waiting for the end.

## MVP Discipline

| Scope                         | What belongs here                                                                                                                                 |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MUST BUILD**                | Model registry/router, planner/executor, file tools, code sandbox, OCR/VLM, RAG, spreadsheet engine, deliverables, audit, sovereignty enforcement |
| **SHOULD BUILD**              | Evidence layer, human approval queue, basic RBAC, admin model registration, validation agent                                                      |
| **SIGNATURE DIFFERENTIATORS** | Sovereignty Control Plane, click-to-source multimodal evidence, capability/security-aware routing                                                 |
| **POST-SIH**                  | Kubernetes-scale deployment, advanced evaluation automation, multi-site manager, advanced replay/ledger/tool-risk scoring                         |

## Immediate Next Actions

| Priority | Action                                                                                | Owner                 |
| -------- | ------------------------------------------------------------------------------------- | --------------------- |
| P0       | Freeze official PS requirements and acceptance tests                                  | Entire team           |
| P0       | Confirm exact demo GPU / workstation hardware                                         | Backend + Runtime     |
| P0       | Collect public/synthetic scanned reports, P&IDs, spreadsheet and SOP samples          | Multimodal + Product  |
| P0       | Benchmark 2–3 local model candidates on the real hardware                             | Runtime + AI          |
| P1       | Lock API contracts: ModelAdapter, ToolAdapter, AgentState, EvidenceRecord, AuditEvent | AI + Backend          |
| P1       | Build air-gapped base stack and network policy first                                  | Backend + Security    |
| P1       | Prototype the composite signature workflow before polishing UI                        | AI + Multimodal       |
| P1       | Make sovereignty-block demonstration deterministic and repeatable                     | Security              |
| P2       | Add evidence graph, approval queue, and polished workbench UX                         | Frontend + Multimodal |
| P2       | Run task-suite evaluation and repeated full-demo rehearsals                           | Entire team           |

## Evaluation Framework

| Area          | Metrics / checks                                                                             |
| ------------- | -------------------------------------------------------------------------------------------- |
| AI quality    | Task completion, groundedness, citation accuracy, OCR/extraction quality, hallucination rate |
| Agent quality | Plan success, tool selection, step efficiency, recovery                                      |
| Routing       | Correct model selection, fallback success, resource utilisation                              |
| Security      | Unauthorized tool blocks, outbound blocks, prompt-injection containment                      |
| Performance   | p50/p95/p99 latency, throughput, VRAM/CPU/RAM                                                |
| Product       | Audit completeness, reproducibility, deployment reliability                                  |

## Key Risks

| Risk                   | Why it matters                                           | Mitigation                                                                     |
| ---------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Multimodal accuracy    | P&ID/handwriting errors can undermine trust              | Benchmark early on representative samples; flag uncertainty; keep human review |
| Demo fragility         | Six pillars in a few minutes creates many failure points | Rehearse repeatedly; isolate pipelines; controlled fallback                    |
| Hardware constraints   | VLM + reasoning + coding models compete for VRAM         | Quantization, staged loading, routing, actual hardware benchmarks              |
| Scope creep            | Enterprise features can consume hackathon time           | Strict MUST/SHOULD/DIFFERENTIATOR/POST-SIH boundary                            |
| Security overclaiming  | Overclaiming can destroy jury credibility                | State the exact security boundary and its limits                               |
| Integration complexity | Six parallel workstreams can drift                       | Shared contracts from Day 1; continuous integration                            |
