from sqlalchemy.orm import Session

from app.models.workspace import Workspace


def create_workspace(
    db: Session,
    name: str,
    description: str = None,
    sensitivity_class: str = "confidential",
) -> Workspace:

    workspace = Workspace(
        name=name,
        description=description,
        sensitivity_class=sensitivity_class,
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return workspace


def get_workspace(
    db: Session,
    workspace_id,
):
    return (
        db.query(Workspace)
        .filter(Workspace.workspace_id == workspace_id)
        .first()
    )


def get_workspaces(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Workspace)
        .limit(limit)
        .all()
    )


def update_workspace(
    db: Session,
    workspace_id,
    name: str = None,
    description: str = None,
    sensitivity_class: str = None,
):
    workspace = get_workspace(db, workspace_id)

    if workspace is None:
        return None

    if name is not None:
        workspace.name = name

    if description is not None:
        workspace.description = description

    if sensitivity_class is not None:
        workspace.sensitivity_class = sensitivity_class

    db.commit()
    db.refresh(workspace)

    return workspace


def delete_workspace(
    db: Session,
    workspace_id,
):
    workspace = get_workspace(db, workspace_id)

    if workspace is None:
        return False

    db.delete(workspace)
    db.commit()

    return True