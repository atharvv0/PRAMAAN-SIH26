"""
Text embeddings — HashingVectorizer (scikit-learn), fully offline, no model
download required. This is a REAL, working embedding method, not a fake
placeholder — it's just simpler than a transformer embedding model (no semantic
understanding, just hashed n-gram frequency). It was chosen deliberately for the
network-independent build (per the project lead's own framing: "network
independent except for installing/downloading dependencies").

Swap for a real transformer embedding model (e.g. sentence-transformers) later on
a machine with internet access if retrieval quality needs to improve — keep the
`embed_texts` signature stable so callers (rag/store.py) don't need to change.
"""
from __future__ import annotations

from sklearn.feature_extraction.text import HashingVectorizer

EMBEDDING_DIM = 256

_vectorizer = HashingVectorizer(n_features=EMBEDDING_DIM, alternate_sign=False, norm="l2")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Returns one L2-normalized dense vector per input text, length EMBEDDING_DIM."""
    matrix = _vectorizer.transform(texts)
    return matrix.toarray().tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
