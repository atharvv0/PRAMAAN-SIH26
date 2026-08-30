# PRAMAAN final setup notes

## Core local services
- PostgreSQL: backend database
- Qdrant: `http://127.0.0.1:6333`
- Ollama: `http://127.0.0.1:11434`

## Ollama models
- `qwen3:4b` -> reasoning, summarization, coding
- `gemma3:4b` -> OCR, vision, document analysis
- `nomic-embed-text:latest` -> RAG embeddings

## Roles
Operator can create/run work and view their own resources.
Reviewer can review operator work and approve/reject pending approval items.
Admin has reviewer privileges and can manage users/roles and view audit records.

New local users default to operator. For a local demo installation, set:

`PRAMAAN_ADMIN_EMAILS=admin@example.com`
`PRAMAAN_REVIEWER_EMAILS=reviewer@example.com`

These values are comma-separated. The backend promotes matching database users at startup. The authoritative role is stored in PostgreSQL `users.role`.

The current browser login is a local development access layer. Production should replace the `X-User-Email` bridge with verified Firebase/OIDC/JWT identity claims.

## AI Assistant
Use the `AI Assistant` page. It calls the local reasoning capability and never intentionally returns hidden chain-of-thought. Task-specific context can be added by the backend when a task ID is supplied.

## E2E task flow
Task -> planner -> tool/model execution -> evidence/RAG where appropriate -> reasoning -> final response -> artifact generation -> Deliverable -> download.

A task is not considered successful merely because an intermediate model call succeeds; final requested outcomes and required artifacts must exist.
