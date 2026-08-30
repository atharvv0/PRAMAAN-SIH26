"""
KnowledgeSearchTool — real ToolAdapter (docs/agent-contract.md) wrapping
services/knowledge's Retriever. id: knowledge.search (matches the tool id family
in docs/architecture.md). This is a REAL tool, not a demo placeholder — unlike
services/orchestrator/tools/examples.py's tools, this one does genuine offline
retrieval (see rag/embeddings.py for why HashingVectorizer, not a downloaded model).

Note this tool needs a Retriever instance at construction time (it owns
in-process ingested state via VectorStore) — see
services/orchestrator/tools/registry_instance.py for how it's wired in and
pre-seeded with a demo SOP document so it has something to actually retrieve.
"""
from __future__ import annotations

from services.knowledge.rag.retriever import Retriever
from services.orchestrator.tools.base import ToolAdapter


class KnowledgeSearchTool(ToolAdapter):
    id = "knowledge.search"
    required_permissions = ["knowledge.read"]
    declares_network_access = False

    def __init__(self, retriever: Retriever):
        self._retriever = retriever

    def invoke(self, inputs: dict) -> dict:
        query = inputs.get("query")
        if not query:
            raise ValueError("KnowledgeSearchTool requires 'query' in inputs")
        top_k = inputs.get("top_k", 3)
        metadata_filter = {}
        if inputs.get("user_id"):
            metadata_filter["user_id"] = inputs["user_id"]
        if inputs.get("workspace_id"):
            metadata_filter["workspace_id"] = inputs["workspace_id"]
        evidence = self._retriever.retrieve(query, top_k=top_k, metadata_filter=metadata_filter or None)
        return {
            "query": query,
            "result_count": len(evidence),
            "evidence": evidence,
        }
