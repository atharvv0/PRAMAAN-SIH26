"""
Run API — executes a task's agent loop synchronously and returns the result.
See docs/api-contract.md "POST /api/v1/tasks/{task_id}/run".

Phase 3 status: synchronous execution only (no background job, no event streaming
yet — see docs/api-contract.md "/runs/{run_id}/events", TODO Phase 11). Good enough
to prove the vertical slice: one instruction -> plan -> tool use -> completed result.
"""
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.api.tasks import _TASKS
from app.models.run import RunResult
from services.orchestrator.planner.planner import create_plan
from services.orchestrator.state_graph.agent_state import AgentState
from services.orchestrator.state_graph.executor import run_plan
from services.orchestrator.tools.registry_instance import default_registry

router = APIRouter(prefix="/tasks", tags=["runs"])


@router.post("/{task_id}/run", response_model=RunResult)
def run_task(task_id: str) -> RunResult:
    record = _TASKS.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="task not found")

    state = AgentState(task_id=task_id, user_id="demo-user", intent=record["intent"])
    state.plan = create_plan(task_id, record["intent"], file_path=record.get("demo_file_path"))

    # Any PramaanError subclass (AgentLoopLimitError, ModelUnavailableError, ...)
    # raised by run_plan is deliberately NOT caught here — it propagates to
    # app.main's pramaan_error_handler, which maps it to the shared error shape
    # (docs/api-contract.md "Error Shape") in one place instead of duplicating
    # that mapping in every endpoint.
    state = run_plan(state, default_registry)

    if state.approval_status == "pending":
        status = "awaiting_approval"
    elif state.errors:
        status = "failed"
    else:
        status = "completed"

    return RunResult(
        run_id=f"run_{uuid4().hex[:12]}",
        task_id=task_id,
        status=status,
        completed_steps=state.completed_steps,
        errors=[e.model_dump() for e in state.errors],
        evidence=[e.model_dump() for e in state.evidence],
        final_output=state.final_output,
    )
