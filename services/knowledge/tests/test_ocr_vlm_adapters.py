"""
Tests for OCR/VLM adapter error-handling contracts.

These tests are deterministic and do not depend on whether PaddleOCR model
weights happen to be cached on the developer machine.

The production adapters must:
- wrap underlying OCR/model failures as ModelUnavailableError
- report health accurately based on actual initialization/reachability
"""

from unittest.mock import patch

import pytest

from services.orchestrator.errors import ModelUnavailableError


def test_paddle_ocr_adapter_raises_model_unavailable_on_failure():
    from services.knowledge.ocr_vlm.paddle_adapter import PaddleOcrAdapter

    adapter = PaddleOcrAdapter()

    with patch(
        "services.knowledge.ocr_vlm.paddle_adapter._get_ocr",
        side_effect=RuntimeError("PaddleOCR model unavailable"),
    ):
        with pytest.raises(ModelUnavailableError):
            adapter.invoke("data/samples/demo/sample_note.txt")


def test_paddle_ocr_adapter_health_check_reports_false_when_unavailable():
    from services.knowledge.ocr_vlm.paddle_adapter import PaddleOcrAdapter

    adapter = PaddleOcrAdapter()

    with patch(
        "services.knowledge.ocr_vlm.paddle_adapter._get_ocr",
        side_effect=RuntimeError("PaddleOCR model unavailable"),
    ):
        assert adapter.health_check() is False


def test_ollama_vlm_adapter_raises_model_unavailable_when_no_server_reachable():
    from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter

    adapter = OllamaVlmAdapter(
        model="llava",
        host="http://localhost:11434",
    )

    with pytest.raises(ModelUnavailableError):
        adapter.invoke("data/samples/demo/sample_note.txt")


def test_ollama_vlm_adapter_health_check_reports_false_when_unreachable():
    from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter

    adapter = OllamaVlmAdapter(
        model="llava",
        host="http://localhost:11434",
    )

    assert adapter.health_check() is False