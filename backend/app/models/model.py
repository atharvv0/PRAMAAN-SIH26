import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    TIMESTAMP,
    text as sql_text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Model(Base):
    __tablename__ = "models"

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sql_text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    provider_family: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    runtime: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("NOW()"),
    )