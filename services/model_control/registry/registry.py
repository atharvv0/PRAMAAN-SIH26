"""
ModelRegistry — see services/model_control/README.md.

Registering a new model is config, not code: construct an adapter (any
ModelAdapter implementation) and call register(). Nothing else in this module
needs to change to add a model — see the "no redesign needed to add a new
model" PS requirement in services/model_control/README.md.
"""
from __future__ import annotations

from services.model_control.adapters.base import ModelAdapter


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, ModelAdapter] = {}

    def register(self, adapter: ModelAdapter) -> None:
        if adapter.id in self._models:
            raise ValueError(f"model '{adapter.id}' already registered")
        self._models[adapter.id] = adapter

    def get(self, model_id: str) -> ModelAdapter:
        if model_id not in self._models:
            raise KeyError(f"model '{model_id}' not registered")
        return self._models[model_id]

    def list_ids(self) -> list[str]:
        return list(self._models.keys())

    def list_by_capability(self, capability: str, modality: str | None = None) -> list[ModelAdapter]:
        """Order of registration is the default preference order — callers that
        want a different priority pass an explicit order via the router, not by
        mutating this registry."""
        candidates = [m for m in self._models.values() if capability in m.capabilities]
        if modality:
            candidates = [m for m in candidates if modality in m.modalities]
        return candidates

    def all(self) -> list[ModelAdapter]:
        return list(self._models.values())

    def all_metadata(self) -> list[dict]:
        return [m.metadata() for m in self._models.values()]
