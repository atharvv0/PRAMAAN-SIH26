# Final Model Registry

The Model Registry is a read-only transparency surface for every authenticated PRAMAAN user. Reviewer/admin permissions remain required for governance actions elsewhere.

Expected local routing:
- qwen3:4b -> reasoning, summarize_text, coding
- gemma3:4b -> vision, OCR, document_analysis
- nomic-embed-text -> embedding/RAG only; not shown as a generation adapter
- demo-fallback -> last-resort deterministic fallback

The backend registry endpoint is /api/v1/models. The frontend route is /models and is intentionally not role-gated.
