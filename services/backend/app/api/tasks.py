"""
Task API — see docs/api-contract.md.

Phase 3 status: creation + run endpoints, in-memory store. Persistence moves to a
real repository (docs/agent-contract.md-compatible) in Phase 3 continuation once
coordinated with the data/persistence owner. Do not wire this to Postgres directly
from here — go through a repository interface, per the master prompt's "Database
Integration" rule.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.task import TaskCreateRequest, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

# TODO(Phase 3 continuation): replace with a real repository (Niraj's persistence
# layer / Postgres). Keyed by task_id -> {"response": TaskResponse, "intent": str,
# "demo_file_path": str | None}.
_TASKS: dict[str, dict] = {}


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreateRequest) -> TaskResponse:
    task = TaskResponse()
    _TASKS[task.task_id] = {
        "response": task,
        "intent": payload.intent,
        "demo_file_path": payload.demo_file_path,
    }
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> TaskResponse:
    record = _TASKS.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="task not found")
    return record["response"]
