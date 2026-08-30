# PRAMAAN Services — Final E2E Repair Report

## Scope

This package is the corrected `services/` tree based on the latest services ZIP supplied for PRAMAAN.

The repair focused on the real runtime path rather than only making the application start.

## Current state

### Working / repaired

- Backend API startup and health endpoint.
- PostgreSQL ORM alignment for `model_versions.vram_required_gb` (`NUMERIC`).
- Automatic local user provisioning on first authenticated request.
- User-scoped task/history access.
- User-scoped run/evidence/deliverable access.
- Protected file downloads.
- Central frontend propagation of `X-User-Email` for local development.
- Tool registry/planner naming alignment.
- Real local Ollama model preference.
- `qwen3:4b` role mapping for reasoning, summarization and coding.
- `gemma3:4b` role mapping for OCR/vision/document analysis.
- `nomic-embed-text` remains an embeddings-only model.
- Real Qdrant server path in production mode; no silent fallback to in-memory when Qdrant is unavailable.
- User/workspace metadata filters in Qdrant retrieval.
- PDF/DOCX/XLSX/text extraction support for the ingestion path.
- Final reasoning step for answer-oriented tasks.
- Task output-spec detection for explicit file/deliverable requests.
- TXT/MD/JSON/CSV/DOCX artifact generation.
- Artifact registration into `FileRecord` + `Deliverable`.
- Final response propagation to API and frontend.
- Frontend run page displays final response and generated artifact links.
- Stale / obsolete tests updated to match the repaired production execution graph.
- Python UTF-8 BOM issues in governance modules removed.

### Deliberately unchanged / isolated

- Demo/naive tools remain in their modules for tests/backward compatibility, but the production planner uses model-backed tools.
- Local `X-User-Email` authentication is a development identity mechanism. Production should verify Firebase/OIDC/JWT and derive identity server-side.
- Qdrant container storage persistence still depends on Docker volume configuration outside the `services/` tree.

## Intended runtime

User
→ authenticated identity
→ task
→ planner
→ dependency-aware executor
→ file/OCR processing
→ model routing
→ embeddings
→ Qdrant retrieval
→ evidence
→ reasoning
→ final response
→ artifact generation
→ deliverable registration
→ audit/persistence
→ frontend

For an explicit request such as:
"Summarize this file in 10 lines and give me a .txt file"

the plan is:

file.read
→ text.summarize_model
→ model.reason
→ artifact.write
→ registered deliverable
→ final response

For an inspection/evidence task, knowledge retrieval is inserted before the final reasoning step.

## Local models

Recommended roles for the supplied development environment:

- qwen3:4b — reasoning, summarize_text, coding
- gemma3:4b — vision, OCR, document analysis
- nomic-embed-text — embeddings / RAG only
- demo-fallback — last-resort offline fallback

## Validation performed in this environment

- 108 Python source files compiled successfully after the final edits.
- 45 tests passed across backend, orchestrator and model-control suites using explicit offline test settings.
- Orchestrator suite: 18 passed.
- Model Control suite: 14 passed.
- Backend suite: 13 passed.
- Direct live Qdrant upsert/query was already verified during the debugging session against Qdrant 1.19.0 on port 6333, including collection creation, point upsert and query.
- Full live browser E2E with the user's Windows services was not reproducible inside this analysis environment; the final package therefore does not claim that external-service execution was performed here.

## Important setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r services\requirements.txt
```

Configure `.env` from `services\.env.example`.

Start PostgreSQL, Qdrant and Ollama.

Then:

```powershell
python -m uvicorn services.backend.app.main:app --reload --port 8000
```

Frontend:

```powershell
cd services\frontend
npm install
npm run dev
```

## Local auth

The backend currently expects:

```text
X-User-Email: <logged-in-user-email>
```

for protected API routes. The frontend client injects this header centrally from its local auth store.

Do NOT treat this header as production authentication.

## Expected model registry

With the supplied three Ollama models and healthy Ollama service, the Model Registry should show:

- `ollama-qwen3:4b` with reasoning/summarize_text/coding
- `ollama-gemma3:4b` with vision/ocr/document_analysis
- `demo-fallback` as a fallback slot

`nomic-embed-text:latest` should not appear as a generation model.

