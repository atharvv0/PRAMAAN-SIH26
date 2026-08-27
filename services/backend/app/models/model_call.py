import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, TIMESTAMP, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ModelCall(Base):
    __tablename__ = "model_calls"

    model_call_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False
    )

    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "model_versions.model_version_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    input_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    output_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()")
    )