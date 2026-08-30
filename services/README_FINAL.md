# PRAMAAN `services/` — final integrated build

This package is the backend/service layer for PRAMAAN Sovereign Workbench.

## Core local services

- PostgreSQL: default `localhost:5433`, database `pramaan`
- Qdrant: default `http://localhost:6333`
- Ollama: default `http://localhost:11434`
- Reasoning/summarization/coding: `qwen3:4b`
- Vision/OCR/document analysis: `gemma3:4b`
- Embeddings: `nomic-embed-text`

## Runtime flow

User/Auth
→ Task
→ Planner
→ Tool/Model routing
→ File/OCR processing
→ Embeddings
→ Qdrant retrieval
→ Evidence
→ Reasoning
→ Final response
→ Artifact generation
→ Deliverable registration
→ Audit/persistence

## Local development identity

The current local-development auth contract uses the `X-User-Email` request header.
The backend automatically provisions the PostgreSQL user record on first use.

This is a development identity mechanism, not production authentication. A production
deployment should replace it with a verified Firebase/OIDC/JWT identity.

## Recommended startup

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn services.backend.app.main:app --reload --port 8000
```

Ensure PostgreSQL, Qdrant and Ollama are running before executing tasks.

Check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:6333
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Frontend lives under `services/frontend`.

## Important behavior

A run is only considered completed after all planned steps finish successfully.
When a task explicitly asks for a file (for example, "give me the summary in a .txt file"),
the planner creates an artifact step and the backend registers the resulting file as a
deliverable.

User-scoped task/run/evidence/deliverable APIs require the authenticated identity and
must not expose another user's resources.

## Validation performed on this source package

- Python source compilation: passed for all 108 source `.py` files.
- Orchestrator tests: 18 passed.
- Model Control tests: 14 passed.
- Direct live Qdrant upsert/query was validated during this debugging session.
- The analysis environment did not have the local Qdrant service running or the
  frontend's complete Node dependency installation, so full live UI/E2E execution
  was not reproduced here.
