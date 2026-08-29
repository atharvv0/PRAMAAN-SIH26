from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from services.backend.app.db.repository import repo
from services.knowledge.rag.runtime import get_retriever

router=APIRouter(prefix="/files",tags=["files"])

@router.post("/upload")
async def upload_file(file:UploadFile=File(...), createdBy:str=Form("demo.operator@local"), workspaceId:str=Form("")):
    content=await file.read()
    if not content: raise HTTPException(status_code=422,detail="empty file")
    ws=workspaceId or (repo.list_workspaces()[0]["id"] if repo.list_workspaces() else "")
    if not ws: raise HTTPException(status_code=500,detail="no workspace available")
    result=repo.save_upload(file.filename or "upload",content,file.content_type or "application/octet-stream",createdBy,ws)
    # Index text-bearing documents into the same retriever used by the agent.
    try:
        get_retriever().ingest_file(result["path"], metadata={"file_id":result["id"],"workspace_id":ws})
    except Exception:
        # Binary/unsupported files (or a temporarily unavailable vector service)
        # remain valid uploads; the task can still use the file tool/VLM path.
        pass
    result.pop("path",None)
    return result

@router.get("/{file_id}/download")
def download_file(file_id:str):
    from ..db.database import FileRecord, session_scope

    with session_scope() as s:
        rec=s.get(FileRecord,file_id)
        if rec is None: raise HTTPException(status_code=404,detail="file not found")
        path=Path(rec.storage_path)
        if not path.exists(): raise HTTPException(status_code=404,detail="stored file not found")
        return FileResponse(path,media_type=rec.mime_type,filename=rec.filename)
