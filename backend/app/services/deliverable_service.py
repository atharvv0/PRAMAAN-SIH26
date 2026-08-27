from sqlalchemy.orm import Session

from app.repositories.deliverable_repository import (
    create_deliverable,
    get_deliverable,
    get_deliverables_by_task,
    get_deliverables_by_file,
    get_deliverables,
    update_deliverable,
    delete_deliverable,
)


VALID_APPROVAL_STATES = {
    "pending",
    "approved",
    "rejected",
}


def create_deliverable_service(
    db: Session,
    task_id,
    file_id,
    format: str,
    version: str,
    approval_state: str = "pending",
):
    if not format or not format.strip():
        raise ValueError(
            "Deliverable format is required."
        )

    if not version or not version.strip():
        raise ValueError(
            "Deliverable version is required."
        )

    if approval_state not in VALID_APPROVAL_STATES:
        raise ValueError(
            "Invalid approval state."
        )

    return create_deliverable(
        db=db,
        task_id=task_id,
        file_id=file_id,
        format=format.strip(),
        version=version.strip(),
        approval_state=approval_state,
    )


def get_deliverable_service(
    db: Session,
    deliverable_id,
):
    deliverable = get_deliverable(
        db,
        deliverable_id,
    )

    if deliverable is None:
        raise ValueError(
            "Deliverable not found."
        )

    return deliverable


def get_deliverables_by_task_service(
    db: Session,
    task_id,
):
    return get_deliverables_by_task(
        db,
        task_id,
    )


def get_deliverables_by_file_service(
    db: Session,
    file_id,
):
    return get_deliverables_by_file(
        db,
        file_id,
    )


def get_deliverables_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_deliverables(
        db,
        limit=limit,
    )


def update_deliverable_service(
    db: Session,
    deliverable_id,
    format: str = None,
    version: str = None,
    approval_state: str = None,
):
    if format is not None and not format.strip():
        raise ValueError(
            "Format cannot be empty."
        )

    if version is not None and not version.strip():
        raise ValueError(
            "Version cannot be empty."
        )

    if (
        approval_state is not None
        and approval_state not in VALID_APPROVAL_STATES
    ):
        raise ValueError(
            "Invalid approval state."
        )

    deliverable = update_deliverable(
        db=db,
        deliverable_id=deliverable_id,
        format=(
            format.strip()
            if format is not None
            else None
        ),
        version=(
            version.strip()
            if version is not None
            else None
        ),
        approval_state=approval_state,
    )

    if deliverable is None:
        raise ValueError(
            "Deliverable not found."
        )

    return deliverable


def delete_deliverable_service(
    db: Session,
    deliverable_id,
):
    deleted = delete_deliverable(
        db,
        deliverable_id,
    )

    if not deleted:
        raise ValueError(
            "Deliverable not found."
        )

    return True