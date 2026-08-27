"""
The shared ModelRegistry instance other services import. Callers (services/backend,
services/orchestrator tools) should only ever import `default_registry` from here —
never construct their own ModelRegistry — same convention as
services/orchestrator/tools/registry_instance.py's `default_registry`.

Configuration is entirely environment-driven (.env.example "Model Runtime" section):
  MODEL_RUNTIME_HOST, MODEL_RUNTIME_PORT   — where the Ollama dev runtime listens
  REASONING_MODEL_NAME, CODING_MODEL_NAME,
  OCR_MODEL_NAME, VISION_MODEL_NAME        — which pulled model backs each capability

Any of the *_MODEL_NAME vars left blank simply means that capability has no live
Ollama adapter registered — the offline DemoModelAdapter (registered last for every
capability, see below) is still available so select_model() never raises
ModelUnavailableError for these MVP capabilities. This satisfies "at least two
models available through one ModelAdapter interface" (services/model_control/README.md
DoD) as soon as any *_MODEL_NAME is configured — the demo adapter is always the
second (fallback) one, and a real Ollama adapter takes priority whenever it's
healthy.

vLLM (production runtime): add a parallel `if os.environ.get("MODEL_RUNTIME") ==
"vllm":` branch here once services/model_control/adapters/vllm_adapter.py exists
(see that adapter's docstring for why it isn't built yet) — do not change the
registry/router interfaces to add it.
"""
from __future__ import annotations

import os

from services.model_control.adapters.demo_adapter import DemoModelAdapter
from services.model_control.adapters.ollama_adapter import OllamaAdapter
from services.model_control.registry.registry import ModelRegistry

# capability -> env var naming the Ollama model that serves it
_CAPABILITY_ENV_MAP = {
    "reasoning": "REASONING_MODEL_NAME",
    "summarize_text": "REASONING_MODEL_NAME",  # summarization rides the reasoning model
    "coding": "CODING_MODEL_NAME",
    "ocr": "OCR_MODEL_NAME",
    "vision": "VISION_MODEL_NAME",
}


def build_default_registry() -> ModelRegistry:
    registry = ModelRegistry()

    host = os.environ.get("MODEL_RUNTIME_HOST", "localhost")
    port = int(os.environ.get("MODEL_RUNTIME_PORT", "11434"))

    # Group capabilities by configured model name so one adapter can legitimately
    # declare several capabilities (e.g. one reasoning model also does
    # summarize_text) instead of registering a duplicate adapter per capability.
    model_to_capabilities: dict[str, list[str]] = {}
    for capability, env_var in _CAPABILITY_ENV_MAP.items():
        model_name = os.environ.get(env_var, "").strip()
        if not model_name:
            continue
        model_to_capabilities.setdefault(model_name, []).append(capability)

    for model_name, capabilities in model_to_capabilities.items():
        registry.register(
            OllamaAdapter(
                id=f"ollama-{model_name}",
                model_name=model_name,
                capabilities=capabilities,
                host=host,
                port=port,
            )
        )

    # Offline fallback — registered last for every MVP capability so
    # select_model()'s "last candidate = fallback" convention (router.py) holds
    # regardless of which/how many real models are configured above.
    registry.register(DemoModelAdapter(id="demo-fallback"))

    return registry


default_registry = build_default_registry()
