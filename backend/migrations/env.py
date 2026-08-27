from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.db.session import Base

# Import ALL SQLAlchemy models so Alembic can detect them
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.task import Task
from app.models.file import File
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.task_file import TaskFile
from app.models.task_step import TaskStep

from app.models.tool import Tool
from app.models.model import Model
from app.models.model_version import ModelVersion
from app.models.model_capability import ModelCapability
from app.models.tool_call import ToolCall
from app.models.model_call import ModelCall

from app.models.evidence_record import EvidenceRecord
from app.models.approval import Approval
from app.models.deliverable import Deliverable
from app.models.audit_event import AuditEvent


# Alembic Config object
config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata used by Alembic autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.
    """

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()