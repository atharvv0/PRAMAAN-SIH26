# PRAMAAN — Requirements Mapping

## Source of Truth

The official **SIH26117** description defines the baseline. Product innovation is layered on top of these requirements — never substituted for them.

## Official Requirement → PRAMAAN Interpretation

| Official requirement                  | PRAMAAN interpretation                                                  | Repo path                                                               |
| ------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Self-hosted / air-gapped              | All core processing runs within the organisation-controlled deployment  | `infra/network-policy/`                                                 |
| Multiple open-weight models           | Model Registry + pluggable ModelAdapter interface                       | `services/model_control/registry`, `adapters`                           |
| Automatic model selection             | Model Router chooses according to task capability and constraints       | `services/model_control/router`                                         |
| Add new models without redesign       | New model registered via configuration/adapter, not application rewrite | `services/model_control/adapters`                                       |
| Agentic multi-step work               | Planner/Executor state graph with tool calls and validation             | `services/orchestrator/planner`, `state_graph`                          |
| Local file read/write                 | Workspace tools operating inside the sovereign boundary                 | `services/orchestrator/tools`                                           |
| Sandboxed code execution              | Isolated execution, no external network access, resource limits         | `services/sandbox/runner`                                               |
| Spreadsheet work                      | Deterministic computation plus LLM explanation, not LLM arithmetic      | `services/knowledge/spreadsheet_engine`                                 |
| Internal document search              | Local RAG over manuals, SOPs and correspondence                         | `services/knowledge/rag`                                                |
| OCR + vision + drawings + handwriting | Local multimodal pipeline for scanned and visual industrial data        | `services/knowledge/ocr_vlm`                                            |
| Real deliverables                     | Word, PPT, Excel, code and calculations — not chat-only responses       | `services/orchestrator/agents` (deliverable agent), `services/frontend` |
| Visible proof of no external calls    | Network monitor/logging with enforceable egress controls                | `services/governance/network_monitor`                                   |

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
