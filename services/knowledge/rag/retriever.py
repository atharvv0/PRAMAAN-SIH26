"""
Retriever — high-level ingest/retrieve API on top of VectorStore. This is what
the rest of the system (the knowledge.search tool, eventually ingestion scripts)
should import — not VectorStore directly.
"""
from __future__ import annotations

from pathlib import Path

from qdrant_client import QdrantClient

from services.knowledge.rag.chunker import chunk_text
from services.knowledge.rag.store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore):
        self._store = store

    def ingest_file(self, path: str) -> int:
        text = Path(path).read_text(encoding="utf-8")
        chunks = chunk_text(text)
        return self._store.add_chunks(chunks, source=path)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Returns results shaped for direct use as EvidenceRecord entries
        (docs/agent-contract.md) — claim/source/page_or_region/confidence."""
        hits = self._store.search(query, top_k=top_k)
        return [
            {
                "claim": hit["text"],
                "source": hit["source"],
                "page_or_region": f"chunk_{hit['chunk_index']}",
                "confidence": hit["score"],
                "validation_state": "unverified",
            }
            for hit in hits
        ]


def build_in_memory_retriever() -> Retriever:
    """Convenience for tests/demos: an ephemeral in-memory Qdrant instance, no
    server required. Production should construct a Retriever with a VectorStore
    pointed at the real `qdrant` service instead — see store.py docstring."""
    client = QdrantClient(":memory:")
    return Retriever(VectorStore(client))
