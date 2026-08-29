from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException

from services.backend.app.db.repository import repo
from services.knowledge.rag.runtime import get_retriever
from ..models.task import TaskCreateRequest, TaskResponse

router=APIRouter(prefix="/tasks",tags=["tasks"])

@router.post("",response_model=TaskResponse,status_code=201)
def create_task(payload:TaskCreateRequest)->TaskResponse:
    intent=payload.intent or payload.instruction or ""
    if not intent.strip(): raise HTTPException(status_code=422,detail="intent or instruction is required")
    title=payload.title or intent[:60] or "PRAMAAN Task"
    workspace_id=payload.workspaceId or repo.list_workspaces()[0]["id"]
    file_ids=list(payload.file_ids)
    # demo_file_path lets a caller point at a file already on the local
    # filesystem (used by the test suite / local demos) without going
    # through the multipart /files/upload endpoint. This field previously
    # existed on the schema but was never read here, so it silently did
    # nothing -- the planner never saw a file_path for these tasks.
    if payload.demo_file_path:
        source=Path(payload.demo_file_path)
        if not source.is_file():
            raise HTTPException(status_code=422,detail=f"demo_file_path not found: {payload.demo_file_path}")
        mime=mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        uploaded=repo.save_upload(source.name,source.read_bytes(),mime,payload.createdBy,workspace_id)
        file_ids.append(uploaded["id"])
        try:
            # Mirror the real /files/upload path so knowledge.search can
            # find this file too, not just file.read/ocr.process.
            get_retriever().ingest_file(uploaded["path"],metadata={"file_id":uploaded["id"],"workspace_id":workspace_id})
        except Exception:
            pass
    return repo.create_task(title,intent,workspace_id,payload.createdBy,payload.sensitivity,file_ids)

@router.get("",response_model=list[TaskResponse])
def list_tasks(workspaceId:str|None=None)->list[TaskResponse]:
    return repo.list_tasks(workspaceId)

@router.get("/{task_id}",response_model=TaskResponse)
def get_task(task_id:str)->TaskResponse:
    item=repo.get_task(task_id)
    if item is None:raise HTTPException(status_code=404,detail="task not found")
    return item
