# PRAMAAN — Final E2E Hardening Report

## Scope
This revision targets the latest services baseline and specifically hardens the runtime areas that were still incomplete during manual testing: final responses, artifacts/deliverables, authenticated downloads, evidence capture, user-scoped RAG retrieval, and image/scanned/PPTX OCR/VLM processing.

## Key fixes
- Added `artifact.write` as a real orchestrator tool and added it to the production tool registry.
- File-backed plans now append artifact generation when the user explicitly asks for a file/export/download, and analysis/review tasks are guaranteed a knowledge-search + reasoning stage.
- Summarization receives the original task intent so constraints such as "10 lines" are visible to the summarization model.
- Artifact writing supports TXT/Markdown/JSON/CSV/DOCX/PDF/PPTX/XLSX when the corresponding Python packages are installed.
- Generated artifacts are persisted as `FileRecord` + `Deliverable` records and are exposed through the existing deliverables API.
- Browser downloads now use an authenticated blob fetch so `X-User-Email` authorization is preserved; direct HTML anchors could not supply that custom header.
- Deliverables support multiple files per task rather than replacing the prior deliverable row for every new artifact.
- Read/extraction now supports PDF, DOCX, PPTX, XLSX/XLSM, CSV/TSV, JSON, TXT/Markdown/XML/HTML and emits a provenance evidence item.
- Image/PDF/PPTX processing routes through Gemma VLM/OCR; scanned PDFs are processed page-by-page when native extraction is effectively empty.
- OCR PDF page limit defaults to all pages (`max_pages <= 0`), while an explicit `max_pages` can cap processing.
- Qdrant retrieval can be filtered by `user_id` and `workspace_id`, preventing cross-user knowledge leakage from shared collections.
- Final reasoning/model text strips common `<think>` and `<analysis>` blocks defensively.
- The final run screen shows the final user-facing response and generated deliverables; thinking traces are not surfaced as the final answer.

## Current model roles
- `qwen3:4b`: reasoning, summarization, coding
- `gemma3:4b`: vision, OCR, document analysis
- `nomic-embed-text`: embeddings/RAG only
- `demo-fallback`: last-resort local fallback

## Important validation note
Python source compilation succeeds for the patched services. Full integration testing against the user's local Windows PostgreSQL/Qdrant/Ollama stack cannot be reproduced in this execution environment. The existing test suite in this environment also requires project dependencies that are not installed here. Do not treat that as a claim of successful live browser E2E verification.

## Expected simple task
"Summarize this document in 10 lines and give me a .txt file" should produce:
1. document extraction
2. model-backed summarization with the 10-line constraint
3. final response
4. `pramaan_output.txt`
5. a persisted Deliverable row
6. a downloadable file from the Deliverables page

## Expected visual task
Image/scanned PDF/PPTX should route through Gemma VLM/OCR, populate evidence, feed the reasoning model, and surface source/model/tool provenance.
