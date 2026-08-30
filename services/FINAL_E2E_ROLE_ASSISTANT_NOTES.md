# PRAMAAN final E2E role/assistant layer

## User roles
- Operator: create and run own work; view own history, evidence and deliverables.
- Reviewer: review tasks/evidence across operators and make approval decisions.
- Admin: all reviewer privileges plus audit and user/role administration.

Backend role is authoritative in PostgreSQL (`users.role`). New users are provisioned as operators. Optional local bootstrap promotion uses `PRAMAAN_ADMIN_EMAILS` and `PRAMAAN_REVIEWER_EMAILS`.

## Local AI Assistant
`POST /api/v1/assistant/chat` uses the Model Control reasoning capability. It is local/Ollama-only, can optionally receive task context, and strips hidden `<think>` / `<analysis>` blocks before returning the final response.

## Model roles
- `qwen3:4b`: reasoning, summarization, coding
- `gemma3:4b`: OCR, vision, document analysis
- `nomic-embed-text`: embeddings only
- `demo-fallback`: emergency/offline fallback

## Document/vision coverage
- PDF: text extraction and scanned-page VLM/OCR
- PPTX: slide text plus embedded-image VLM/OCR
- DOCX: paragraph/table extraction
- XLSX/XLSM: sheet/row extraction
- CSV/JSON/TXT/Markdown: native text extraction
- Common image formats: VLM/OCR

Legacy `.doc`/`.ppt`, encrypted files, CAD, audio/video and unsupported proprietary formats should be explicitly rejected rather than silently mis-processed.
