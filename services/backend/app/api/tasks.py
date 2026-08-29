from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.backend.app.db.repository import repo
from ..models.task import TaskCreateRequest, TaskResponse

router=APIRouter(prefix="/tasks",tags=["tasks"])

@router.post("",response_model=TaskResponse,status_code=201)
def create_task(payload:TaskCreateRequest)->TaskResponse:
    intent=payload.intent or payload.instruction or ""
    if not intent.strip(): raise HTTPException(status_code=422,detail="intent or instruction is required")
    title=payload.title or intent[:60] or "PRAMAAN Task"
    return repo.create_task(title,intent,payload.workspaceId or repo.list_workspaces()[0]["id"],payload.createdBy,payload.sensitivity,payload.file_ids)

@router.get("",response_model=list[TaskResponse])
def list_tasks(workspaceId:str|None=None)->list[TaskResponse]:
    return repo.list_tasks(workspaceId)

@router.get("/{task_id}",response_model=TaskResponse)
def get_task(task_id:str)->TaskResponse:
    item=repo.get_task(task_id)
    if item is None:raise HTTPException(status_code=404,detail="task not found")
    return item
