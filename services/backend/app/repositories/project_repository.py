from sqlalchemy.orm import Session

from app.models.project import Project


def create_project(
    db: Session,
    workspace_id,
    name: str,
    description: str = None,
    status: str = "active",
) -> Project:

    project = Project(
        workspace_id=workspace_id,
        name=name,
        description=description,
        status=status,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_project(
    db: Session,
    project_id,
):
    return (
        db.query(Project)
        .filter(Project.project_id == project_id)
        .first()
    )


def get_projects_by_workspace(
    db: Session,
    workspace_id,
):
    return (
        db.query(Project)
        .filter(Project.workspace_id == workspace_id)
        .all()
    )


def get_projects(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Project)
        .limit(limit)
        .all()
    )


def update_project(
    db: Session,
    project_id,
    name: str = None,
    description: str = None,
    status: str = None,
):
    project = get_project(db, project_id)

    if project is None:
        return None

    if name is not None:
        project.name = name

    if description is not None:
        project.description = description

    if status is not None:
        project.status = status

    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project_id,
):
    project = get_project(db, project_id)

    if project is None:
        return False

    db.delete(project)
    db.commit()

    return True