"""
ModelAdapter — see docs/agent-contract.md "ModelAdapter".

Every runtime (Ollama, vLLM, ...) gets exactly one adapter implementation here.
The router (services/model_control/router) and callers (services/orchestrator)
depend only on this interface — never on a specific runtime's client library.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict


class ModelResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: str
    text: str
    latency_ms: int | None = None
    raw: dict | None = None


class ModelAdapter(ABC):
    id: str
    capabilities: list[str] = []
    # e.g. "text" | "image" | "code" — used by the router to filter candidates
    # for a requested modality. Most text-only models declare just ["text"].
    modalities: list[str] = ["text"]

    @abstractmethod
    def invoke(self, prompt: str, **kwargs) -> ModelResponse:
        """Call the model and return its response. Must not raise on a normal
        (non-exceptional) empty/short completion — only on genuine invocation
        failure (network, timeout, malformed response)."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Cheap, fast liveness check. Must never raise — return False on any
        failure so the router can fall back without a try/except at every call
        site."""
        raise NotImplementedError

    def metadata(self) -> dict:
        return {"id": self.id, "capabilities": self.capabilities, "modalities": self.modalities}
