from sqlalchemy.orm import Session

from app.models.deliverable import Deliverable


def create_deliverable(
    db: Session,
    task_id,
    file_id,
    format: str,
    version: str,
    approval_state: str = "pending",
):
    deliverable = Deliverable(
        task_id=task_id,
        file_id=file_id,
        format=format,
        version=version,
        approval_state=approval_state,
    )

    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)

    return deliverable


def get_deliverable(
    db: Session,
    deliverable_id,
):
    return (
        db.query(Deliverable)
        .filter(
            Deliverable.deliverable_id == deliverable_id
        )
        .first()
    )


def get_deliverables_by_task(
    db: Session,
    task_id,
):
    return (
        db.query(Deliverable)
        .filter(
            Deliverable.task_id == task_id
        )
        .all()
    )


def get_deliverables_by_file(
    db: Session,
    file_id,
):
    return (
        db.query(Deliverable)
        .filter(
            Deliverable.file_id == file_id
        )
        .all()
    )


def get_deliverables(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Deliverable)
        .limit(limit)
        .all()
    )


def update_deliverable(
    db: Session,
    deliverable_id,
    format: str = None,
    version: str = None,
    approval_state: str = None,
):
    deliverable = get_deliverable(
        db,
        deliverable_id,
    )

    if deliverable is None:
        return None

    if format is not None:
        deliverable.format = format

    if version is not None:
        deliverable.version = version

    if approval_state is not None:
        deliverable.approval_state = approval_state

    db.commit()
    db.refresh(deliverable)

    return deliverable


def delete_deliverable(
    db: Session,
    deliverable_id,
):
    deliverable = get_deliverable(
        db,
        deliverable_id,
    )

    if deliverable is None:
        return False

    db.delete(deliverable)
    db.commit()

    return True
    