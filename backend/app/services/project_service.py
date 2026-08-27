from sqlalchemy.orm import Session

from app.repositories.project_repository import (
    create_project,
    get_project,
    get_projects,
    update_project,
    delete_project,
)


def create_project_service(
    db: Session,
    workspace_id,
    name: str,
    description: str = None,
):
    if not name or not name.strip():
        raise ValueError("Project name is required.")

    return create_project(
        db=db,
        workspace_id=workspace_id,
        name=name.strip(),
        description=description,
    )


def get_project_service(
    db: Session,
    project_id,
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise ValueError("Project not found.")

    return project


def get_projects_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_projects(
        db,
        limit=limit,
    )


def update_project_service(
    db: Session,
    project_id,
    name: str = None,
    description: str = None,
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise ValueError("Project not found.")

    if name is not None:
        if not name.strip():
            raise ValueError(
                "Project name cannot be empty."
            )

        name = name.strip()

    return update_project(
        db=db,
        project_id=project_id,
        name=name,
        description=description,
    )


def delete_project_service(
    db: Session,
    project_id,
):
    deleted = delete_project(
        db,
        project_id,
    )

    if not deleted:
        raise ValueError(
            "Project not found."
        )

    return True