"""
Real model-backed tools for PRAMAAN.

All model calls go through the capability-driven Model Router.
The router may select a healthy local Ollama model or the offline
DemoModelAdapter fallback.
"""

from __future__ import annotations

from services.model_control.errors import ModelControlError
from services.model_control.router.router import select_model
from services.orchestrator.errors import ModelUnavailableError
from services.orchestrator.tools.base import ToolAdapter


class SummarizeTextModelTool(ToolAdapter):
    """Model-backed text summarization tool."""

    id = "text.summarize_model"
    required_permissions: list[str] = []
    declares_network_access = False

    def invoke(self, inputs: dict) -> dict:
        content = None

        for value in inputs.values():
            if isinstance(value, dict) and "content" in value:
                content = value["content"]
                break

        if content is None and isinstance(inputs.get("content"), str):
            content = inputs["content"]

        if not content:
            raise ValueError(
                "SummarizeTextModelTool found no upstream content to summarize"
            )

        try:
            from services.model_control.registry.registry_instance import default_registry
            model = select_model(
                default_registry,
                capability="summarize_text",
                modality="text",
            )

            response = model.invoke(
                "Summarize the following text in 2-3 concise sentences:\n\n"
                + content
            )

        except ModelControlError as exc:
            raise ModelUnavailableError(
                str(exc),
                detail=repr(exc),
            ) from exc

        return {
            "summary": response.text,
            "model_id": response.model_id,
            "latency_ms": response.latency_ms,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }


class ReasoningModelTool(ToolAdapter):
    """
    General model-backed reasoning/respond tool.

    This is the bridge between the orchestrator and Model Router.
    """

    id = "model.reason"
    required_permissions: list[str] = []
    declares_network_access = False

    def invoke(self, inputs: dict) -> dict:
        prompt = inputs.get("prompt") or inputs.get("intent")

        if not prompt:
            raise ValueError("ReasoningModelTool requires 'prompt' or 'intent'")

        try:
            from services.model_control.registry.registry_instance import default_registry
            model = select_model(
                default_registry,
                capability="reasoning",
                modality="text",
            )

            response = model.invoke(str(prompt))

        except ModelControlError as exc:
            raise ModelUnavailableError(
                str(exc),
                detail=repr(exc),
            ) from exc

        return {
            "content": response.text,
            "model_id": response.model_id,
            "latency_ms": response.latency_ms,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }

class CodingModelTool(ToolAdapter):
    id = "code.generate_model"
    required_permissions: list[str] = []
    declares_network_access = False

    def generate_code(self, task: str) -> dict:
        try:
            model = select_model(default_registry, capability="coding", modality="text")
            response = model.invoke(
                "You are PRAMAAN's local coding agent. Return ONLY a complete Python program, "
                "without markdown fences or explanation. The program must read no network and "
                "write only within the provided working directory. Task:\n" + task,
                system="Generate safe, testable code. Never use network access.",
                options={"temperature": 0},
                think=False,
            )
        except ModelControlError as exc:
            raise ModelUnavailableError(str(exc), detail=repr(exc)) from exc
        code = response.text.strip()
        if code.startswith("```"):
            code = code.replace("```python", "", 1).replace("```", "").strip()
        return {"code": code, "model_id": response.model_id, "latency_ms": response.latency_ms}

    def invoke(self, inputs: dict) -> dict:
        prompt = inputs.get("prompt") or inputs.get("intent")
        if not prompt:
            raise ValueError("CodingModelTool requires 'prompt' or 'intent'")
        return self.generate_code(str(prompt))
