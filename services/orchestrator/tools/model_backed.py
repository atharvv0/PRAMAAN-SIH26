"""Model-backed PRAMAAN tools.

All generation calls go through the capability-driven Model Router. The final
reasoning tool consumes dependency outputs so completed runs contain a user-
facing response instead of only a raw tool trace.
"""
from __future__ import annotations

from services.model_control.errors import ModelControlError
from services.model_control.router.router import select_model
from services.orchestrator.errors import ModelUnavailableError
from services.orchestrator.tools.base import ToolAdapter


def _select(capability: str):
    try:
        from services.model_control.registry.registry_instance import default_registry

        return select_model(
            default_registry,
            capability=capability,
            modality="text",
        )
    except ModelControlError as exc:
        raise ModelUnavailableError(str(exc), detail=repr(exc)) from exc


def _flatten_context(inputs: dict) -> str:
    chunks: list[str] = []
    intent = inputs.get("intent")
    if isinstance(intent, str) and intent.strip():
        chunks.append(f"TASK INTENT:\n{intent.strip()}")

    for key, value in inputs.items():
        if not str(key).startswith("upstream_"):
            continue

        if isinstance(value, dict):
            text = value.get("content") or value.get("summary") or value.get("text")
            if text:
                chunks.append(str(text))

            evidence = value.get("evidence")
            if isinstance(evidence, list) and evidence:
                chunks.append(
                    "EVIDENCE:\n" + "\n".join(str(item) for item in evidence)
                )
        elif value:
            chunks.append(str(value))

    return "\n\n".join(chunks).strip()


class SummarizeTextModelTool(ToolAdapter):
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

        model = _select("summarize_text")
        response = model.invoke(
            "Summarize the following source material in 2-3 concise sentences. "
            "Preserve important facts, numbers, deficiencies, and safety-relevant "
            "details. Do not invent information.\n\n" + str(content),
            system=(
                "You are PRAMAAN's local document summarization model. "
                "Do not invent facts."
            ),
            options={"temperature": 0},
            think=False,
        )

        return {
            "summary": response.text,
            "model_id": response.model_id,
            "latency_ms": response.latency_ms,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }


class ReasoningModelTool(ToolAdapter):
    id = "model.reason"
    required_permissions: list[str] = []
    declares_network_access = False

    def invoke(self, inputs: dict) -> dict:
        prompt = inputs.get("prompt") or inputs.get("intent")
        context = _flatten_context(inputs)

        if context:
            prompt = f"{prompt or ''}\n\nSOURCE CONTEXT:\n{context}".strip()

        if not prompt:
            raise ValueError(
                "ReasoningModelTool requires 'prompt', 'intent', or upstream context"
            )

        model = _select("reasoning")
        response = model.invoke(
            str(prompt),
            system=(
                "You are PRAMAAN's local engineering reasoning model. "
                "Answer only from the supplied task context. Distinguish facts from "
                "uncertainty. Never invent missing measurements, requirements, or findings."
            ),
            options={"temperature": 0},
            think=False,
        )

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
        model = _select("coding")
        response = model.invoke(
            "Generate safe, testable Python code for this task. Return only the complete "
            "program.\n\n" + str(task),
            system=(
                "Never use network access. Write only within the supplied working "
                "directory when executed."
            ),
            options={"temperature": 0},
            think=False,
        )

        code = response.text.strip()
        if code.startswith("```"):
            code = code.replace("```python", "", 1).replace("```", "").strip()

        return {
            "code": code,
            "model_id": response.model_id,
            "latency_ms": response.latency_ms,
        }

    def invoke(self, inputs: dict) -> dict:
        task = inputs.get("prompt") or inputs.get("intent") or _flatten_context(inputs)
        if not task:
            raise ValueError(
                "CodingModelTool requires 'prompt', 'intent', or upstream context"
            )
        return self.generate_code(str(task))
