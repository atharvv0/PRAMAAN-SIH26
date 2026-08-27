from sqlalchemy.orm import Session

from app.repositories.workspace_repository import (
    create_workspace,
    get_workspace,
    get_workspaces,
    update_workspace,
    delete_workspace,
)


VALID_SENSITIVITY_CLASSES = {
    "public",
    "internal",
    "confidential",
    "restricted",
}


def create_workspace_service(
    db: Session,
    name: str,
    description: str = None,
    sensitivity_class: str = "confidential",
):
    if not name or not name.strip():
        raise ValueError("Workspace name is required.")

    if sensitivity_class not in VALID_SENSITIVITY_CLASSES:
        raise ValueError(
            "Invalid sensitivity class."
        )

    return create_workspace(
        db=db,
        name=name.strip(),
        description=(
            description.strip()
            if description is not None
            else None
        ),
        sensitivity_class=sensitivity_class,
    )


def get_workspace_service(
    db: Session,
    workspace_id,
):
    workspace = get_workspace(
        db,
        workspace_id,
    )

    if workspace is None:
        raise ValueError("Workspace not found.")

    return workspace


def get_workspaces_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_workspaces(
        db,
        limit=limit,
    )


def update_workspace_service(
    db: Session,
    workspace_id,
    name: str = None,
    description: str = None,
    sensitivity_class: str = None,
):
    if name is not None and not name.strip():
        raise ValueError(
            "Workspace name cannot be empty."
        )

    if (
        sensitivity_class is not None
        and sensitivity_class not in VALID_SENSITIVITY_CLASSES
    ):
        raise ValueError(
            "Invalid sensitivity class."
        )

    workspace = update_workspace(
        db=db,
        workspace_id=workspace_id,
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
        sensitivity_class=sensitivity_class,
    )

    if workspace is None:
        raise ValueError("Workspace not found.")

    return workspace


def delete_workspace_service(
    db: Session,
    workspace_id,
):
    deleted = delete_workspace(
        db,
        workspace_id,
    )

    if not deleted:
        raise ValueError("Workspace not found.")

    return True