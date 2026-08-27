import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, TIMESTAMP, ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ModelCapability(Base):
    __tablename__ = "model_capabilities"

    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "model_versions.model_version_id",
            ondelete="CASCADE"
        ),
        primary_key=True,
        nullable=False
    )

    capability: Mapped[str] = mapped_column(
        String(80),
        primary_key=True,
        nullable=False
    )

    score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()")
    )