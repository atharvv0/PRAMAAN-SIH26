"""
Executor — walks a Plan's steps in dependency order, calling tools via the
ToolRegistry, updating AgentState as it goes.

Safety rules:
  - hard max_steps ceiling
  - bounded retries per step
  - approval-required steps pause execution
  - every tool call passes through PolicyEngine
  - every policy decision is recorded in AuditLog
  - model-backed tool results are recorded in AgentState.model_calls
"""

from __future__ import annotations

from datetime import datetime, timezone

from services.governance.audit.log import AuditLog, default_audit_log
from services.governance.policy_engine.base import (
    PolicyEngine,
    default_policy_engine,
)
from services.orchestrator.errors import (
    AgentLoopLimitError,
    PermissionDeniedError,
    ToolExecutionError,
)
from services.orchestrator.planner.schemas import Plan, PlanStep, StepStatus
from services.orchestrator.state_graph.agent_state import (
    AgentError as AgentErrorRecord,
)
from services.orchestrator.state_graph.agent_state import (
    AgentState,
    EvidenceRecord,
    ModelCall,
    ToolCall,
)
from services.orchestrator.tools.base import ToolRegistry


DEFAULT_MAX_STEPS = 20
DEFAULT_MAX_RETRIES_PER_STEP = 1


def _ready_steps(
    plan: Plan,
    completed_ids: set[str],
) -> list[PlanStep]:
    ready: list[PlanStep] = []

    for step in plan.steps:
        if step.status != StepStatus.PENDING:
            continue

        if all(dep in completed_ids for dep in step.depends_on):
            ready.append(step)

    return ready


def _emit(
    state: AgentState,
    event_type: str,
    **detail,
) -> None:
    state.events.append(
        {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **detail,
        }
    )


def run_plan(
    state: AgentState,
    registry: ToolRegistry,
    max_steps: int = DEFAULT_MAX_STEPS,
    max_retries_per_step: int = DEFAULT_MAX_RETRIES_PER_STEP,
    policy_engine: PolicyEngine = default_policy_engine,
    audit_log: AuditLog = default_audit_log,
) -> AgentState:

    if state.plan is None:
        raise ValueError("state.plan must be set before running the executor")

    if not state.events:
        _emit(
            state,
            "TASK_CREATED",
            task_id=state.task_id,
        )

        _emit(
            state,
            "PLAN_CREATED",
            step_count=len(state.plan.steps),
        )

    steps_run = 0
    retries: dict[str, int] = {}

    while True:
        pending_steps = [
            step
            for step in state.plan.steps
            if step.status == StepStatus.PENDING
        ]

        if not pending_steps:
            break

        ready = _ready_steps(
            state.plan,
            set(state.completed_steps),
        )

        if not ready:
            # Steps remain but none are unblocked.
            # This indicates an upstream failure or dependency cycle.
            break

        step = ready[0]

        # --------------------------------------------------------------
        # Human approval gate
        # --------------------------------------------------------------
        if step.requires_approval and state.approval_status != "approved":
            state.approval_status = "pending"
            state.current_step = step.id

            _emit(
                state,
                "APPROVAL_REQUIRED",
                step_id=step.id,
            )

            return state

        # --------------------------------------------------------------
        # Hard execution limit
        # --------------------------------------------------------------
        if steps_run >= max_steps:
            err = AgentLoopLimitError(
                f"executor exceeded max_steps={max_steps} "
                f"for task {state.task_id}"
            )

            state.errors.append(
                AgentErrorRecord(
                    code=err.code,
                    message=err.message,
                    retryable=err.retryable,
                )
            )

            _emit(
                state,
                "TASK_FAILED",
                reason=err.code,
            )

            raise err

        state.current_step = step.id
        step.status = StepStatus.RUNNING

        _emit(
            state,
            "STEP_STARTED",
            step_id=step.id,
            capability=step.capability,
        )

        try:
            result: dict = {}

            # ----------------------------------------------------------
            # Tool execution
            # ----------------------------------------------------------
            if step.tool:
                tool = registry.get(step.tool)

                # ------------------------------------------------------
                # Policy gate
                # ------------------------------------------------------
                decision = policy_engine.check(
                    actor=state.user_id,
                    action="tool.invoke",
                    tool_id=step.tool,
                    declares_network_access=tool.declares_network_access,
                )

                audit_log.record(
                    actor=state.user_id,
                    action="tool.invoke",
                    target=step.tool,
                    decision="allow" if decision.allow else "deny",
                    policy_reason=decision.reason,
                )

                if not decision.allow:
                    raise PermissionDeniedError(
                        decision.reason
                    )

                _emit(
                    state,
                    "TOOL_STARTED",
                    step_id=step.id,
                    tool=step.tool,
                )

                # ------------------------------------------------------
                # Actual tool invocation
                # ------------------------------------------------------
                if step.tool == "knowledge.search":
                    step.inputs = {**step.inputs, "user_id": state.user_id}
                if step.tool in {"text.summarize_model", "model.reason", "artifact.write"}:
                    step.inputs = {**step.inputs, "intent": state.intent}
                result = tool.invoke(step.inputs)

                # ------------------------------------------------------
                # Record successful tool call
                # ------------------------------------------------------
                state.tool_calls.append(
                    ToolCall(
                        tool_id=step.tool,
                        inputs=step.inputs,
                        output=result,
                    )
                )

                # ------------------------------------------------------
                # Record model-backed execution
                #
                # Model-backed tools return:
                #   model_id
                #   latency_ms
                #
                # Example:
                # {
                #     "summary": "...",
                #     "model_id": "ollama-...",
                #     "latency_ms": 1234
                # }
                # ------------------------------------------------------
                if isinstance(result, dict) and result.get("model_id"):
                    state.model_calls.append(
                        ModelCall(
                            model_id=str(result["model_id"]),
                            purpose=step.capability,
                            latency_ms=result.get("latency_ms"),
                        )
                    )

                _emit(
                    state,
                    "TOOL_COMPLETED",
                    step_id=step.id,
                    tool=step.tool,
                )

            # ----------------------------------------------------------
            # Mark step complete
            # ----------------------------------------------------------
            step.status = StepStatus.DONE
            state.completed_steps.append(step.id)

            # ----------------------------------------------------------
            # Evidence population
            # ----------------------------------------------------------
            raw_evidence = (
                result.get("evidence")
                if isinstance(result, dict)
                else None
            )

            if isinstance(raw_evidence, list):
                for item in raw_evidence:
                    if (
                        not isinstance(item, dict)
                        or "claim" not in item
                        or "source" not in item
                    ):
                        continue

                    state.evidence.append(
                        EvidenceRecord(
                            claim=item["claim"],
                            source=item["source"],
                            page_or_region=item.get("page_or_region"),
                            model=item.get("model"),
                            tool=step.tool,
                            confidence=item.get("confidence"),
                            validation_state=item.get(
                                "validation_state",
                                "unverified",
                            ),
                        )
                    )

                    _emit(
                        state,
                        "EVIDENCE_ADDED",
                        step_id=step.id,
                    )

            # ----------------------------------------------------------
            # Simple data-flow
            #
            # Pass this step's output to dependent steps.
            # ----------------------------------------------------------
            for other in state.plan.steps:
                if step.id in other.depends_on:
                    other.inputs = {
                        **other.inputs,
                        f"upstream_{step.id}": result,
                    }

        except PermissionDeniedError as exc:
            # ----------------------------------------------------------
            # Permission denial is never retried.
            # ----------------------------------------------------------
            step.status = StepStatus.FAILED

            state.errors.append(
                AgentErrorRecord(
                    code=exc.code,
                    message=exc.message,
                    retryable=exc.retryable,
                )
            )

            _emit(
                state,
                "TASK_FAILED",
                step_id=step.id,
                reason=exc.code,
            )

            break

        except Exception as exc:  # noqa: BLE001
            # ----------------------------------------------------------
            # Bounded retry
            # ----------------------------------------------------------
            attempt = retries.get(step.id, 0)

            if attempt < max_retries_per_step:
                retries[step.id] = attempt + 1
                step.status = StepStatus.PENDING
                continue

            # ----------------------------------------------------------
            # Final failure
            # ----------------------------------------------------------
            step.status = StepStatus.FAILED

            wrapped = ToolExecutionError(
                str(exc),
                detail=repr(exc),
            )

            state.errors.append(
                AgentErrorRecord(
                    code=wrapped.code,
                    message=wrapped.message,
                    retryable=wrapped.retryable,
                )
            )

            # Record the failed tool invocation.
            if step.tool:
                state.tool_calls.append(
                    ToolCall(
                        tool_id=step.tool,
                        inputs=step.inputs,
                        error=str(exc),
                    )
                )

            _emit(
                state,
                "TASK_FAILED",
                step_id=step.id,
                reason=wrapped.code,
            )

            # MVP behaviour:
            # stop on first unrecoverable failure.
            break

        steps_run += 1

    # ------------------------------------------------------------------
    # Task completion
    # ------------------------------------------------------------------
    if state.plan.steps and all(
        step.status == StepStatus.DONE
        for step in state.plan.steps
    ):
        tool_outputs = [
            tool_call.output
            for tool_call in state.tool_calls
            if tool_call.output is not None
        ]

        # Prefer the final reasoning/model output as the user-facing answer;
        # otherwise use the last summary/content result, then the raw tool trace.
        response_text = None
        for output in reversed(tool_outputs):
            if isinstance(output, dict):
                candidate = output.get("content") or output.get("answer")
                if isinstance(candidate, str) and candidate.strip():
                    response_text = candidate.strip()
                    break
                candidate = output.get("summary")
                if isinstance(candidate, str) and candidate.strip():
                    response_text = candidate.strip()
                    break

        state.final_output = {
            "task_id": state.task_id,
            "goal": state.plan.goal,
            "response": response_text,
            "completed_steps": state.completed_steps,
            "tool_outputs": tool_outputs,
            "evidence": [e.model_dump() for e in state.evidence],
            "model_calls": [m.model_dump() for m in state.model_calls],
            "approval_status": state.approval_status,
        }

        _emit(
            state,
            "TASK_COMPLETED",
            task_id=state.task_id,
        )

    return state