from __future__ import annotations

from uuid import uuid4
from typing import Any

from services.knowledge.rag.embeddings import embed_text, embed_texts, embedding_dimension

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams
except ImportError:  # optional for true local in-memory development
    QdrantClient = Any  # type: ignore[misc,assignment]
    Distance = FieldCondition = Filter = MatchValue = PointStruct = VectorParams = None  # type: ignore[assignment]


class VectorStore:
    def __init__(self, client: QdrantClient, collection: str = "pramaan_knowledge"):
        self._client = client
        self._collection = collection
        self._collection_ready = False

    def _ensure_collection(self, size: int | None = None) -> None:
        if self._collection_ready:
            return
        try:
            exists = self._client.collection_exists(self._collection)
        except AttributeError:
            exists = self._collection in [c.name for c in self._client.get_collections().collections]
        if not exists:
            dim = size or embedding_dimension()
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
        self._collection_ready = True

    def add_chunks(self, chunks: list[str], source: str, metadata: dict | None = None) -> list[str]:
        if not chunks:
            return []
        vectors = embed_texts(chunks)
        self._ensure_collection(len(vectors[0]))
        ids=[]
        points=[]
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point_id=str(uuid4())
            ids.append(point_id)
            payload={"text":chunk,"source":source,"chunk_index":i, **(metadata or {})}
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))
        self._client.upsert(collection_name=self._collection, points=points)
        return ids

    def search(self, query: str, top_k: int = 3, metadata_filter: dict | None = None) -> list[dict]:
        # Embed the query once and reuse it for both collection sizing and
        # the actual search -- this used to call embed_text(query) twice per
        # search (doubling embedding latency/cost, and doubling network
        # calls when using the real Ollama embedding provider), even though
        # _ensure_collection's size argument is only ever used the first
        # time a collection is created.
        query_vector = embed_text(query)
        self._ensure_collection(len(query_vector))
        query_filter = None
        if metadata_filter:
            query_filter = Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in metadata_filter.items() if v is not None])
        response = self._client.query_points(collection_name=self._collection, query=query_vector, limit=top_k, query_filter=query_filter)
        return [{"text":p.payload["text"],"source":p.payload["source"],"chunk_index":p.payload.get("chunk_index",0),"score":p.score,"point_id":str(p.id)} for p in response.points]


class MemoryVectorStore:
    """Tiny deterministic cosine-search store for local/offline development without Qdrant."""
    def __init__(self):
        self._items: list[dict] = []

    def add_chunks(self, chunks: list[str], source: str, metadata: dict | None = None) -> list[str]:
        if not chunks:
            return []
        vectors = embed_texts(chunks)
        ids=[]
        for i,(chunk,vector) in enumerate(zip(chunks,vectors)):
            point_id=str(uuid4()); ids.append(point_id)
            self._items.append({"id":point_id,"text":chunk,"source":source,"chunk_index":i,"vector":vector,**(metadata or {})})
        return ids

    def search(self, query: str, top_k: int = 3, metadata_filter: dict | None = None) -> list[dict]:
        import math
        q=embed_text(query)
        def dot(a,b): return sum(x*y for x,y in zip(a,b))
        scored=[]
        qnorm=math.sqrt(dot(q,q)) or 1.0
        for item in self._items:
            if metadata_filter and any(item.get(k) != v for k, v in metadata_filter.items() if v is not None):
                continue
            v=item["vector"]; vnorm=math.sqrt(dot(v,v)) or 1.0
            score=dot(q,v)/(qnorm*vnorm)
            scored.append((score,item))
        scored.sort(key=lambda x:x[0], reverse=True)
        return [{"text":it["text"],"source":it["source"],"chunk_index":it.get("chunk_index",0),"score":score,"point_id":it["id"]} for score,it in scored[:top_k]]
