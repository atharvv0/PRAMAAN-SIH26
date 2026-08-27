import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Text, TIMESTAMP, ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False
    )

    claim_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.document_id"),
        nullable=True
    )

    chunk_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.chunk_id"),
        nullable=True
    )

    model_call_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("model_calls.model_call_id"),
        nullable=True
    )

    confidence: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    validation_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'pending'")
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()")
    )