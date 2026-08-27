# services/knowledge — Document Intelligence, OCR/VLM, RAG, Spreadsheet Engine

**Owner:** per `docs/team-structure.md` this is Role 5 (Multimodal/ML) — note as of
this pass, the project lead has said they intend to implement this module
personally (RAG, OCR/VLM, multimodal pipeline) rather than leaving it to Role 5.
Confirm actual ownership with the team before assuming either way; this README's
contract and Definition of Done hold regardless of who implements it.

The placeholder tool `ocr.process_naive` in `services/orchestrator/tools/examples.py`
stands in for this module's real OCR/VLM pipeline until it lands — see that file's
docstring for the exact output shape (`content` + `evidence[]`) a real
implementation needs to match so existing plans don't break.

## What belongs here

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

- [ ] Scanned report + P&ID processed with page/region provenance preserved
- [ ] Local SOP query returns correct citations
- [ ] Spreadsheet values are recomputed deterministically, not LLM-estimated
