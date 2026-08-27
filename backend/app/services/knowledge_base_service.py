from sqlalchemy.orm import Session

from app.repositories.knowledge_base_repository import (
    create_knowledge_base,
    get_knowledge_base,
    get_knowledge_bases_by_workspace,
    get_knowledge_bases,
    update_knowledge_base,
    delete_knowledge_base,
)


VALID_STATUSES = {
    "active",
    "inactive",
}


def create_knowledge_base_service(
    db: Session,
    workspace_id,
    name: str,
    description: str = None,
    status: str = "active",
):
    if not name or not name.strip():
        raise ValueError(
            "Knowledge base name is required."
        )

    if status not in VALID_STATUSES:
        raise ValueError(
            "Invalid knowledge base status."
        )

    return create_knowledge_base(
        db=db,
        workspace_id=workspace_id,
        name=name.strip(),
        description=(
            description.strip()
            if description is not None
            else None
        ),
        status=status,
    )


def get_knowledge_base_service(
    db: Session,
    knowledge_base_id,
):
    knowledge_base = get_knowledge_base(
        db,
        knowledge_base_id,
    )

    if knowledge_base is None:
        raise ValueError(
            "Knowledge base not found."
        )

    return knowledge_base


def get_knowledge_bases_by_workspace_service(
    db: Session,
    workspace_id,
):
    return get_knowledge_bases_by_workspace(
        db,
        workspace_id,
    )


def get_knowledge_bases_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_knowledge_bases(
        db,
        limit=limit,
    )


def update_knowledge_base_service(
    db: Session,
    knowledge_base_id,
    name: str = None,
    description: str = None,
    status: str = None,
):
    if name is not None and not name.strip():
        raise ValueError(
            "Knowledge base name cannot be empty."
        )

    if (
        status is not None
        and status not in VALID_STATUSES
    ):
        raise ValueError(
            "Invalid knowledge base status."
        )

    knowledge_base = update_knowledge_base(
        db=db,
        knowledge_base_id=knowledge_base_id,
        name=(
            name.strip()
            if name is not None
            else None
        ),
        description=(
            description.strip()
            if description is not None
            else None
        ),
        status=status,
    )

    if knowledge_base is None:
        raise ValueError(
            "Knowledge base not found."
        )

    return knowledge_base


def delete_knowledge_base_service(
    db: Session,
    knowledge_base_id,
):
    deleted = delete_knowledge_base(
        db,
        knowledge_base_id,
    )

    if not deleted:
        raise ValueError(
            "Knowledge base not found."
        )

    return True