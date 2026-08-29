from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    Uuid,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from services.backend.app.core.config import settings


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Workspace(Base):
    __tablename__ = "workspaces"

    workspace_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    sensitivity_class: Mapped[str] = mapped_column(
        String(30),
        default="confidential",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workspaces.workspace_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey(
            "projects.project_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    intent: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
        nullable=False,
    )
    sensitivity_class: Mapped[str] = mapped_column(
        String(30),
        default="confidential",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class FileRecord(Base):
    __tablename__ = "files"

    file_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey(
            "projects.project_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    uploaded_by: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    sensitivity_class: Mapped[str] = mapped_column(
        String(30),
        default="confidential",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TaskFile(Base):
    __tablename__ = "task_files"

    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    file_id: Mapped[str] = mapped_column(
        ForeignKey(
            "files.file_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default="input",
        nullable=False,
    )


class TaskStep(Base):
    __tablename__ = "task_steps"

    step_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    step_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    step_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )
    input_ref: Mapped[dict | None] = mapped_column(JSON)
    output_ref: Mapped[dict | None] = mapped_column(JSON)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    error_message: Mapped[str | None] = mapped_column(Text)


class TaskRun(Base):
    __tablename__ = "task_runs"

    run_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
        nullable=False,
    )
    state_json: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Model(Base):
    __tablename__ = "models"

    model_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    provider_family: Mapped[str | None] = mapped_column(
        String(150)
    )
    runtime: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"

    model_version_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    model_id: Mapped[str] = mapped_column(
        ForeignKey(
            "models.model_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    weights_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    quantization: Mapped[str | None] = mapped_column(
        String(50)
    )

    # PostgreSQL column is NUMERIC, so the ORM must also use Numeric.
    vram_required_gb: Mapped[float | None] = mapped_column(
        Numeric(10, 2)
    )

    license: Mapped[str] = mapped_column(
        String(120),
        default="open-weight",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )


class ModelCall(Base):
    __tablename__ = "model_calls"

    model_call_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    model_version_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False)
    )
    purpose: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(30),
        default="success",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Tool(Base):
    __tablename__ = "tools"

    tool_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    tool_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ToolCall(Base):
    __tablename__ = "tool_calls"

    tool_call_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    tool_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tools.tool_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    agent_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    args_json: Mapped[dict | None] = mapped_column(JSON)
    result_json: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(
        String(30),
        default="started",
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    error_message: Mapped[str | None] = mapped_column(Text)


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    knowledge_base_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workspaces.workspace_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    knowledge_base_id: Mapped[str] = mapped_column(
        ForeignKey(
            "knowledge_bases.knowledge_base_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    file_id: Mapped[str] = mapped_column(
        ForeignKey("files.file_id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    version: Mapped[str | None] = mapped_column(
        String(50)
    )
    source_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="indexing",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    document_id: Mapped[str] = mapped_column(
        ForeignKey(
            "documents.document_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    page_no: Mapped[int | None] = mapped_column(
        Integer
    )
    region_json: Mapped[dict | None] = mapped_column(
        JSON
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    qdrant_point_id: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Evidence(Base):
    __tablename__ = "evidence_records"

    evidence_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    claim_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    document_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False)
    )
    chunk_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False)
    )
    model_call_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False)
    )
    confidence: Mapped[float | None] = mapped_column(
        Float
    )
    validation_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Approval(Base):
    __tablename__ = "approvals"

    approval_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    requested_from: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )
    decision: Mapped[str | None] = mapped_column(
        String(30)
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    comment: Mapped[str | None] = mapped_column(Text)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    audit_event_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    actor_type: Mapped[str] = mapped_column(
        String(30),
        default="user",
        nullable=False,
    )
    actor_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False)
    )
    action: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    target_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False)
    )
    decision: Mapped[str] = mapped_column(
        String(20),
        default="none",
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(
        Text
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Deliverable(Base):
    __tablename__ = "deliverables"

    deliverable_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    file_id: Mapped[str] = mapped_column(
        ForeignKey("files.file_id"),
        nullable=False,
    )
    format: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        String(50),
        default="1.0",
        nullable=False,
    )
    approval_state: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )


ENGINE = None


def get_engine():
    global ENGINE

    if ENGINE is None:
        ENGINE = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
        )

    return ENGINE


def init_db() -> None:
    engine = get_engine()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_user = session.scalar(
            select(User).where(
                User.email == "demo.operator@local"
            )
        )

        if seed_user is None:
            seed_user = User(
                email="demo.operator@local",
                display_name="Demo Operator",
            )
            session.add(seed_user)
            session.flush()

        ws = session.scalar(
            select(Workspace).where(
                Workspace.name
                == "PRAMAAN Sovereign Workspace"
            )
        )

        if ws is None:
            ws = Workspace(
                name="PRAMAAN Sovereign Workspace",
                description="Local sovereign workspace",
                sensitivity_class="confidential",
            )
            session.add(ws)
            session.flush()

        project = session.scalar(
            select(Project)
            .where(
                Project.workspace_id == ws.workspace_id
            )
            .limit(1)
        )

        if project is None:
            project = Project(
                workspace_id=ws.workspace_id,
                name="Industrial Workbench",
                description="Default PRAMAAN project",
            )
            session.add(project)

        session.commit()


def session_scope() -> Session:
    return Session(
        get_engine(),
        expire_on_commit=False,
    )


def iso(dt: datetime | None) -> str | None:
    return (
        dt.astimezone(timezone.utc).isoformat()
        if dt
        else None
    )


def seed_ids() -> tuple[str, str, str]:
    with session_scope() as session:
        user = session.scalar(
            select(User).where(
                User.email == "demo.operator@local"
            )
        )

        ws = session.scalar(
            select(Workspace).where(
                Workspace.name
                == "PRAMAAN Sovereign Workspace"
            )
        )

        project = session.scalar(
            select(Project)
            .where(
                Project.workspace_id
                == ws.workspace_id
            )
            .limit(1)
        )

        return (
            user.user_id,
            ws.workspace_id,
            project.project_id,
        )