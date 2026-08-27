"""
Run API — executes a task's agent loop and supports pausing/resuming for approval.
See docs/api-contract.md.

Phase 3 status: synchronous execution, in-memory AgentState kept alongside the task
record (persists for the life of the process, not across restarts — TODO Phase 3
continuation, coordinate with the data owner for real Postgres persistence).
"""
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.api.tasks import _TASKS
from app.models.run import RunResult
from services.orchestrator.errors import AgentLoopLimitError
from services.orchestrator.planner.planner import create_plan
from services.orchestrator.state_graph.agent_state import AgentState
from services.orchestrator.state_graph.executor import run_plan
from services.orchestrator.tools.registry_instance import default_registry

router = APIRouter(prefix="/tasks", tags=["runs"])


def _status_from_state(state: AgentState) -> str:
    if state.approval_status == "pending":
        return "awaiting_approval"
    if state.errors:
        return "failed"
    return "completed"


def _to_run_result(task_id: str, state: AgentState) -> RunResult:
    return RunResult(
        run_id=f"run_{uuid4().hex[:12]}",
        task_id=task_id,
        status=_status_from_state(state),
        completed_steps=state.completed_steps,
        errors=[e.model_dump() for e in state.errors],
        evidence=[e.model_dump() for e in state.evidence],
        final_output=state.final_output,
    )


@router.post("/{task_id}/run", response_model=RunResult)
def run_task(task_id: str) -> RunResult:
    record = _TASKS.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="task not found")

    state: AgentState | None = record.get("state")
    if state is None:
        state = AgentState(task_id=task_id, user_id="demo-user", intent=record["intent"])
        state.plan = create_plan(task_id, record["intent"], file_path=record.get("demo_file_path"))

    try:
        state = run_plan(state, default_registry)
    except AgentLoopLimitError as exc:
        record["state"] = state
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    record["state"] = state
    return _to_run_result(task_id, state)


@router.post("/{task_id}/approve", response_model=RunResult)
def approve_task(task_id: str) -> RunResult:
    record = _TASKS.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="task not found")

    state: AgentState | None = record.get("state")
    if state is None or state.approval_status != "pending":
        raise HTTPException(
            status_code=409, detail="task has no step currently awaiting approval"
        )

    state.approval_status = "approved"
    try:
        state = run_plan(state, default_registry)
    except AgentLoopLimitError as exc:
        record["state"] = state
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    record["state"] = state
    return _to_run_result(task_id, state)


@router.get("/{task_id}/events")
def get_task_events(task_id: str) -> list[dict]:
    """Plain JSON list of the event log — see docs/api-contract.md. Not true SSE
    streaming yet (TODO Phase 11); this is the full log to date, polled or fetched
    once the run reaches a terminal/paused state."""
    record = _TASKS.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="task not found")

    state: AgentState | None = record.get("state")
    if state is None:
        return []
    return state.events
