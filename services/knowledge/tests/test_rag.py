"""
Real, fully-offline tests for the RAG pipeline (embeddings -> Qdrant in-memory
store -> retrieval). No mocking of the vector search itself — this proves actual
similarity search works, not just that the code imports.
"""
from qdrant_client import QdrantClient

from services.knowledge.rag.chunker import chunk_text
from services.knowledge.rag.retriever import Retriever, build_in_memory_retriever
from services.knowledge.rag.store import VectorStore
from services.knowledge.rag.tool import KnowledgeSearchTool


def test_chunk_text_splits_on_paragraphs():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    chunks = chunk_text(text)
    assert chunks == ["First paragraph.", "Second paragraph.", "Third paragraph."]


def test_ingest_and_retrieve_relevant_chunk():
    retriever = build_in_memory_retriever()
    added = retriever._store.add_chunks(
        [
            "The corrosion inspection SOP requires readings every 90 days.",
            "The office coffee machine is on the third floor.",
            "Pipeline pressure must not exceed 150 psi under the safety SOP.",
        ],
        source="sop_demo.txt",
    )
    assert added == 3

    results = retriever.retrieve("what does the SOP say about pressure limits?", top_k=1)
    assert len(results) == 1
    assert "pressure" in results[0]["claim"].lower()
    assert results[0]["source"] == "sop_demo.txt"
    assert results[0]["validation_state"] == "unverified"


def test_ingest_file_reads_and_chunks_a_real_file():
    import os

    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "samples", "demo", "sample_note.txt"
    )
    sample_path = os.path.abspath(sample_path)

    retriever = build_in_memory_retriever()
    count = retriever.ingest_file(sample_path)
    assert count >= 1

    results = retriever.retrieve("corrosion inspection findings", top_k=1)
    assert len(results) == 1
    assert results[0]["source"] == sample_path


def test_knowledge_search_tool_returns_evidence_shaped_results():
    client = QdrantClient(":memory:")
    store = VectorStore(client, collection="tool_test")
    store.add_chunks(["Maintenance is recommended within 90 days."], source="sop_demo.txt")
    tool = KnowledgeSearchTool(Retriever(store))

    result = tool.invoke({"query": "when should maintenance happen?"})
    assert result["result_count"] == 1
    assert "evidence" in result
    assert result["evidence"][0]["source"] == "sop_demo.txt"


def test_knowledge_search_tool_requires_query():
    import pytest

    client = QdrantClient(":memory:")
    tool = KnowledgeSearchTool(Retriever(VectorStore(client, collection="tool_test_2")))
    with pytest.raises(ValueError):
        tool.invoke({})
