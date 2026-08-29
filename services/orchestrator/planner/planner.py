"""
PRAMAAN planner.

There are two planner entry points:

* create_plan() keeps the deterministic planner used by offline/unit tests.
* create_model_backed_plan() uses the capability-driven Model Router and the
  configured local Ollama reasoning model to produce a structured plan.

The model-backed path never executes model output directly. The LLM output is
parsed into a dedicated schema, converted into the canonical Plan/PlanStep
objects, and validated against a small safe tool vocabulary before the executor
can see it.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from services.model_control.errors import ModelControlError
from services.model_control.registry.registry import ModelRegistry
from services.model_control.registry.registry_instance import default_registry
from services.model_control.router.router import select_model
from services.orchestrator.errors import ModelUnavailableError, PlannerError
from services.orchestrator.planner.schemas import Plan, PlanStep


# Planner may only emit tools that are actually registered for the MVP and are
# safe to consider for automatic planning. Network demo is deliberately absent.
PLANNER_SAFE_TOOLS = {
    "file.read",
    "ocr.process",
    "knowledge.search",
    "text.summarize_model",
    "model.reason",
    "code.generate_model",
    "code.execute",
}


class GeneratedPlanStep(BaseModel):
    step_no: int = Field(ge=1)
    capability: str = Field(min_length=1, max_length=80)
    tool: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[int] = Field(default_factory=list)
    requires_approval: bool = False


class GeneratedPlan(BaseModel):
    goal: str = Field(min_length=1, max_length=2000)
    steps: list[GeneratedPlanStep] = Field(min_length=1, max_length=20)


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(cleaned[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    raise PlannerError(
        "The planning model returned invalid JSON.",
        detail=f"raw_response={text[:2000]!r}",
    )


def _build_plan_from_generated(
    task_id: str,
    intent: str,
    generated: GeneratedPlan,
    file_path: str | None,
) -> Plan:
    ordered = sorted(generated.steps, key=lambda step: step.step_no)
    expected_numbers = list(range(1, len(ordered) + 1))
    actual_numbers = [step.step_no for step in ordered]
    if actual_numbers != expected_numbers:
        raise PlannerError(
            "The planning model returned non-contiguous step numbers.",
            detail=f"step_numbers={actual_numbers}",
        )

    known_numbers = set(actual_numbers)
    built_steps: list[PlanStep] = []
    number_to_id: dict[int, str] = {}

    for generated_step in ordered:
        if generated_step.tool and generated_step.tool not in PLANNER_SAFE_TOOLS:
            raise PlannerError(
                f"Planner proposed unsupported tool '{generated_step.tool}'.",
                detail=f"allowed_tools={sorted(PLANNER_SAFE_TOOLS)}",
            )

        invalid_dependencies = [d for d in generated_step.depends_on if d not in known_numbers or d >= generated_step.step_no]
        if invalid_dependencies:
            raise PlannerError(
                f"Planner returned invalid dependencies for step {generated_step.step_no}.",
                detail=f"invalid_dependencies={invalid_dependencies}",
            )

        inputs = dict(generated_step.inputs)
        if file_path and generated_step.tool in {"file.read", "ocr.process"}:
            inputs.setdefault("path", file_path)
        if generated_step.tool == "knowledge.search":
            inputs.setdefault("query", intent)

        step = PlanStep(
            capability=generated_step.capability,
            tool=generated_step.tool,
            inputs=inputs,
            requires_approval=generated_step.requires_approval,
        )
        built_steps.append(step)
        number_to_id[generated_step.step_no] = step.id

    for generated_step, built_step in zip(ordered, built_steps, strict=True):
        built_step.depends_on = [number_to_id[d] for d in generated_step.depends_on]

    return Plan(task_id=task_id, goal=generated.goal or intent, steps=built_steps)


def _planner_prompt(intent: str, file_path: str | None, available_tools: list[str]) -> str:
    file_context = f"\nA local input file is available at: {file_path}" if file_path else ""
    tools = ", ".join(sorted(available_tools))
    return f"""You are PRAMAAN's local planning engine.

Create a safe, concise execution plan for the user's task.{file_context}

Available tools (use only these exact IDs): {tools}

Rules:
1. Return ONLY valid JSON matching the supplied schema.
2. step_no must start at 1 and increase by 1.
3. depends_on contains earlier step numbers only.
4. tool must be null or one of the allowed tool IDs.
5. Prefer real tools over abstract/unexecutable steps.
6. For scanned/image/P&ID tasks with a local file, prefer tool `ocr.process`.
7. For coding/Python/internal-tool tasks, use `code.generate_model` followed by `code.execute` when execution is required.
8. If the user expects an answer, assessment, recommendation, or deliverable, finish with tool `model.reason` and make it depend on the relevant upstream analysis/evidence steps.
9. If a final recommendation/approval-oriented output is being prepared, mark the final consequential step requires_approval=true.
10. Do not invent facts, file contents, findings, SOP requirements, or tool results.
11. Keep the plan to at most 8 steps.
12. Return JSON with fields: goal, steps[]. Each step has step_no, capability, tool, inputs, depends_on, requires_approval.
13. Use tool ids exactly as provided. Do not return markdown or chain-of-thought.

User task:
{intent}
"""


def create_model_backed_plan(
    task_id: str,
    intent: str,
    file_path: str | None = None,
    registry: ModelRegistry = default_registry,
) -> Plan:
    """Generate a real plan with the locally configured reasoning model."""
    try:
        model = select_model(
            registry,
            capability="reasoning",
            modality="text",
        )
    except ModelControlError as exc:
        raise ModelUnavailableError(str(exc), detail=repr(exc)) from exc

    # A model-backed production plan must never silently downgrade to the demo
    # adapter. Unit/offline callers can still use create_plan().
    if model.metadata().get("runtime") == "demo-offline":
        raise ModelUnavailableError(
            "No healthy local reasoning model is configured for planning.",
            detail="Set REASONING_MODEL_NAME to a pulled Ollama model.",
        )

    schema = GeneratedPlan.model_json_schema()
    prompt = _planner_prompt(intent, file_path, sorted(PLANNER_SAFE_TOOLS))

    try:
        response = model.invoke(
            prompt,
            system="You are PRAMAAN's planning engine. Never reveal chain-of-thought. Return only the requested JSON object.",
            format=schema,
            think=False,
            options={
                "temperature": 0,
                "num_ctx": int(os.environ.get("PLANNER_CONTEXT_LENGTH", "4096")),
            },
        )
    except ModelControlError as exc:
        raise ModelUnavailableError(str(exc), detail=repr(exc)) from exc

    payload = _extract_json_object(response.text)
    try:
        generated = GeneratedPlan.model_validate(payload)
    except ValidationError as exc:
        raise PlannerError(
            "The planning model returned a plan that does not match PRAMAAN's schema.",
            detail=repr(exc),
        ) from exc

    plan = _build_plan_from_generated(task_id, intent, generated, file_path)
    if any(k in intent.lower() for k in ("approval note", "approval", "approve", "sign-off", "signoff")) and plan.steps:
        plan.steps[-1].requires_approval = True
    return plan


def create_plan(
    task_id: str,
    intent: str,
    file_path: str | None = None,
) -> Plan:
    """Deterministic compatibility/production plan.

    Production callers that do not yet enable the model-backed planner still get
    executable tool steps. In particular, file-backed tasks finish with a real
    model.reason step so the run produces a user-facing answer rather than only a
    tool trace.
    """
    intent_lower = intent.lower()

    if any(
        k in intent_lower
        for k in (
            "network",
            "outbound",
            "external call",
            "sovereignty proof",
            "sovereign proof",
        )
    ):
        return Plan(
            task_id=task_id,
            goal=intent,
            steps=[
                PlanStep(
                    capability="network_egress_test",
                    tool="network.fetch_demo",
                    inputs={},
                )
            ],
        )

    if any(
        k in intent_lower
        for k in (
            "sop",
            "search the knowledge",
            "what does the sop",
            "search sop",
            "look up",
        )
    ):
        search_step = PlanStep(
            capability="knowledge_search",
            tool="knowledge.search",
            inputs={"query": intent},
        )
        reason_step = PlanStep(
            capability="reasoning",
            tool="model.reason",
            inputs={"intent": intent},
            depends_on=[search_step.id],
        )
        return Plan(
            task_id=task_id,
            goal=intent,
            steps=[search_step, reason_step],
        )

    is_visual_document = file_path and any(
        k in intent_lower
        for k in (
            "scan",
            "scanned",
            "p&id",
            "pid drawing",
            "drawing",
            "ocr",
            "vision",
            "image",
            "photo",
            "handwrit",
            "inspection package",
            "inspection report",
            "pressure vessel",
        )
    )

    if is_visual_document:
        analysis_step = PlanStep(
            capability="document_analysis",
            tool="ocr.process",
            inputs={"path": file_path},
        )
        summarize_step = PlanStep(
            capability="summarize_text",
            tool="text.summarize_model",
            inputs={},
            depends_on=[analysis_step.id],
        )
        respond_step = PlanStep(
            capability="reasoning",
            tool="model.reason",
            inputs={"intent": intent},
            depends_on=[analysis_step.id, summarize_step.id],
        )
        return Plan(
            task_id=task_id,
            goal=intent,
            steps=[analysis_step, summarize_step, respond_step],
        )

    if file_path:
        read_step = PlanStep(
            capability="document_analysis",
            tool="file.read",
            inputs={"path": file_path},
        )

        if "summar" in intent_lower:
            summarize_step = PlanStep(
                capability="summarize_text",
                tool="text.summarize_model",
                inputs={},
                depends_on=[read_step.id],
            )
            respond_step = PlanStep(
                capability="reasoning",
                tool="model.reason",
                inputs={"intent": intent},
                depends_on=[read_step.id, summarize_step.id],
            )
            return Plan(
                task_id=task_id,
                goal=intent,
                steps=[read_step, summarize_step, respond_step],
            )

        respond_step = PlanStep(
            capability="reasoning",
            tool="model.reason",
            inputs={"intent": intent},
            depends_on=[read_step.id],
        )
        return Plan(
            task_id=task_id,
            goal=intent,
            steps=[read_step, respond_step],
        )

    # Generic tasks still get a real answer-capable step.
    respond_step = PlanStep(
        capability="reasoning",
        tool="model.reason",
        inputs={"intent": intent},
    )
    if "approval" in intent_lower or "approve" in intent_lower:
        respond_step.requires_approval = True

    return Plan(
        task_id=task_id,
        goal=intent,
        steps=[respond_step],
    )
