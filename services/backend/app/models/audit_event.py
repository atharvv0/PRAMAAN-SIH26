import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    audit_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    actor_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    decision: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        server_default=text("'pending'"),
    )

    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )