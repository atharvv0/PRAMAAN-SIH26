from __future__ import annotations

import os
from functools import lru_cache

from services.knowledge.rag.retriever import Retriever, build_in_memory_retriever
from services.knowledge.rag.store import VectorStore


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    if os.environ.get("USE_QDRANT_SERVER", "1") == "0":
        return build_in_memory_retriever()
    host=os.environ.get("QDRANT_HOST","localhost")
    port=int(os.environ.get("QDRANT_PORT","6333"))
    try:
        from qdrant_client import QdrantClient
        return Retriever(VectorStore(QdrantClient(url=f"http://{host}:{port}")))
    except Exception:
        return build_in_memory_retriever()
