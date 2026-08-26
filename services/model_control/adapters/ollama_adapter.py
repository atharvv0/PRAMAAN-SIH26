"""
OllamaAdapter — real ModelAdapter implementation for the Ollama dev runtime
(see .env.example MODEL_RUNTIME=ollama, MODEL_RUNTIME_HOST, MODEL_RUNTIME_PORT).

This talks to a real Ollama server over HTTP (`/api/generate`, `/api/tags`). It is
not a mock: given a reachable Ollama instance with the named model pulled, invoke()
returns a real completion. If no Ollama server is reachable (e.g. this sandbox, or
a fresh dev machine before models are pulled), health_check() returns False and the
router (services/model_control/router) falls back to another registered adapter —
see registry_instance.py's DemoModelAdapter fallback.

vLLM production adapter: same interface, different HTTP client — add
`vllm_adapter.py` alongside this one when the production runtime is benchmarked
(services/model_control/benchmarks); do not extend this file to branch on runtime.
"""
from __future__ import annotations

import time

import httpx

from services.model_control.adapters.base import ModelAdapter, ModelResponse

DEFAULT_TIMEOUT_SECONDS = 30.0
HEALTH_CHECK_TIMEOUT_SECONDS = 2.0


class OllamaAdapter(ModelAdapter):
    def __init__(
        self,
        id: str,  # noqa: A002 — matches ModelAdapter.id naming
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
        try:
            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    **{k: v for k, v in kwargs.items() if k in ("options", "system", "format")},
                },
                timeout=self.timeout_seconds,
            )
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ModelInvocationError(
                f"Ollama invocation failed for model '{self.model_name}': {exc}",
                detail=repr(exc),
            ) from exc

        latency_ms = int((time.monotonic() - started) * 1000)
        return ModelResponse(
            model_id=self.id,
            text=data.get("response", ""),
            latency_ms=latency_ms,
            raw=data,
        )

    def health_check(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=HEALTH_CHECK_TIMEOUT_SECONDS)
            if resp.status_code != 200:
                return False
            tags = resp.json().get("models", [])
            return any(self.model_name in (m.get("name") or "") for m in tags) or bool(tags)
        except (httpx.HTTPError, ValueError):
            return False

    def metadata(self) -> dict:
        return {
            **super().metadata(),
            "runtime": "ollama",
            "model_name": self.model_name,
            "base_url": self.base_url,
        }
