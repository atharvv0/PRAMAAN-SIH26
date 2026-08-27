"""
Executor — walks a Plan's steps in dependency order, calling tools via the
ToolRegistry, updating AgentState as it goes.

Safety rules enforced here (master prompt section 49 — never `while True: agent.run()`):
  - hard max_steps ceiling -> AgentLoopLimitError
  - bounded retries per step, not infinite retry
  - a step with requires_approval=True is never auto-executed; execution pauses and
    approval_status is set to "pending" for the caller to surface as APPROVAL_REQUIRED

NOT done here yet (explicitly out of scope for this pass — do not silently add):
  - Policy Engine gate before each tool call (services/governance/policy_engine
    doesn't exist yet — TODO Phase 7). Once it does, the tool-call block below is
    where `Agent -> Tool Request -> Policy Engine -> ALLOW/DENY -> Tool` gets wired in.
  - Persistence of AgentState between calls (Phase 3, coordinate with the data owner).
  - Model-backed re-planning on failure (Phase 5+).

Evidence population: any tool result with an "evidence" list (shaped per
docs/agent-contract.md "EvidenceRecord") is appended to state.evidence automatically —
see the block below. Tools that don't produce evidence simply omit the key.
"""
from __future__ import annotations

from services.orchestrator.errors import AgentLoopLimitError, ToolExecutionError
from services.orchestrator.planner.schemas import Plan, PlanStep, StepStatus
from services.orchestrator.state_graph.agent_state import (
    AgentError as AgentErrorRecord,
)
from services.orchestrator.state_graph.agent_state import AgentState, EvidenceRecord, ToolCall
from services.orchestrator.tools.base import ToolRegistry

DEFAULT_MAX_STEPS = 20
DEFAULT_MAX_RETRIES_PER_STEP = 1


def _ready_steps(plan: Plan, completed_ids: set[str]) -> list[PlanStep]:
    ready = []
    for step in plan.steps:
        if step.status != StepStatus.PENDING:
            continue
        if all(dep in completed_ids for dep in step.depends_on):
            ready.append(step)
    return ready


def run_plan(
    state: AgentState,
    registry: ToolRegistry,
    max_steps: int = DEFAULT_MAX_STEPS,
    max_retries_per_step: int = DEFAULT_MAX_RETRIES_PER_STEP,
) -> AgentState:
    if state.plan is None:
        raise ValueError("state.plan must be set before running the executor")

    steps_run = 0
    retries: dict[str, int] = {}

    while True:
        pending_steps = [s for s in state.plan.steps if s.status == StepStatus.PENDING]
        if not pending_steps:
            break

        ready = _ready_steps(state.plan, set(state.completed_steps))
        if not ready:
            # Steps remain but none are unblocked -> upstream failure or a cycle.
            # Don't spin: stop and let the caller inspect state.errors.
            break

        step = ready[0]

        if step.requires_approval and state.approval_status != "approved":
            state.approval_status = "pending"
            state.current_step = step.id
            return state  # caller surfaces APPROVAL_REQUIRED; resume after approval

        if steps_run >= max_steps:
            err = AgentLoopLimitError(
                f"executor exceeded max_steps={max_steps} for task {state.task_id}"
            )
            state.errors.append(
                AgentErrorRecord(code=err.code, message=err.message, retryable=err.retryable)
            )
            raise err

        state.current_step = step.id
        step.status = StepStatus.RUNNING

        try:
            result: dict = {}
            if step.tool:
                tool = registry.get(step.tool)
                result = tool.invoke(step.inputs)
                state.tool_calls.append(
                    ToolCall(tool_id=step.tool, inputs=step.inputs, output=result)
                )
            step.status = StepStatus.DONE
            state.completed_steps.append(step.id)

            # Evidence population — see docs/agent-contract.md "EvidenceRecord".
            # Contract: any tool may return an "evidence" key (list of dicts shaped
            # like EvidenceRecord). Tools that don't produce evidence just omit it.
            raw_evidence = result.get("evidence") if isinstance(result, dict) else None
            if isinstance(raw_evidence, list):
                for item in raw_evidence:
                    if not isinstance(item, dict) or "claim" not in item or "source" not in item:
                        continue  # malformed evidence entry — skip rather than crash the run
                    state.evidence.append(
                        EvidenceRecord(
                            claim=item["claim"],
                            source=item["source"],
                            page_or_region=item.get("page_or_region"),
                            model=item.get("model"),
                            tool=step.tool,
                            confidence=item.get("confidence"),
                            validation_state=item.get("validation_state", "unverified"),
                        )
                    )

            # Simple data-flow: hand this step's output to any step that depends on it.
            for other in state.plan.steps:
                if step.id in other.depends_on:
                    other.inputs = {**other.inputs, f"upstream_{step.id}": result}

        except Exception as exc:  # noqa: BLE001 — deliberately broad: wrap into a typed error
            attempt = retries.get(step.id, 0)
            if attempt < max_retries_per_step:
                retries[step.id] = attempt + 1
                step.status = StepStatus.PENDING  # retry on the next loop iteration
                continue
            step.status = StepStatus.FAILED
            wrapped = ToolExecutionError(str(exc), detail=repr(exc))
            state.errors.append(
                AgentErrorRecord(code=wrapped.code, message=wrapped.message, retryable=wrapped.retryable)
            )
            break  # MVP behaviour: stop on first un-retryable failure, don't cascade

        steps_run += 1

    if state.plan.steps and all(s.status == StepStatus.DONE for s in state.plan.steps):
        state.final_output = {
            "task_id": state.task_id,
            "completed_steps": state.completed_steps,
            "tool_outputs": [tc.output for tc in state.tool_calls],
        }

    return state
