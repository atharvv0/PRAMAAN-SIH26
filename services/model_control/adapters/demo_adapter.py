"""
DemoModelAdapter — deterministic, offline, always-healthy fallback.

Purpose: the router (services/model_control/router) must always have *something*
to select even on a machine with no Ollama/vLLM running yet, or fully air-gapped
before models are pulled — this is the DoD's "health-check + fallback model
behavior" (services/model_control/README.md). It performs no network calls and no
real inference; it is intentionally simple (extractive, not generative) so it is
never mistaken for a real model result — every ModelResponse it returns is tagged
`raw={"demo": True}` for exactly that reason.

Do not register this as the *only* adapter for a capability in production config —
it exists so the system degrades gracefully, not as a substitute for real models.
"""
from __future__ import annotations

from services.model_control.adapters.base import ModelAdapter, ModelResponse


class DemoModelAdapter(ModelAdapter):
    def __init__(self, id: str = "demo-fallback", capabilities: list[str] | None = None):  # noqa: A002
        self.id = id
        self.capabilities = capabilities or ["reasoning", "summarize_text", "coding", "ocr", "vision"]
        self.modalities = ["text"]

    def invoke(self, prompt: str, **kwargs) -> ModelResponse:
        sentences = [s.strip() for s in prompt.replace("\n", " ").split(".") if s.strip()]
        text = ". ".join(sentences[:3])
        if text and not text.endswith("."):
            text += "."
        if not text:
            text = "(demo adapter: no content to summarize)"
        return ModelResponse(model_id=self.id, text=text, latency_ms=0, raw={"demo": True})

    def health_check(self) -> bool:
        return True

    def metadata(self) -> dict:
        return {**super().metadata(), "runtime": "demo-offline"}
