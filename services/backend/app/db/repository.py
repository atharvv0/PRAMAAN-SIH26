from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import desc, select

from ..db.database import (
    Approval,
    AuditEvent,
    Deliverable,
    Evidence,
    FileRecord,
    Model as DBModel,
    ModelCall as DBModelCall,
    ModelVersion,
    Project,
    Task,
    TaskFile,
    TaskRun,
    TaskStep,
    Tool as DBTool,
    ToolCall as DBToolCall,
    User,
    Workspace,
    session_scope,
    iso,
)

UPLOAD_ROOT = Path(__file__).resolve().parents[4] / "data" / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


class Repository:
    def get_or_create_user(self, value):
        with session_scope() as s:
            raw = str(value).strip()
            try:
                user_id = UUID(raw)
            except (ValueError, TypeError, AttributeError):
                user_id = None

            if user_id is not None:
                user = s.get(User, str(user_id))
                if user:
                    return user

            email = raw.lower()
            user = s.scalar(select(User).where(User.email == email))
            if user:
                return user

            user = User(email=email, display_name=email.split("@")[0])
            s.add(user)
            s.commit()
            s.refresh(user)
            return user

    def get_user(self, value):
        """Backward-compatible alias; auto-provisions local users."""
        return self.get_or_create_user(value)

    def list_workspaces(self) -> list[dict]:
        with session_scope() as s:
            workspaces = s.scalars(
                select(Workspace).order_by(Workspace.name)
            ).all()

            result = []

            for ws in workspaces:
                active = s.scalar(
                    select(Task.task_id)
                    .join(Project, Project.project_id == Task.project_id)
                    .where(
                        Project.workspace_id == ws.workspace_id,
                        Task.status.in_(
                            ["queued", "running", "awaiting_approval"]
                        ),
                    )
                    .limit(1)
                )

                total_deliverables = s.scalar(
                    select(Deliverable.deliverable_id)
                    .join(Task, Task.task_id == Deliverable.task_id)
                    .join(Project, Project.project_id == Task.project_id)
                    .where(Project.workspace_id == ws.workspace_id)
                    .limit(1)
                )

                result.append(
                    {
                        "id": ws.workspace_id,
                        "name": ws.name,
                        "description": ws.description or "",
                        "documentCount": 0,
                        "activeTasks": 1 if active else 0,
                        "pendingApprovals": 0,
                        "deliverableCount": 1 if total_deliverables else 0,
                        "updatedAt": iso(ws.created_at),
                    }
                )

            return result

    def resolve_workspace_project(
        self, workspace_id: str
    ) -> tuple[Workspace, Project]:
        with session_scope() as s:
            ws = s.get(Workspace, workspace_id) or s.scalar(
                select(Workspace).where(
                    Workspace.name == "PRAMAAN Sovereign Workspace"
                )
            )

            if ws is None:
                ws = Workspace(
                    name="PRAMAAN Sovereign Workspace",
                    description="Local sovereign workspace",
                )
                s.add(ws)
                s.flush()

            project = s.scalar(
                select(Project)
                .where(Project.workspace_id == ws.workspace_id)
                .limit(1)
            )

            if project is None:
                project = Project(
                    workspace_id=ws.workspace_id,
                    name="Industrial Workbench",
                    description="Default PRAMAAN project",
                )
                s.add(project)
                s.flush()

            s.commit()
            s.refresh(ws)
            s.refresh(project)

            return ws, project

    def save_upload(
        self,
        filename: str,
        content: bytes,
        mime: str,
        uploaded_by: str,
        workspace_id: str,
    ) -> dict:
        user = self.get_user(uploaded_by)

        if user is None:
            raise ValueError(
                f"User not found for uploaded_by={uploaded_by!r}"
            )

        ws, project = self.resolve_workspace_project(workspace_id)

        file_id = str(uuid4())

        path = UPLOAD_ROOT / f"{file_id}_{Path(filename).name}"
        path.write_bytes(content)

        with session_scope() as s:
            record = FileRecord(
                file_id=file_id,
                project_id=project.project_id,
                uploaded_by=user.user_id,
                filename=filename,
                mime_type=mime or "application/octet-stream",
                size_bytes=len(content),
                storage_path=str(path),
                sha256=hashlib.sha256(content).hexdigest(),
            )

            s.add(record)
            s.commit()

        return {
            "id": file_id,
            "name": filename,
            "type": mime or "other",
            "sizeBytes": len(content),
            "status": "queued",
            "localProcessing": True,
            "path": str(path),
        }

    def create_task(
        self,
        title: str,
        intent: str,
        workspace_id: str,
        created_by: str,
        sensitivity: str,
        file_ids: list[str],
    ) -> dict:
        user = self.get_user(created_by)

        if user is None:
            raise ValueError(
                f"User not found for created_by={created_by!r}"
            )

        ws, project = self.resolve_workspace_project(workspace_id)

        with session_scope() as s:
            task = Task(
                project_id=project.project_id,
                created_by=user.user_id,
                title=title,
                intent=intent,
                status="queued",
                sensitivity_class=sensitivity,
            )

            s.add(task)
            s.flush()

            for fid in file_ids:
                if s.get(FileRecord, fid):
                    s.add(
                        TaskFile(
                            task_id=task.task_id,
                            file_id=fid,
                            role="input",
                        )
                    )

            run = TaskRun(
                task_id=task.task_id,
                status="queued",
                state_json={
                    "task_id": task.task_id,
                    "user_id": user.user_id,
                    "intent": intent,
                    "files": file_ids,
                },
            )

            s.add(run)
            s.commit()
            s.refresh(task)
            s.refresh(run)

        self.add_audit(
            user.user_id,
            "task.created",
            "task",
            task.task_id,
            "allow",
            "Task created locally.",
        )

        with session_scope() as s:
            return self.task_payload(
                s,
                s.get(Task, task.task_id),
                s.get(Workspace, ws.workspace_id),
            )

    def task_payload(self, s, task: Task, ws: Workspace) -> dict:
        files = s.scalars(
            select(FileRecord)
            .join(TaskFile, TaskFile.file_id == FileRecord.file_id)
            .where(TaskFile.task_id == task.task_id)
        ).all()

        run = s.scalar(
            select(TaskRun).where(TaskRun.task_id == task.task_id)
        )

        return {
            "task_id": str(task.task_id),
            "id": str(task.task_id),
            "status": task.status,
            "title": task.title,
            "instruction": task.intent,
            "workspaceId": str(ws.workspace_id),
            "workspaceName": ws.name,
            "progress": self.progress(s, task.task_id),
            "currentStep": "TASK CREATED",
            "createdBy": s.get(User, task.created_by).email,
            "createdAt": iso(task.created_at),
            "updatedAt": iso(task.updated_at),
            "elapsedMs": 0,
            "files": [
                {
                    "id": str(f.file_id),
                    "name": f.filename,
                    "type": f.mime_type,
                    "sizeBytes": f.size_bytes,
                    "status": "queued",
                    "localProcessing": True,
                }
                for f in files
            ],
            "runId": str(run.run_id) if run else None,
        }

    def list_tasks(
        self, workspace_id: str | None = None, user_id: str | None = None
    ) -> list[dict]:
        with session_scope() as s:
            q = select(Task).order_by(desc(Task.updated_at))

            if user_id:
                q = q.where(Task.created_by == user_id)

            if workspace_id:
                q = (
                    q.join(Project, Project.project_id == Task.project_id)
                    .where(Project.workspace_id == workspace_id)
                )

            out = []

            for t in s.scalars(q).all():
                ws = s.scalar(
                    select(Workspace)
                    .join(Project, Project.workspace_id == Workspace.workspace_id)
                    .where(Project.project_id == t.project_id)
                )

                out.append(self.task_payload(s, t, ws))

            return out

    def get_task_for_user(self, task_id: str, user_id: str) -> dict | None:
        with session_scope() as s:
            task = s.scalar(
                select(Task).where(
                    Task.task_id == task_id,
                    Task.created_by == user_id,
                )
            )
            if not task:
                return None
            ws = s.scalar(
                select(Workspace)
                .join(Project, Project.workspace_id == Workspace.workspace_id)
                .where(Project.project_id == task.project_id)
            )
            return self.task_payload(s, task, ws)

    def get_task(self, task_id: str) -> dict | None:
        with session_scope() as s:
            task = s.get(Task, task_id)

            if not task:
                return None

            ws = s.scalar(
                select(Workspace)
                .join(Project, Project.workspace_id == Workspace.workspace_id)
                .where(Project.project_id == task.project_id)
            )

            return self.task_payload(s, task, ws)

    def get_state(self, task_id: str):
        with session_scope() as s:
            t = s.get(Task, task_id)
            r = s.scalar(
                select(TaskRun).where(TaskRun.task_id == task_id)
            )

            return (t, r) if t and r else None

    def update_run(
        self, task_id: str, state: dict, status: str
    ) -> None:
        with session_scope() as s:
            run = s.scalar(
                select(TaskRun).where(TaskRun.task_id == task_id)
            )
            task = s.get(Task, task_id)

            if run:
                run.state_json = state
                run.status = status
                run.updated_at = datetime.now(timezone.utc)

            if task:
                task.status = status
                task.updated_at = datetime.now(timezone.utc)

            s.commit()

        self.persist_state_artifacts(state)

    def persist_state_artifacts(self, state: dict) -> None:
        task_id = state["task_id"]

        with session_scope() as s:
            s.query(TaskStep).filter(
                TaskStep.task_id == task_id
            ).delete(synchronize_session=False)

            for no, step in enumerate(
                (state.get("plan") or {}).get("steps", []), 1
            ):
                s.add(
                    TaskStep(
                        step_id=str(uuid4()),
                        task_id=task_id,
                        step_no=no,
                        step_type=step.get(
                            "capability", "unknown"
                        ),
                        status=step.get("status", "pending"),
                        input_ref={
                            "plan_step_id": step.get("id"),
                            **(step.get("inputs") or {}),
                        },
                        output_ref=None,
                    )
                )

            s.query(DBToolCall).filter(
                DBToolCall.task_id == task_id
            ).delete(synchronize_session=False)

            for call in state.get("tool_calls", []):
                tool_id = self.ensure_tool_id(
                    s,
                    call.get("tool_id", "unknown"),
                )

                s.add(
                    DBToolCall(
                        task_id=task_id,
                        tool_id=tool_id,
                        agent_name="pramaan-agent",
                        args_json=call.get("inputs") or {},
                        result_json=call.get("output"),
                        status=(
                            "failed"
                            if call.get("error")
                            else "completed"
                        ),
                        error_message=call.get("error"),
                    )
                )

            s.query(DBModelCall).filter(
                DBModelCall.task_id == task_id
            ).delete(synchronize_session=False)

            for call in state.get("model_calls", []):
                mv = self.ensure_model_version(
                    s,
                    call.get("model_id", "unknown"),
                )

                s.add(
                    DBModelCall(
                        task_id=task_id,
                        model_version_id=mv,
                        purpose=call.get("purpose", "unknown"),
                        input_tokens=call.get("input_tokens"),
                        output_tokens=call.get("output_tokens"),
                        latency_ms=call.get("latency_ms"),
                        status="success",
                    )
                )

            s.query(Evidence).filter(
                Evidence.task_id == task_id
            ).delete(synchronize_session=False)

            for ev in state.get("evidence", []):
                s.add(
                    Evidence(
                        task_id=task_id,
                        claim_text=ev.get("claim", "") or "",
                        confidence=ev.get("confidence"),
                        validation_status=ev.get(
                            "validation_state", "pending"
                        ),
                    )
                )

            s.commit()

    def ensure_tool_id(self, s, tool_name: str) -> str:
        existing = s.scalar(
            select(DBTool).where(DBTool.name == tool_name)
        )

        if existing:
            return existing.tool_id

        obj = DBTool(
            name=tool_name,
            tool_type="agent_tool",
            status="active",
        )

        s.add(obj)
        s.flush()

        return obj.tool_id

    def ensure_model_version(
        self, s, model_name: str
    ) -> str:
        mv = s.scalar(
            select(ModelVersion).where(
                ModelVersion.version == model_name
            )
        )

        if mv:
            return mv.model_version_id

        m = s.scalar(
            select(DBModel).where(DBModel.name == model_name)
        )

        if m is None:
            m = DBModel(
                name=model_name,
                provider_family="ollama",
                runtime="ollama",
                status="active",
            )

            s.add(m)
            s.flush()

        mv = ModelVersion(
            model_id=m.model_id,
            version=model_name,
            weights_path="ollama://" + model_name,
            license="open-weight",
            status="active",
        )

        s.add(mv)
        s.flush()

        return mv.model_version_id

    def get_file_for_user(self, file_id: str, user_id: str):
        with session_scope() as s:
            return s.scalar(
                select(FileRecord).where(
                    FileRecord.file_id == file_id,
                    FileRecord.uploaded_by == user_id,
                )
            )

    def get_task_owner(self, task_id: str):
        with session_scope() as s:
            return s.scalar(select(Task.created_by).where(Task.task_id == task_id))

    def get_run_owner(self, run_id: str):
        with session_scope() as s:
            return s.scalar(
                select(Task.created_by)
                .join(TaskRun, TaskRun.task_id == Task.task_id)
                .where(TaskRun.run_id == run_id)
            )

    def file_path_for_task(
        self, task_id: str
    ) -> str | None:
        with session_scope() as s:
            f = s.scalar(
                select(FileRecord)
                .join(
                    TaskFile,
                    TaskFile.file_id == FileRecord.file_id,
                )
                .where(TaskFile.task_id == task_id)
                .order_by(FileRecord.created_at)
                .limit(1)
            )

            return f.storage_path if f else None

    def files_for_task(
        self, task_id: str
    ) -> list[dict]:
        with session_scope() as s:
            fs = s.scalars(
                select(FileRecord)
                .join(
                    TaskFile,
                    TaskFile.file_id == FileRecord.file_id,
                )
                .where(TaskFile.task_id == task_id)
            ).all()

            return [
                {
                    "id": str(f.file_id),
                    "name": f.filename,
                    "path": f.storage_path,
                    "mime": f.mime_type,
                }
                for f in fs
            ]

    def add_audit(
        self,
        actor_id: str | None,
        action: str,
        target_type: str,
        target_id: str | None,
        decision: str,
        reason: str | None,
    ) -> dict:
        with session_scope() as s:
            resolved_actor = None
            actor_label = actor_id or "system"

            if actor_id:
                try:
                    UUID(str(actor_id))
                    resolved_actor = str(actor_id)

                except (
                    ValueError,
                    TypeError,
                    AttributeError,
                ):
                    user = s.scalar(
                        select(User).where(User.email == actor_id)
                    )

                    if user is not None:
                        resolved_actor = str(user.user_id)

                    else:
                        user = User(
                            email=(
                                actor_id
                                if "@" in actor_id
                                else f"{actor_id}@local"
                            ),
                            display_name=str(actor_id).split("@")[0],
                        )

                        s.add(user)
                        s.flush()

                        resolved_actor = str(user.user_id)

            e = AuditEvent(
                actor_id=resolved_actor,
                action=action,
                target_type=target_type,
                target_id=target_id,
                decision=decision,
                reason=reason,
            )

            s.add(e)
            s.commit()
            s.refresh(e)

            return {
                "id": str(e.audit_event_id),
                "timestamp": iso(e.created_at),
                "actor": actor_label,
                "action": action,
                "targetType": target_type,
                "targetId": target_id,
                "decision": decision,
                "reason": reason,
                "eventType": target_type,
            }

    def approvals(self, user_id: str | None = None) -> list[dict]:
        return self.approval_rows(user_id)

    def audits(
        self, task_id: str | None = None
    ) -> list[dict]:
        with session_scope() as s:
            q = select(AuditEvent).order_by(
                desc(AuditEvent.created_at)
            )

            if task_id:
                q = q.where(
                    (AuditEvent.target_id == task_id)
                    | (AuditEvent.actor_id == task_id)
                )

            return [
                {
                    "id": str(e.audit_event_id),
                    "timestamp": iso(e.created_at),
                    "actor": e.actor_id or "system",
                    "action": e.action,
                    "targetType": e.target_type,
                    "targetId": e.target_id,
                    "decision": e.decision,
                    "reason": e.reason,
                    "eventType": e.target_type,
                }
                for e in s.scalars(q).all()
            ]

    def persisted_evidence(
        self, task_id: str | None = None, user_id: str | None = None
    ) -> list[dict]:
        with session_scope() as s:
            q = select(TaskRun).order_by(
                desc(TaskRun.updated_at)
            )

            if task_id:
                q = q.where(TaskRun.task_id == task_id)

            if user_id:
                q = q.join(Task, Task.task_id == TaskRun.task_id).where(Task.created_by == user_id)

            out = []

            for run in s.scalars(q).all():
                state = run.state_json or {}

                for i, ev in enumerate(
                    state.get("evidence", []), 1
                ):
                    source = str(ev.get("source", "local"))

                    matched = next(
                        (
                            f
                            for f in self.files_for_task(
                                str(run.task_id)
                            )
                            if Path(f["path"]).name
                            == Path(source).name
                            or Path(f["path"]).name in source
                        ),
                        None,
                    )

                    page_region = str(
                        ev.get("page_or_region", "1")
                    )

                    page_region_clean = page_region.replace(
                        "page_", ""
                    )

                    page = (
                        int(page_region_clean)
                        if page_region_clean.isdigit()
                        else 1
                    )

                    out.append(
                        {
                            "id": f"ev-{run.task_id}-{i}",
                            "taskId": str(run.task_id),
                            "runId": str(run.run_id),
                            "claim": ev.get("claim", ""),
                            "sourceDocument": (
                                Path(source).name
                                if source
                                else "local"
                            ),
                            "sourceUrl": (
                                f"/api/v1/files/{matched['id']}/download"
                                if matched
                                else None
                            ),
                            "page": page,
                            "region": {
                                "x": 0,
                                "y": 0,
                                "w": 1,
                                "h": 1,
                            },
                            "extractedText": ev.get(
                                "claim", ""
                            ),
                            "confidence": float(
                                ev.get("confidence") or 0
                            ),
                            "validationStatus": (
                                "validated"
                                if ev.get("validation_state")
                                == "validated"
                                else "pending"
                            ),
                            "modelId": ev.get("model"),
                            "toolId": ev.get("tool"),
                            "createdAt": iso(
                                run.updated_at
                            ),
                        }
                    )

            return out

    def evidence(
        self, task_id: str | None = None, user_id: str | None = None
    ) -> list[dict]:
        return self.persisted_evidence(task_id, user_id)

    def get_run(self, run_id: str):
        with session_scope() as s:
            run = s.get(TaskRun, run_id)
            return run.state_json if run else None

    def approval_rows(self, user_id: str | None = None) -> list[dict]:
        with session_scope() as s:
            q = select(Approval).where(Approval.status == "pending")
            if user_id:
                q = q.join(Task, Task.task_id == Approval.task_id).where(Task.created_by == user_id)
            rows = s.scalars(q).all()

            out = []

            for a in rows:
                t = s.get(Task, a.task_id)

                out.append(
                    {
                        "id": str(a.approval_id),
                        "deliverableId": str(a.approval_id),
                        "taskId": str(a.task_id),
                        "taskTitle": (
                            t.title
                            if t
                            else str(a.task_id)
                        ),
                        "name": "Approval Note",
                        "type": "docx",
                        "createdAt": iso(
                            t.created_at
                            if t
                            else a.decided_at
                        ),
                        "status": "approval_required",
                        "approvalStatus": "pending",
                        "evidenceCount": len(
                            self.persisted_evidence(
                                str(a.task_id)
                            )
                        ),
                        "provenanceSummary": (
                            "Human approval is required "
                            "before finalisation."
                        ),
                    }
                )

            return out

    def ensure_pending_approval(
        self,
        task_id: str,
        requested_from: str,
    ) -> str:
        user = self.get_user(requested_from)

        if user is None:
            raise ValueError(
                f"User not found for requested_from={requested_from!r}"
            )

        with session_scope() as s:
            existing = s.scalar(
                select(Approval).where(
                    Approval.task_id == task_id,
                    Approval.status == "pending",
                )
            )

            if existing:
                return str(existing.approval_id)

            a = Approval(
                task_id=task_id,
                requested_from=user.user_id,
                status="pending",
            )

            s.add(a)
            s.commit()
            s.refresh(a)

            return str(a.approval_id)

    def set_approval(
        self,
        task_id: str,
        decision: str,
        actor: str,
        comment: str | None = None,
    ) -> None:
        user = self.get_user(actor)

        if user is None:
            raise ValueError(
                f"User not found for actor={actor!r}"
            )

        with session_scope() as s:
            a = s.scalar(
                select(Approval).where(
                    Approval.task_id == task_id,
                    Approval.status == "pending",
                )
            )

            if a:
                a.status = (
                    "approved"
                    if decision == "approved"
                    else decision
                )
                a.decision = decision
                a.decided_at = datetime.now(timezone.utc)
                a.comment = comment

            else:
                s.add(
                    Approval(
                        task_id=task_id,
                        requested_from=user.user_id,
                        status=(
                            "approved"
                            if decision == "approved"
                            else decision
                        ),
                        decision=decision,
                        decided_at=datetime.now(timezone.utc),
                        comment=comment,
                    )
                )

            s.commit()

    def deliverables(
        self, task_id: str | None = None, user_id: str | None = None
    ) -> list[dict]:
        with session_scope() as s:
            q = select(Deliverable)

            if task_id:
                q = q.where(Deliverable.task_id == task_id)

            if user_id:
                q = (
                    q.join(Task, Task.task_id == Deliverable.task_id)
                    .where(Task.created_by == user_id)
                )

            out = []

            for d in s.scalars(q).all():
                t = s.get(Task, d.task_id)
                f = s.get(FileRecord, d.file_id)

                out.append(
                    {
                        "id": str(d.deliverable_id),
                        "name": (
                            f.filename
                            if f
                            else "Deliverable"
                        ),
                        "type": d.format,
                        "taskId": str(d.task_id),
                        "taskTitle": (
                            t.title
                            if t
                            else str(d.task_id)
                        ),
                        "createdAt": (
                            iso(t.created_at)
                            if t
                            else iso(
                                datetime.now(
                                    timezone.utc
                                )
                            )
                        ),
                        "status": (
                            "completed"
                            if d.approval_state == "approved"
                            else "approval_required"
                        ),
                        "approvalStatus": d.approval_state,
                        "evidenceCount": len(
                            self.persisted_evidence(
                                str(d.task_id)
                            )
                        ),
                        "provenanceSummary": (
                            "Generated locally from "
                            "the agent run with "
                            "evidence and audit trace."
                        ),
                        "downloadUrl": (
                            f"/api/v1/files/{d.file_id}/download"
                            if f
                            else None
                        ),
                    }
                )

            return out

    def create_deliverable(
        self,
        task_id: str,
        file_id: str,
        fmt: str,
        approval_state: str,
    ) -> str:
        with session_scope() as s:
            existing = s.scalar(
                select(Deliverable).where(
                    Deliverable.task_id == task_id,
                    Deliverable.file_id == file_id,
                )
            )

            if existing:
                existing.format = fmt
                existing.approval_state = approval_state
                s.commit()
                return str(existing.deliverable_id)

            d = Deliverable(
                task_id=task_id,
                file_id=file_id,
                format=fmt,
                approval_state=approval_state,
            )

            s.add(d)
            s.commit()
            s.refresh(d)

            return str(d.deliverable_id)

    def has_deliverable(
        self, task_id: str
    ) -> bool:
        with session_scope() as s:
            return (
                s.scalar(
                    select(Deliverable.deliverable_id).where(
                        Deliverable.task_id == task_id
                    )
                )
                is not None
            )

    def set_task_status(
        self,
        task_id: str,
        status: str,
    ) -> None:
        with session_scope() as s:
            t = s.get(Task, task_id)

            if t:
                t.status = status
                t.updated_at = datetime.now(
                    timezone.utc
                )
                s.commit()

    def approve_deliverable(
        self,
        task_id: str,
        approved: bool,
    ):
        with session_scope() as s:
            d = s.scalar(
                select(Deliverable).where(
                    Deliverable.task_id == task_id
                )
            )

            if d:
                d.approval_state = (
                    "approved"
                    if approved
                    else "rejected"
                )
                s.commit()

    @staticmethod
    def progress(s, task_id):
        steps = s.scalars(
            select(TaskStep).where(
                TaskStep.task_id == task_id
            )
        ).all()

        return (
            int(
                sum(x.status == "done" for x in steps)
                / len(steps)
                * 100
            )
            if steps
            else 0
        )


repo = Repository()