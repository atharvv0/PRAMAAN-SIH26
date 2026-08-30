from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends
from fastapi.responses import FileResponse

from services.backend.app.core.auth import get_current_user
from services.backend.app.db.repository import repo
from services.knowledge.rag.runtime import get_retriever

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    createdBy: str | None = Form(None),
    workspaceId: str = Form(""),
    current_user=Depends(get_current_user),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="empty file")

    ws = workspaceId or (repo.list_workspaces()[0]["id"] if repo.list_workspaces() else "")
    if not ws:
        raise HTTPException(status_code=500, detail="no workspace available")

    # Never trust createdBy for authorization. The authenticated identity is
    # authoritative; createdBy is retained only for backward compatibility.
    result = repo.save_upload(
        file.filename or "upload",
        content,
        file.content_type or "application/octet-stream",
        current_user.user_id,
        ws,
    )

    try:
        indexed = get_retriever().ingest_file(
            result["path"],
            metadata={"file_id": result["id"], "workspace_id": ws, "user_id": current_user.user_id},
        )
        result["knowledgeIndexedChunks"] = indexed
    except Exception as exc:
        result["knowledgeIndexedChunks"] = 0
        result["knowledgeIndexError"] = str(exc)

    result.pop("path", None)
    return result


@router.get("/{file_id}/download")
def download_file(file_id: str, current_user=Depends(get_current_user)):
    from ..db.database import FileRecord, session_scope

    with session_scope() as s:
        rec = s.scalar(
            __import__("sqlalchemy").select(FileRecord).where(
                FileRecord.file_id == file_id,
                FileRecord.uploaded_by == current_user.user_id,
            )
        )
        role = str(getattr(current_user, "role", "operator")).lower()
        if rec is None:
            raise HTTPException(status_code=404, detail="file not found")
        if str(rec.uploaded_by) != str(current_user.user_id) and role not in {"reviewer", "admin"}:
            raise HTTPException(status_code=403, detail="not authorized for this file")
        path = Path(rec.storage_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="stored file not found")
        return FileResponse(path, media_type=rec.mime_type, filename=rec.filename)
