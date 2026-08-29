"""Repo-wide pytest configuration.

Several PRAMAAN modules default to talking to real local services (Ollama for
generation/embeddings, Qdrant for vector search) so that *production* behaviour
never silently substitutes a fake result for a real one. That is correct for
production, but it means the test suite is not hermetic by default: running
`pytest` on a machine with no Ollama/Qdrant listening previously failed with
raw connection errors instead of exercising the code under test.

This conftest forces the documented offline fallbacks on for the whole test
session, unless a value has already been set explicitly (e.g. by a developer
who *wants* to run the suite against real local services as an integration
check):

  - USE_OLLAMA_EMBEDDINGS=0   -> services/knowledge/rag/embeddings.py uses the
                                  deterministic HashingVectorizer fallback.
  - USE_QDRANT_SERVER=0       -> services/knowledge/rag/runtime.py uses the
                                  in-memory MemoryVectorStore fallback.
  - AUTO_DISCOVER_OLLAMA_MODELS=0
                              -> services/model_control registry does not try
                                 to probe a local Ollama server at import
                                 time; the registry falls back to
                                 DemoModelAdapter for every capability, which
                                 is deterministic and always healthy.

These must be set as plain module-level statements (not inside a fixture) so
they land before any module-level singletons (default_registry, default
retriever, etc.) are constructed at import time.
"""
from __future__ import annotations

import os

os.environ.setdefault("USE_OLLAMA_EMBEDDINGS", "0")
os.environ.setdefault("USE_QDRANT_SERVER", "0")
os.environ.setdefault("AUTO_DISCOVER_OLLAMA_MODELS", "0")
