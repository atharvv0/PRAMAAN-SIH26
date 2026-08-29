"""Local embedding providers.

Production uses the configured Ollama embedding model through the local HTTP API.
A hashing fallback is retained for unit tests/offline development only.
"""
from __future__ import annotations

import os
from typing import Protocol

import httpx
from sklearn.feature_extraction.text import HashingVectorizer


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    def embed_text(self, text: str) -> list[float]: ...


class OllamaEmbeddingProvider:
    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or os.environ.get("EMBEDDING_MODEL_NAME", "nomic-embed-text")
        self.host = (host or os.environ.get("MODEL_RUNTIME_HOST", "localhost"))
        self.port = int(os.environ.get("MODEL_RUNTIME_PORT", "11434"))
        self.base_url = f"http://{self.host}:{self.port}"

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = httpx.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": texts},
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise RuntimeError("Ollama embedding response has an invalid shape")
        return embeddings

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


# Deterministic local fallback for tests only.
_HASH_DIM = 256
_vectorizer = HashingVectorizer(n_features=_HASH_DIM, alternate_sign=False, norm="l2")


def _use_hashing() -> bool:
    return os.environ.get("USE_OLLAMA_EMBEDDINGS", "1").strip() == "0"


def embed_texts(texts: list[str]) -> list[list[float]]:
    if _use_hashing():
        return _vectorizer.transform(texts).toarray().tolist()
    return OllamaEmbeddingProvider().embed_texts(texts)


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]


def embedding_dimension() -> int:
    if _use_hashing():
        return _HASH_DIM
    return len(embed_text("dimension probe"))
