"""
OllamaVlmAdapter — real ModelAdapter (docs/agent-contract.md) for vision/P&ID
understanding via a local Ollama vision model (e.g. llava, moondream, or a
Qwen-VL-class model once available through Ollama — per docs/architecture.md
Model Strategy: "Vision/P&ID: use a VLM appropriate for drawing and image
reasoning").

STATUS: code only, UNTESTED. This sandbox has no Ollama server running and no
network route to one — I could not verify this against a real model. **You must
test this on your own machine** with Ollama installed and a vision model pulled
(e.g. `ollama pull llava`) before relying on it for the demo:

    from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter
    adapter = OllamaVlmAdapter(model="llava")
    print(adapter.health_check())
    print(adapter.invoke("/path/to/a/pid_drawing.png", prompt="Describe this P&ID"))

Talks to Ollama's HTTP API (default http://localhost:11434) — set
OLLAMA_HOST in .env if it runs elsewhere. Raises ModelUnavailableError on any
connection/inference failure, same pattern as PaddleOcrAdapter.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

from services.orchestrator.errors import ModelUnavailableError

DEFAULT_OLLAMA_HOST = "http://localhost:11434"


class OllamaVlmAdapter:
    capabilities = ["vision", "document_analysis"]

    def __init__(self, model: str = "llava", host: str | None = None):
        self.id = f"ollama_vlm:{model}"
        self._model = model
        self._host = host or os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST)

    def invoke(self, image_path: str, prompt: str = "Describe this image in detail.") -> dict:
        try:
            import httpx

            image_b64 = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
            response = httpx.post(
                f"{self._host}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "images": [image_b64],
                    "stream": False,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # noqa: BLE001 — any failure -> typed, retryable error
            raise ModelUnavailableError(
                f"Ollama VLM ({self._model}) could not process '{image_path}': {exc}",
                detail=repr(exc),
            ) from exc

        description = data.get("response", "")
        return {
            "content": description,
            "path": image_path,
            "evidence": [
                {
                    "claim": description,
                    "source": image_path,
                    "page_or_region": None,
                    "model": self.id,
                    "confidence": None,
                    "validation_state": "unverified",
                }
            ],
        }

    def health_check(self) -> bool:
        try:
            import httpx

            resp = httpx.get(f"{self._host}/api/tags", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    def metadata(self) -> dict:
        return {"id": self.id, "capabilities": self.capabilities, "host": self._host}
