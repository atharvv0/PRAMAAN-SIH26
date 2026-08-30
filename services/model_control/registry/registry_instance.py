"""Shared model registry for PRAMAAN.

Explicit role environment variables take precedence. When roles are not configured,
local Ollama models are auto-discovered with deterministic role heuristics so a
fresh dev machine with the PRAMAAN SIH MVP models does not silently route normal
text work to the demo adapter.

Recommended local roles:
    reasoning/summarize/coding -> qwen3:4b
    vision/OCR/document_analysis -> gemma3:4b
    embeddings -> handled by services.knowledge, not this registry
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
    "document_analysis": "VISION_MODEL_NAME",
}

_GENERATION_HINTS = (
    "qwen", "llama", "mistral", "mixtral", "gemma", "phi",
    "deepseek", "granite", "command", "minicpm", "llava", "moondream",
)
_VISION_HINTS = (
    "gemma", "llava", "minicpm", "qwen-vl",
    "qwen2.5-vl", "qwen2-vl", "moondream",
)
_CODING_HINTS = (
    "coder", "code", "qwen", "deepseek", "starcoder",
)

_EMBED_HINTS = ("embed", "bge", "e5", "gte")


def _tags(host: str, port: int) -> list[str]:
    try:
        response = httpx.get(
            f"http://{host}:{port}/api/tags",
            timeout=2.0,
        )
        if response.status_code != 200:
            return []

        models = response.json().get("models", [])
        return [
            str(m.get("name") or "").strip()
            for m in models
            if m.get("name")
        ]
    except (httpx.HTTPError, ValueError, TypeError):
        return []


def _pick(
    model_names: list[str],
    hints: tuple[str, ...],
    excluded: set[str] | None = None,
) -> str | None:
    excluded = excluded or set()

    for name in model_names:
        if name in excluded:
            continue

        low = name.lower()
        if any(hint in low for hint in hints):
            return name

    return None


def _discover_roles(model_names: list[str]) -> dict[str, str]:
    """Infer practical SIH-MVP roles from local Ollama model names.

    Embedding models are deliberately excluded. Discovery remains heuristic and
    generic; no model-specific branching exists in the router itself.
    """
    generation = [
        name
        for name in model_names
        if not any(h in name.lower() for h in _EMBED_HINTS)
        and any(h in name.lower() for h in _GENERATION_HINTS)
    ]

    if not generation:
        return {}

    # Prefer qwen/llama/etc. for general text generation.
    reasoning = (
        _pick(
            generation,
            ("qwen", "llama", "mistral", "phi", "deepseek"),
        )
        or generation[0]
    )

    # Coding can use the same general-purpose model if a coder-specific model
    # is not available.
    coding = _pick(generation, _CODING_HINTS) or reasoning

    # Vision/OCR/document analysis should prefer multimodal-capable models.
    vision = _pick(generation, _VISION_HINTS)
    if vision is None:
        vision = reasoning

    return {
        "reasoning": reasoning,
        "summarize_text": reasoning,
        "coding": coding,
        "ocr": vision,
        "vision": vision,
        "document_analysis": vision,
    }


def _modalities_for(capabilities: list[str]) -> list[str]:
    multimodal_caps = {
        "vision",
        "ocr",
        "document_analysis",
        "multimodal",
    }
    if any(cap in multimodal_caps for cap in capabilities):
        return ["text", "image"]
    return ["text"]


def build_default_registry() -> ModelRegistry:
    registry = ModelRegistry()

    host = os.environ.get("MODEL_RUNTIME_HOST", "localhost")
    port = int(os.environ.get("MODEL_RUNTIME_PORT", "11434"))

    role_models: dict[str, str] = {}

    # Explicit environment configuration always wins.
    for capability, env_var in _CAPABILITY_ENV_MAP.items():
        model_name = os.environ.get(env_var, "").strip()
        if model_name:
            role_models[capability] = model_name

    # Fill any unconfigured roles by discovering local Ollama models.
    if os.environ.get("AUTO_DISCOVER_OLLAMA_MODELS", "1") != "0":
        discovered = _discover_roles(_tags(host, port))
        for capability, model_name in discovered.items():
            role_models.setdefault(capability, model_name)

    # One adapter per model, with all roles it was assigned.
    model_to_capabilities: dict[str, list[str]] = {}
    for capability, model_name in role_models.items():
        model_to_capabilities.setdefault(model_name, []).append(capability)

    for model_name, capabilities in model_to_capabilities.items():
        capabilities = sorted(set(capabilities))

        registry.register(
            OllamaAdapter(
                id=f"ollama-{model_name}",
                model_name=model_name,
                capabilities=capabilities,
                modalities=_modalities_for(capabilities),
                host=host,
                port=port,
            )
        )

    # Always last: router fallback slot.
    registry.register(DemoModelAdapter(id="demo-fallback"))
    return registry


def get_live_model_ids(
    registry: ModelRegistry | None = None,
) -> list[str]:
    registry = registry or default_registry
    return [
        model.id
        for model in registry.all()
        if model.metadata().get("runtime") == "ollama"
    ]


def get_model_registry_status(
    registry: ModelRegistry | None = None,
) -> list[dict[str, Any]]:
    registry = registry or default_registry
    return registry.all_metadata()


default_registry = build_default_registry()
