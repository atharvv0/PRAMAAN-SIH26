import uuid

from sqlalchemy import (
    String,
    ForeignKey,
    text as sql_text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TaskFile(Base):
    __tablename__ = "task_files"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tasks.task_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "files.file_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=sql_text("'input'"),
    )