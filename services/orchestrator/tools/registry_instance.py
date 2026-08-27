"""
The shared ToolRegistry instance backend/app wires up at startup.

Registers both the demo-only tools (tools/examples.py — proven, always-available
fallbacks) and the real tools from services/knowledge (RAG search, OCR). Backend
should only ever import `default_registry` from this module — never construct its
own ToolRegistry.

Real tool status:
  - knowledge.search: REAL and working, fully offline (see
    services/knowledge/rag/ — HashingVectorizer + in-memory Qdrant). Pre-seeded
    below with the demo sample file as a stand-in "SOP" so it has something to
    retrieve. Swap the in-memory Qdrant client for the real `qdrant` service
    (docker-compose.yml) in production — see services/knowledge/rag/store.py.
  - ocr.process: REAL PaddleOCR integration, but model weights could not be
    downloaded in the environment this was built in — see
    services/knowledge/ocr_vlm/paddle_adapter.py for exact status and how to
    verify on real hardware. Registered here so it's available once verified;
    the planner (planner.py) still defaults to ocr.process_naive until then.
"""
from __future__ import annotations

from pathlib import Path

from qdrant_client import QdrantClient

from services.knowledge.ocr_vlm.ocr_tool import OcrProcessTool
from services.knowledge.rag.retriever import Retriever
from services.knowledge.rag.store import VectorStore
from services.knowledge.rag.tool import KnowledgeSearchTool
from services.orchestrator.tools.base import ToolRegistry
from services.orchestrator.tools.examples import (
    NetworkFetchDemoTool,
    OcrProcessNaiveTool,
    ReadFileTool,
    SummarizeTextTool,
)

default_registry = ToolRegistry()
default_registry.register(ReadFileTool())
default_registry.register(SummarizeTextTool())
default_registry.register(OcrProcessNaiveTool())
default_registry.register(NetworkFetchDemoTool())
default_registry.register(OcrProcessTool())

# knowledge.search — pre-seed with the demo sample file as a stand-in SOP so
# there's something real to retrieve out of the box. Real ingestion of actual
# SOPs/manuals replaces this once services/knowledge/ingestion exists.
_demo_retriever = Retriever(VectorStore(QdrantClient(":memory:")))
_demo_sample_path = Path(__file__).resolve().parents[3] / "data" / "samples" / "demo" / "sample_note.txt"
if _demo_sample_path.exists():
    _demo_retriever.ingest_file(str(_demo_sample_path))
default_registry.register(KnowledgeSearchTool(_demo_retriever))
