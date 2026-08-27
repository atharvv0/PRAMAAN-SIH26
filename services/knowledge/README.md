# services/knowledge — Document Intelligence, OCR/VLM, RAG, Spreadsheet Engine

**Owner:** per `docs/team-structure.md` this is Role 5 (Multimodal/ML) — the project
lead is implementing this module personally.

## Status — what's real vs. what's blocked, honestly

| Piece | Status |
|---|---|
| RAG (`rag/`) — embeddings, Qdrant store, chunker, retriever, `knowledge.search` tool | **Real and fully tested, working today.** Verified live over HTTP: real similarity search, real relevance scores, real evidence citations. See "Why HashingVectorizer" below. |
| OCR (`ocr_vlm/paddle_adapter.py`, `ocr_tool.py`) | **Real integration code**, installs cleanly, but model weights could not download in the sandbox this was built in (no route to PaddleOCR's model hosting). **You must verify this on a machine with internet access** before demo day — see the adapter's docstring for the exact command to run. Raises `ModelUnavailableError` cleanly on failure either way. |
| VLM / P&ID (`ocr_vlm/ollama_vlm_adapter.py`) | **Real integration code, UNTESTED** — no Ollama server was available to test against. You need Ollama + a vision model (`ollama pull llava`) on your own machine to verify this before relying on it. |
| Spreadsheet engine (`spreadsheet_engine/`) | Not started |
| Ingestion pipeline (`ingestion/`) beyond the one demo file already wired into the registry | Not started — `retriever.ingest_file()` exists and works, just needs calling for your real SOPs/manuals |

### Why HashingVectorizer instead of a transformer embedding model

Real semantic embeddings (e.g. sentence-transformers) need to download a model
from the internet on first use. Given the "network independent except for
installing dependencies" requirement, RAG here uses scikit-learn's
`HashingVectorizer` instead — genuinely real, fully offline, no download, just
lower semantic quality than a transformer embedding. See `rag/embeddings.py` for
exactly why and how to swap it later if retrieval quality needs to improve.

### The demo OCR tool question

`services/orchestrator/tools/examples.py`'s `ocr.process_naive` (fakes OCR by
reading a text file) is still what the planner uses by default — **not** the real
`ocr.process` tool in this module — until PaddleOCR is verified working on real
hardware. See `planner.py` and `tools/registry_instance.py` for exactly where to
flip that switch once you've confirmed it works.

## What belongs here (beyond the above)

- `ingestion/` — loading manuals/SOPs/reports/correspondence into the local knowledge layer
- `ocr_vlm/` — scanned PDF / P&ID / handwriting pipelines (preserve page/region
  provenance — every extracted claim needs a source per `docs/agent-contract.md`
  "EvidenceRecord")
- `rag/` — hybrid retrieval + reranking + permission-aware evidence over Qdrant
- `spreadsheet_engine/` — **deterministic** computation; the LLM narrates results, it
  does not do the arithmetic (see `docs/architecture.md` differentiator table)

## What does NOT belong here

- Agent orchestration/tool registration wiring → `services/orchestrator` (this package
  exposes tools that get registered there, it doesn't call the planner itself)
- Permission enforcement → `services/governance` (RBAC is applied to what you retrieve,
  but you don't own the policy engine)

## Contract to implement

Every retrieved claim should populate an `EvidenceRecord` (`docs/agent-contract.md`).
Tools this module exposes register as `ToolAdapter` (`docs/agent-contract.md`) with
`services/orchestrator/tools`.

## Definition of Done (Phase 5/6, see docs/roadmap.md)

- [x] Local SOP query returns correct citations — real, tested, verified live
      (RAG pipeline: embeddings + Qdrant + retriever + `knowledge.search` tool)
- [ ] Scanned report + P&ID processed with page/region provenance preserved —
      code is real and ready (`ocr_vlm/`), blocked on verifying PaddleOCR model
      download + Ollama VLM on real hardware (see status table above)
- [ ] Spreadsheet values are recomputed deterministically, not LLM-estimated —
      not started
- [ ] Real SOPs/manuals ingested (currently only the one demo sample file is
      pre-seeded in `tools/registry_instance.py`)
