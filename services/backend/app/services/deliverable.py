from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from docx import Document

from ..db.database import FileRecord, Project, Task, session_scope
from ..db.repository import UPLOAD_ROOT, repo


def generate_approval_note(task_id: str, title: str, intent: str, state: dict) -> dict:
    doc = Document()
    doc.add_heading("PRAMAAN Approval Note", level=0)
    doc.add_paragraph(title)
    doc.add_heading("Task Intent", level=1)
    doc.add_paragraph(intent)
    doc.add_heading("Execution Summary", level=1)
    completed = state.get("completed_steps", [])
    doc.add_paragraph(f"Completed steps: {len(completed)}")
    doc.add_heading("Evidence", level=1)
    evidence = state.get("evidence", [])
    if evidence:
        for item in evidence:
            p=doc.add_paragraph(style="List Bullet")
            p.add_run(item.get("claim", ""))
            src=item.get("source")
            if src:p.add_run(f" — source: {src}")
    else:
        doc.add_paragraph("No evidence records were captured in this run.")
    doc.add_heading("Final Output", level=1)
    final=state.get("final_output") or {}
    doc.add_paragraph(str(final)[:10000])
    doc.add_heading("Approval", level=1)
    doc.add_paragraph("Human approval is required before release of the final deliverable.")
    path = UPLOAD_ROOT / f"{uuid4()}_Approval_Note.docx"
    doc.save(path)
    data=path.read_bytes()
    # Reuse repository's project lookup and create a file row.
    with session_scope() as s:
        task_row = s.get(Task, task_id)
        user_id = task_row.created_by
        project_id = task_row.project_id
        rec=FileRecord(file_id=str(uuid4()),project_id=project_id,uploaded_by=user_id,filename=path.name,mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",size_bytes=len(data),storage_path=str(path),sha256=__import__('hashlib').sha256(data).hexdigest(),sensitivity_class=task_row.sensitivity_class)
        s.add(rec); s.commit(); s.refresh(rec)
        repo.create_deliverable(task_id,rec.file_id,"docx","pending")
        return {"file_id":rec.file_id,"name":rec.filename}
