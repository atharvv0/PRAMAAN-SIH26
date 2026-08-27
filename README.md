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

```text
User / UI → Orchestration (Planner/Executor) → Model Control (Registry/Router) → Sovereignty (Network policy/Audit)
                ↓                    ↓                    ↓                         ↓

           Multimodal           Knowledge             Tools                    Trust
         (OCR/VLM, P&ID)      (RAG over SOPs)     (Files, Sandbox)       (Evidence, Provenance)

                └────────────────────┴────────────────────┴──────────────────────────┘
                                             ↓

                                  Deliverables (Word/PPT/Excel/Code)

                         Everything stays inside the controlled deployment boundary