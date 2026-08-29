# PRAMAAN Final Architecture

## Product loop

`User → Task → Planner → Model Router → Local Model → Validated Plan → Executor → Local Tools/RAG → Evidence → Approval/Policy → Deliverable → Audit`

## Local AI roles

- Reasoning/planning: configured Ollama reasoning model (default `qwen3:4b`)
- Coding: configured Ollama coding model (default `qwen3:4b`)
- Vision/OCR: configured Ollama vision model (default `gemma3:4b`)
- Embeddings: configured Ollama embedding model (default `nomic-embed-text`)

## Persistence

PostgreSQL is the durable relational store. A small `task_runs` runtime table stores serialized AgentState checkpoints so execution survives a backend restart. Qdrant is used for vector retrieval; Ollama supplies local embeddings.

## Network boundary

AI inference is local. `OLLAMA_NO_CLOUD=1` is required. Docker Desktop deployments can reach host Ollama through `host.docker.internal`; see `docs/OLLAMA_SETUP.md`.
