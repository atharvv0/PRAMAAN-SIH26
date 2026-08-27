"""
Tests for the OCR/VLM adapters' error-handling contract. These do NOT test real
model inference (PaddleOCR needs internet access to download weights; the Ollama
VLM adapter needs a running Ollama server — neither is available in this sandbox,
see each adapter's module docstring). What IS tested: both adapters correctly
raise ModelUnavailableError instead of crashing when the underlying model/service
is unreachable — the real behaviour every caller depends on.
"""
import pytest

from services.orchestrator.errors import ModelUnavailableError


def test_paddle_ocr_adapter_raises_model_unavailable_on_failure():
    from services.knowledge.ocr_vlm.paddle_adapter import PaddleOcrAdapter

    adapter = PaddleOcrAdapter()
    # In this sandbox PaddleOCR cannot download its model weights (no network
    # route to the model hosting platform) — this is the real, current failure
    # mode, not a simulated one. On a machine with internet access this call
    # would instead need a real image path and would succeed.
    with pytest.raises(ModelUnavailableError):
        adapter.invoke("data/samples/demo/sample_note.txt")


def test_paddle_ocr_adapter_health_check_reports_false_when_unavailable():
    from services.knowledge.ocr_vlm.paddle_adapter import PaddleOcrAdapter

    adapter = PaddleOcrAdapter()
    assert adapter.health_check() is False


def test_ollama_vlm_adapter_raises_model_unavailable_when_no_server_reachable():
    from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter

    adapter = OllamaVlmAdapter(model="llava", host="http://localhost:11434")
    # No Ollama server is running in this sandbox — real connection failure,
    # correctly wrapped rather than propagated as a raw httpx exception.
    with pytest.raises(ModelUnavailableError):
        adapter.invoke("data/samples/demo/sample_note.txt")


def test_ollama_vlm_adapter_health_check_reports_false_when_unreachable():
    from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter

    adapter = OllamaVlmAdapter(model="llava", host="http://localhost:11434")
    assert adapter.health_check() is False
