from __future__ import annotations

import os
from pathlib import Path

from services.knowledge.rag.chunker import chunk_text
from services.knowledge.rag.store import MemoryVectorStore, VectorStore


class Retriever:
    def __init__(self, store: VectorStore):
        self._store = store

    def ingest_text(self, text: str, source: str, metadata: dict | None = None) -> int:
        chunks = chunk_text(text)
        self._store.add_chunks(chunks, source=source, metadata=metadata)
        return len(chunks)

    def ingest_file(self, path: str, metadata: dict | None = None) -> int:
        from services.knowledge.ingestion.document_extractor import extract_document
        extracted = extract_document(path)
        text = str(extracted.get("content") or "")
        if not text.strip():
            return 0
        return self.ingest_text(text, source=path, metadata=metadata)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        hits=self._store.search(query,top_k=top_k)
        return [{"claim":h["text"],"source":h["source"],"page_or_region":f"chunk_{h['chunk_index']}","confidence":float(h["score"]),"validation_state":"unverified","qdrant_point_id":h.get("point_id")} for h in hits]


def build_production_retriever() -> Retriever:
    host=os.environ.get("QDRANT_HOST","localhost")
    port=int(os.environ.get("QDRANT_PORT","6333"))
    from qdrant_client import QdrantClient
    return Retriever(VectorStore(QdrantClient(url=f"http://{host}:{port}")))


def build_in_memory_retriever() -> Retriever:
    return Retriever(MemoryVectorStore())
