from sqlalchemy.orm import Session

from app.repositories.task_repository import (
    create_task,
    get_task,
    get_tasks_by_project,
    get_tasks_by_user,
    get_tasks,
    update_task,
    delete_task,
)


VALID_STATUSES = {
    "queued",
    "running",
    "completed",
    "failed",
    "cancelled",
}

VALID_SENSITIVITY_CLASSES = {
    "public",
    "internal",
    "confidential",
    "restricted",
}


def create_task_service(
    db: Session,
    project_id,
    created_by,
    title: str,
    intent: str,
):
    if not title or not title.strip():
        raise ValueError("Task title is required.")

    if not intent or not intent.strip():
        raise ValueError("Task intent is required.")

    return create_task(
        db=db,
        project_id=project_id,
        created_by=created_by,
        title=title.strip(),
        intent=intent.strip(),
    )


def get_task_service(
    db: Session,
    task_id,
):
    task = get_task(db, task_id)

    if task is None:
        raise ValueError("Task not found.")

    return task


def get_tasks_by_project_service(
    db: Session,
    project_id,
):
    return get_tasks_by_project(
        db,
        project_id,
    )


def get_tasks_by_user_service(
    db: Session,
    created_by,
):
    return get_tasks_by_user(
        db,
        created_by,
    )


def get_tasks_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_tasks(
        db,
        limit=limit,
    )


def update_task_service(
    db: Session,
    task_id,
    title: str = None,
    intent: str = None,
    status: str = None,
    sensitivity_class: str = None,
):
    if title is not None and not title.strip():
        raise ValueError(
            "Task title cannot be empty."
        )

    if intent is not None and not intent.strip():
        raise ValueError(
            "Task intent cannot be empty."
        )

    if status is not None and status not in VALID_STATUSES:
        raise ValueError(
            "Invalid task status."
        )

    if (
        sensitivity_class is not None
        and sensitivity_class not in VALID_SENSITIVITY_CLASSES
    ):
        raise ValueError(
            "Invalid sensitivity class."
        )

    task = update_task(
        db=db,
        task_id=task_id,
        title=title.strip() if title is not None else None,
        intent=intent.strip() if intent is not None else None,
        status=status,
        sensitivity_class=sensitivity_class,
    )

    if task is None:
        raise ValueError(
            "Task not found."
        )

    return task


def delete_task_service(
    db: Session,
    task_id,
):
    deleted = delete_task(
        db,
        task_id,
    )

    if not deleted:
        raise ValueError(
            "Task not found."
        )

    return True