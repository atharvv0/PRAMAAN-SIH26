import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    text as sql_text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ToolCall(Base):
    __tablename__ = "tool_calls"

    tool_call_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sql_text("gen_random_uuid()"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
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

    args_json: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    result_json: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )