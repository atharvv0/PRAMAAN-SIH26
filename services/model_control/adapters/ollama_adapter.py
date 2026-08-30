"""
OllamaAdapter — real ModelAdapter implementation for the local Ollama runtime.

Supports:
- text generation via /api/generate
- image inputs for multimodal Ollama models via the `images` argument
- model liveness checks via /api/tags

The adapter is deliberately runtime-agnostic to callers: Orchestrator and Router
depend only on ModelAdapter.
"""
from __future__ import annotations

import time
from typing import Any

import httpx

from services.model_control.adapters.base import ModelAdapter, ModelResponse

DEFAULT_TIMEOUT_SECONDS = 120.0
HEALTH_CHECK_TIMEOUT_SECONDS = 2.0


class OllamaAdapter(ModelAdapter):
    def __init__(
        self,
        id: str,  # noqa: A002
        model_name: str,
        capabilities: list[str],
        host: str = "localhost",
        port: int = 11434,
        modalities: list[str] | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.id = id
        self.model_name = model_name
        self.capabilities = capabilities
        self.modalities = modalities or ["text"]
        self.base_url = f"http://{host}:{port}"
        self.timeout_seconds = timeout_seconds

    def invoke(self, prompt: str, **kwargs) -> ModelResponse:
        from services.model_control.errors import ModelInvocationError

        started = time.monotonic()

        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }

        # Supported Ollama generation controls.
        for key in ("options", "system", "format", "think"):
            if key in kwargs:
                payload[key] = kwargs[key]

        # Ollama multimodal generation accepts base64-encoded images.
        # Accept either a single string or a list of strings.
        if "images" in kwargs and kwargs["images"] is not None:
            images = kwargs["images"]
            if isinstance(images, str):
                images = [images]
            payload["images"] = images

        try:
            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout_seconds,
            )
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ModelInvocationError(
                f"Ollama invocation failed for model "
                f"'{self.model_name}': {exc}",
                detail=repr(exc),
            ) from exc

        latency_ms = int((time.monotonic() - started) * 1000)

        return ModelResponse(
            model_id=self.id,
            text=data.get("response", ""),
            latency_ms=latency_ms,
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
            raw=data,
        )

    def health_check(self) -> bool:
        try:
            resp = httpx.get(
                f"{self.base_url}/api/tags",
                timeout=HEALTH_CHECK_TIMEOUT_SECONDS,
            )

            if resp.status_code != 200:
                return False

            tags = resp.json().get("models", [])

            return any(
                (model.get("name") or "") == self.model_name
                for model in tags
            )
        except (httpx.HTTPError, ValueError, TypeError):
            return False

    def metadata(self) -> dict:
        return {
            **super().metadata(),
            "runtime": "ollama",
            "model_name": self.model_name,
            "base_url": self.base_url,
            "allow_restricted": self.base_url.startswith(
                ("http://127.0.0.1", "http://localhost")
            ),
        }
