"""
Real model-backed tools for PRAMAAN.

These tools use the capability-driven model router. The router can select
a healthy local model or fall back to the offline demo adapter.
"""

from __future__ import annotations

from services.model_control.errors import ModelControlError
from services.model_control.registry.registry_instance import default_registry
from services.model_control.router.router import select_model
from services.orchestrator.errors import ModelUnavailableError
from services.orchestrator.tools.base import ToolAdapter


class SummarizeTextModelTool(ToolAdapter):
    """Model-backed text summarization tool."""

    id = "text.summarize_model"
    required_permissions: list[str] = []

    # This tool does not itself require outbound network access.
    # Local Ollama and the offline DemoModelAdapter are both valid backends.
    declares_network_access = False

    def invoke(self, inputs: dict) -> dict:
        content = None

        for value in inputs.values():
            if isinstance(value, dict) and "content" in value:
                content = value["content"]
                break

        if content is None:
            raise ValueError(
                "SummarizeTextModelTool found no upstream content to summarize"
            )

        try:
            model = select_model(
                default_registry,
                capability="summarize_text",
            )

            response = model.invoke(
                f"Summarize the following text in 2-3 sentences:\n\n{content}"
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
        }