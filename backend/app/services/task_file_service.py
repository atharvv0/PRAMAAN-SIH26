from sqlalchemy.orm import Session

from app.repositories.task_file_repository import (
    attach_file_to_task,
    get_task_file,
    get_files_for_task,
    get_tasks_for_file,
    update_task_file_role,
    detach_file_from_task,
)


VALID_ROLES = {
    "input",
    "output",
    "reference",
    "evidence",
}


def attach_file_to_task_service(
    db: Session,
    task_id,
    file_id,
    role: str = "input",
):
    if not role or not role.strip():
        raise ValueError(
            "File role is required."
        )

    role = role.strip()

    if role not in VALID_ROLES:
        raise ValueError(
            "Invalid task file role."
        )

    existing = get_task_file(
        db,
        task_id,
        file_id,
    )

    if existing is not None:
        raise ValueError(
            "This file is already attached to this task."
        )

    return attach_file_to_task(
        db=db,
        task_id=task_id,
        file_id=file_id,
        role=role,
    )


def get_task_file_service(
    db: Session,
    task_id,
    file_id,
):
    task_file = get_task_file(
        db,
        task_id,
        file_id,
    )

    if task_file is None:
        raise ValueError(
            "Task file relationship not found."
        )

    return task_file


def get_files_for_task_service(
    db: Session,
    task_id,
):
    return get_files_for_task(
        db,
        task_id,
    )


def get_tasks_for_file_service(
    db: Session,
    file_id,
):
    return get_tasks_for_file(
        db,
        file_id,
    )


def update_task_file_role_service(
    db: Session,
    task_id,
    file_id,
    role: str,
):
    if not role or not role.strip():
        raise ValueError(
            "File role is required."
        )

    role = role.strip()

    if role not in VALID_ROLES:
        raise ValueError(
            "Invalid task file role."
        )

    task_file = update_task_file_role(
        db=db,
        task_id=task_id,
        file_id=file_id,
        role=role,
    )

    if task_file is None:
        raise ValueError(
            "Task file relationship not found."
        )

    return task_file


def detach_file_from_task_service(
    db: Session,
    task_id,
    file_id,
):
    deleted = detach_file_from_task(
        db,
        task_id,
        file_id,
    )

    if not deleted:
        raise ValueError(
            "Task file relationship not found."
        )

    return True