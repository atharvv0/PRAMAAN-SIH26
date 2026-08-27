"""
VectorStore — thin wrapper around qdrant-client for ingest + similarity search.

Real and testable fully offline via QdrantClient(":memory:") — see
services/knowledge/tests/test_rag.py. Production points this at the real `qdrant`
service (docker-compose.yml) using services.backend.app.core.config.settings
(qdrant_host/qdrant_port) instead of ":memory:" — pass a real QdrantClient in via
the `client` constructor argument, don't hard-code the connection here.
"""
from __future__ import annotations

from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from services.knowledge.rag.embeddings import EMBEDDING_DIM, embed_text, embed_texts


class VectorStore:
    def __init__(self, client: QdrantClient, collection: str = "pramaan_knowledge"):
        self._client = client
        self._collection = collection
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        existing = [c.name for c in self._client.get_collections().collections]
        if self._collection not in existing:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )

    def add_chunks(self, chunks: list[str], source: str) -> int:
        """Embeds and stores `chunks`, tagging each with `source` (e.g. a file path
        or SOP id) and its index within that source for page/region-style
        provenance. Returns the number of chunks stored."""
        if not chunks:
            return 0
        vectors = embed_texts(chunks)
        points = [
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={"text": chunk, "source": source, "chunk_index": i},
            )
            for i, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        self._client.upsert(collection_name=self._collection, points=points)
        return len(points)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        query_vector = embed_text(query)
        response = self._client.query_points(
            collection_name=self._collection, query=query_vector, limit=top_k
        )
        return [
            {
                "text": point.payload["text"],
                "source": point.payload["source"],
                "chunk_index": point.payload["chunk_index"],
                "score": point.score,
            }
            for point in response.points
        ]
