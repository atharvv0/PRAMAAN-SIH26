"""
Real (non-demo) tools backed by services/model_control — closes the TODO left in
tools/examples.py's SummarizeTextTool ("TODO(Phase 5): replace with a real call
through services/model_control once the Model Router exists").

These are the first tools in this package that are NOT demo-only: they call a real
ModelAdapter (services/model_control/adapters/base.py) selected by the capability-
driven router (services/model_control/router). Behind the scenes that may be a live
Ollama model or, if none is configured/healthy, the offline DemoModelAdapter — the
tool itself doesn't know or care which, by design (docs/architecture.md "Core
Principle: Separation of Concerns").
"""
from __future__ import annotations

from services.model_control.errors import ModelControlError
from services.model_control.registry.registry_instance import default_registry
from services.model_control.router.router import select_model
from services.orchestrator.errors import ModelUnavailableError as OrchestratorModelUnavailableError
from services.orchestrator.tools.base import ToolAdapter


class SummarizeTextModelTool(ToolAdapter):
    """Model-backed replacement for text.summarize_naive. id: text.summarize_model
    (see docs/agent-contract.md tool id family + services/model_control/README.md
    "Contract to implement"). Selects a model for the 'summarize_text' capability
    via the Model Router rather than hard-coding a provider/model — see
    docs/architecture.md "Hard rule" on Agent -> Tool -> (Policy Engine, not yet
    wired — Phase 7) -> real work."""

    id = "text.summarize_model"
    required_permissions: list[str] = []
    declares_network_access = True  # may reach a local Ollama runtime over HTTP

    def invoke(self, inputs: dict) -> dict:
        content = None
        for value in inputs.values():
            if isinstance(value, dict) and "content" in value:
                content = value["content"]
                break
        if content is None:
            raise ValueError("SummarizeTextModelTool found no upstream 'content' to summarize")

        try:
            model = select_model(default_registry, capability="summarize_text")
            response = model.invoke(
                f"Summarize the following text in 2-3 sentences:\n\n{content}"
            )
        except ModelControlError as exc:
            # Translate the model_control-local error into the orchestrator's own
            # error vocabulary (docs/agent-contract.md "Error Classes") so the
            # executor's existing try/except ToolExecutionError handling (see
            # state_graph/executor.py) doesn't need to know about model_control's
            # error types at all.
            raise OrchestratorModelUnavailableError(str(exc), detail=repr(exc)) from exc

        return {
            "summary": response.text,
            "model_id": response.model_id,
            "latency_ms": response.latency_ms,
        }
