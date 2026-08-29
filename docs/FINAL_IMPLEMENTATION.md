# PRAMAAN Final Implementation Handoff

## Implemented in this baseline

- Root React frontend consolidated under `services/frontend`.
- FastAPI task/run/file APIs connected to PostgreSQL through a repository layer.
- Durable task/run state via `task_runs` checkpoint table.
- Task steps, tool calls, model calls and evidence persisted.
- Real local Ollama reasoning integration through Model Control.
- Real local Ollama vision/OCR path for images and rendered PDF pages.
- Local Ollama embeddings + Qdrant retrieval path.
- Real local coding route + restricted Python execution tool.
- Approval queue with resume behaviour.
- Real Word approval-note generation and download endpoint.
- Frontend file upload and real API mode.
- Sovereignty metadata and network-policy visibility.

## Environment defaults

`REASONING_MODEL_NAME=qwen3:4b`
`CODING_MODEL_NAME=qwen3:4b`
`VISION_MODEL_NAME=gemma3:4b`
`OCR_MODEL_NAME=gemma3:4b`
`EMBEDDING_MODEL_NAME=nomic-embed-text`
`OLLAMA_NO_CLOUD=1`
`OLLAMA_MODELS=D:\\OllamaModels`

Change only the model names if the target machine has different pulled model IDs.

## First browser acceptance test

1. Start Postgres + Qdrant.
2. Start local Ollama with the models above available.
3. Start backend.
4. Start frontend.
5. Sign in as Operator.
6. Create a task and upload a real PDF/image.
7. Run the task.
8. Verify model routing, evidence and audit events.
9. Approve when the run pauses for HITL.
10. Download the generated Word deliverable.
11. Disconnect internet and repeat the AI workflow to demonstrate local-only inference.
