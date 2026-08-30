# PRAMAAN — Final E2E Integration Notes

This package adds the final runtime pieces needed for a user-facing document task workflow.

## User-visible behavior

- Ollama `think` output is never surfaced as the answer. The model adapters request `think=false` and strip common `<think>` / `Thinking:` wrappers defensively.
- Run pages display only the final user-facing response.
- Generated artifacts appear in the run view and Deliverables page.
- Downloads use the authenticated API client so the protected file endpoint works with local auth.
- Evidence is shown on the run page when the task produces evidence, with source, page, confidence, and validation status.

## Output artifacts

When an intent asks for a file/deliverable or a concrete format, the backend creates and registers an artifact. Supported output formats are TXT, DOCX, PDF, PPTX, XLSX, CSV, and JSON. An explicit request such as `in 10 lines` is honored deterministically without fabricating content.

## Input/document coverage

The document reader supports PDF, DOCX, PPTX, XLSX/XLSM-family spreadsheets, CSV, JSON, TXT/Markdown and common image formats. Images are routed to the local Gemma VLM OCR path. Text PDFs are extracted directly; scanned PDFs fall back to VLM OCR page-by-page. PPTX text is extracted slide-by-slide and embedded slide images are sent through OCR/VLM.

This is not a guarantee for arbitrary binary formats (for example legacy `.ppt`, proprietary CAD formats, audio/video, or encrypted/password-protected documents). Unsupported binary formats return an explicit error rather than pretending to have analyzed them.

## Evidence behavior

Evidence is expected for inspection/assessment/safety/compliance/recommendation-style file tasks. The planner enforces a `knowledge.search` step for these task classes even if a model-backed planner forgets it. Simple summarization can complete without evidence records when no retrieval/claim validation is required.

## Important deployment note

Persistent Qdrant storage should be mounted to a host volume for production. The current local Qdrant container can work without a volume, but vectors may be lost when the container is recreated.

## Validation performed in this environment

- Python source compilation: PASS.
- Static artifact writer behavior for `.txt` and exact line-count requests: PASS.
- Existing pytest suite was not a clean green run in this sandbox because the package test environment does not include every runtime dependency/fixture used by the repo (notably `qdrant-client` in the sandbox Python environment) and several older tests still encode pre-auth/pre-evidence expectations. The runtime changes themselves were compiled successfully.
