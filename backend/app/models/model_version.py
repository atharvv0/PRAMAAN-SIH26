import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Text, TIMESTAMP, ForeignKey, Numeric, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    __table_args__ = (
        UniqueConstraint(
            "model_id",
            "version",
            name="model_versions_model_id_version_key"
        ),
    )

    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("models.model_id", ondelete="CASCADE"),
        nullable=False
    )

    version: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    weights_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    quantization: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    vram_required_gb: Mapped[Optional[Decimal]] = mapped_column(
        Numeric,
        nullable=True
    )

    license: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )