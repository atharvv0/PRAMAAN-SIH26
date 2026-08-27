# PRAMAAN — Demo Script

## Flagship Use Case

> "Review this confidential package, identify key findings, compare them against the relevant SOP and historical record, and prepare an approval note."

| Step                   | PRAMAAN behaviour                                                                |
| ---------------------- | -------------------------------------------------------------------------------- |
| 1. Intent              | User uploads scanned report + P&ID + spreadsheet + SOP and gives one instruction |
| 2. Plan                | Planner creates a visible step graph                                             |
| 3. Model routing       | OCR/VLM, reasoning, and data tools are selected according to capability          |
| 4. Knowledge grounding | Relevant SOP/history is retrieved locally with citations                         |
| 5. Tool execution      | Spreadsheet engine recomputes values; document/vision tools extract evidence     |
| 6. Validation          | Numeric claims and citations are checked before finalisation                     |
| 7. Human approval      | Sensitive approval note requires explicit user approval                          |
| 8. Deliverable         | A real `.docx` approval note is generated                                        |
| 9. Audit               | Full execution, evidence, and policy trail is stored                             |

**Why this works as a demo:**

- Demonstrates several official requirements inside one coherent workflow instead of disconnected feature demos.
- The judge watches the plan, model choices, evidence, tools, and final artifact appear.
- The coding/sandbox task then serves as an independent proof of safe tool execution.

## Recommended 6–7 Minute Demo Timeline

| Time      | Moment                   | Proof                                                       |
| --------- | ------------------------ | ----------------------------------------------------------- |
| 0:00–0:45 | Sovereign boundary       | Network monitor / blocked external attempt                  |
| 0:45–1:30 | Model registry + routing | Different tasks visibly use different models                |
| 1:30–3:30 | Composite workflow       | Scanned report + P&ID + spreadsheet + SOP → plan → evidence |
| 3:30–4:15 | Deliverable              | Real approval-note `.docx` with evidence                    |
| 4:15–5:15 | Coding                   | Local code generation + sandbox execution + tests           |
| 5:15–6:00 | Evidence/audit           | Source, model, tool, approval trace                         |
| 6:00–6:45 | Close                    | Scale path + why not generic local AI                       |

## What Must Be Perfect

1. **The composite signature workflow** (the flagship use case above).
2. **The sovereignty-proof moment** (live blocked outbound request).

Everything else can be less polished than these two.

## High-Value Judge Questions — Answer Bank

| Question                                   | Defensible answer                                                                                                                                                      |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| How is confidentiality maintained?         | Local models + local data + deny-all network egress + tool permissions + sandbox isolation + audit/sovereignty monitoring                                              |
| Why not just use Ollama?                   | Ollama is an inference component. PRAMAAN adds routing, agents, tools, governance, evidence, deliverables, and sovereignty proof                                       |
| Why is it really agentic?                  | One high-level instruction produces a plan, tool calls, iteration, validation, and a final artifact without step-by-step prompting                                     |
| How is it different from RAG?              | RAG is one module. PRAMAAN executes work across models, vision, files, code, spreadsheets, validation, and deliverables                                                |
| What if the model is manipulated?          | Assume manipulation is possible; constrain what the agent can do and contain the blast radius below the model                                                          |
| How do you add a new model?                | ModelAdapter + Registry: register capabilities and runtime metadata without changing core application logic                                                            |
| Why smaller models?                        | The PS explicitly permits smaller open-weight models when 120B-class hardware is unavailable; the system is model-agnostic                                             |
| What is actually innovative?               | The integrated sovereign execution architecture: capability/security-aware routing, observable sovereignty, evidence-linked multimodal work, deterministic computation |
| How will it scale?                         | Stable service contracts remain the same while infrastructure grows from one workstation to departmental and multi-site deployments                                    |
| Why should MRPL trust a student prototype? | The demo uses public/synthetic data. The goal is to prove the architecture and controls, then validate a controlled pilot pathway                                      |

## The One-Liner

> "Most teams will show a local AI that can answer. We want to show an AI system that can actually do confidential work — and prove where the data stayed, which models/tools were used, and what evidence supports the result."

## Honesty Rule

Do **not** claim "100% secure." The defensible claim: the system structurally limits the blast radius, enforces the sovereignty boundary, and makes violations observable. Never claim prompt injection or model manipulation is impossible.
