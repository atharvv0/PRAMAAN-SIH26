"""Shared model registry for PRAMAAN.

Explicit role environment variables take precedence. If roles are not configured,
local Ollama models can be auto-discovered so a fresh dev machine does not silently
fall back to the demo adapter when a real model is already installed.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

from services.model_control.adapters.demo_adapter import DemoModelAdapter
from services.model_control.adapters.ollama_adapter import OllamaAdapter
from services.model_control.registry.registry import ModelRegistry


_CAPABILITY_ENV_MAP = {
    "reasoning": "REASONING_MODEL_NAME",
    "summarize_text": "REASONING_MODEL_NAME",
    "coding": "CODING_MODEL_NAME",
    "ocr": "OCR_MODEL_NAME",
    "vision": "VISION_MODEL_NAME",
}

_GENERATION_HINTS = (
    "qwen", "llama", "mistral", "mixtral", "gemma", "phi",
    "deepseek", "granite", "command", "minicpm", "llava", "moondream",
)
_VISION_HINTS = ("gemma", "llava", "minicpm", "qwen-vl", "qwen2.5-vl", "moondream")
_CODING_HINTS = ("coder", "code", "qwen", "deepseek", "starcoder")
_EMBED_HINTS = ("embed", "bge", "e5", "gte")


def _tags(host: str, port: int) -> list[str]:
    try:
        response = httpx.get(f"http://{host}:{port}/api/tags", timeout=2.0)
        if response.status_code != 200:
            return []
        models = response.json().get("models", [])
        return [str(m.get("name") or "").strip() for m in models if m.get("name")]
    except (httpx.HTTPError, ValueError, TypeError):
        return []


def _discover_roles(model_names: list[str]) -> dict[str, str]:
    generation = [
        name for name in model_names
        if not any(h in name.lower() for h in _EMBED_HINTS)
        and any(h in name.lower() for h in _GENERATION_HINTS)
    ]
    if not generation:
        return {}

    def pick(hints: tuple[str, ...], excluded: set[str] | None = None) -> str | None:
        excluded = excluded or set()
        for name in generation:
            low = name.lower()
            if name not in excluded and any(h in low for h in hints):
                return name
        return None

    reasoning = pick(("qwen", "llama", "gemma", "mistral", "phi", "deepseek")) or generation[0]
    coding = pick(_CODING_HINTS) or reasoning
    vision = pick(_VISION_HINTS) or reasoning

    return {
        "reasoning": reasoning,
        "summarize_text": reasoning,
        "coding": coding,
        "ocr": vision,
        "vision": vision,
    }


def build_default_registry() -> ModelRegistry:
    registry = ModelRegistry()
    host = os.environ.get("MODEL_RUNTIME_HOST", "localhost")
    port = int(os.environ.get("MODEL_RUNTIME_PORT", "11434"))

    role_models: dict[str, str] = {}
    for capability, env_var in _CAPABILITY_ENV_MAP.items():
        model_name = os.environ.get(env_var, "").strip()
        if model_name:
            role_models[capability] = model_name

    if os.environ.get("AUTO_DISCOVER_OLLAMA_MODELS", "1") != "0":
        for capability, model_name in _discover_roles(_tags(host, port)).items():
            role_models.setdefault(capability, model_name)

    model_to_capabilities: dict[str, list[str]] = {}
    for capability, model_name in role_models.items():
        model_to_capabilities.setdefault(model_name, []).append(capability)

    for model_name, capabilities in model_to_capabilities.items():
        registry.register(
            OllamaAdapter(
                id=f"ollama-{model_name}",
                model_name=model_name,
                capabilities=sorted(set(capabilities)),
                host=host,
                port=port,
            )
        )

    registry.register(DemoModelAdapter(id="demo-fallback"))
    return registry


def get_live_model_ids(registry: ModelRegistry | None = None) -> list[str]:
    registry = registry or default_registry
    return [m.id for m in registry.all() if m.metadata().get("runtime") == "ollama"]


def get_model_registry_status(registry: ModelRegistry | None = None) -> list[dict[str, Any]]:
    registry = registry or default_registry
    return registry.all_metadata()


default_registry = build_default_registry()
