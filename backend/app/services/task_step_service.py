from sqlalchemy.orm import Session

from app.repositories.task_step_repository import (
    create_task_step,
    get_task_step,
    get_task_steps_by_task,
    get_task_step_by_number,
    get_task_steps,
    update_task_step,
    start_task_step,
    complete_task_step,
    fail_task_step,
    delete_task_step,
)


VALID_STATUSES = {
    "pending",
    "running",
    "completed",
    "failed",
    "cancelled",
}


def create_task_step_service(
    db: Session,
    task_id,
    step_no: int,
    step_type: str,
    status: str = "pending",
    input_ref: dict = None,
    output_ref: dict = None,
):
    if step_no is None:
        raise ValueError(
            "Step number is required."
        )

    if step_no <= 0:
        raise ValueError(
            "Step number must be greater than 0."
        )

    if not step_type or not step_type.strip():
        raise ValueError(
            "Step type is required."
        )

    if status not in VALID_STATUSES:
        raise ValueError(
            "Invalid task step status."
        )

    existing = get_task_step_by_number(
        db,
        task_id,
        step_no,
    )

    if existing is not None:
        raise ValueError(
            "This step number already exists for this task."
        )

    return create_task_step(
        db=db,
        task_id=task_id,
        step_no=step_no,
        step_type=step_type.strip(),
        status=status,
        input_ref=input_ref,
        output_ref=output_ref,
    )


def get_task_step_service(
    db: Session,
    step_id,
):
    task_step = get_task_step(
        db,
        step_id,
    )

    if task_step is None:
        raise ValueError(
            "Task step not found."
        )

    return task_step


def get_task_steps_by_task_service(
    db: Session,
    task_id,
):
    return get_task_steps_by_task(
        db,
        task_id,
    )


def get_task_step_by_number_service(
    db: Session,
    task_id,
    step_no: int,
):
    if step_no is None or step_no <= 0:
        raise ValueError(
            "Step number must be greater than 0."
        )

    task_step = get_task_step_by_number(
        db,
        task_id,
        step_no,
    )

    if task_step is None:
        raise ValueError(
            "Task step not found."
        )

    return task_step


def get_task_steps_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_task_steps(
        db,
        limit=limit,
    )


def update_task_step_service(
    db: Session,
    step_id,
    step_no: int = None,
    step_type: str = None,
    status: str = None,
    input_ref: dict = None,
    output_ref: dict = None,
    started_at=None,
    completed_at=None,
    error_message: str = None,
):
    if step_no is not None and step_no <= 0:
        raise ValueError(
            "Step number must be greater than 0."
        )

    if step_type is not None and not step_type.strip():
        raise ValueError(
            "Step type cannot be empty."
        )

    if status is not None and status not in VALID_STATUSES:
        raise ValueError(
            "Invalid task step status."
        )

    task_step = update_task_step(
        db=db,
        step_id=step_id,
        step_no=step_no,
        step_type=(
            step_type.strip()
            if step_type is not None
            else None
        ),
        status=status,
        input_ref=input_ref,
        output_ref=output_ref,
        started_at=started_at,
        completed_at=completed_at,
        error_message=error_message,
    )

    if task_step is None:
        raise ValueError(
            "Task step not found."
        )

    return task_step


def start_task_step_service(
    db: Session,
    step_id,
):
    task_step = start_task_step(
        db,
        step_id,
    )

    if task_step is None:
        raise ValueError(
            "Task step not found."
        )

    return task_step


def complete_task_step_service(
    db: Session,
    step_id,
    output_ref: dict = None,
):
    task_step = complete_task_step(
        db,
        step_id,
        output_ref=output_ref,
    )

    if task_step is None:
        raise ValueError(
            "Task step not found."
        )

    return task_step


def fail_task_step_service(
    db: Session,
    step_id,
    error_message: str,
):
    if not error_message or not error_message.strip():
        raise ValueError(
            "Error message is required."
        )

    task_step = fail_task_step(
        db,
        step_id,
        error_message.strip(),
    )

    if task_step is None:
        raise ValueError(
            "Task step not found."
        )

    return task_step


def delete_task_step_service(
    db: Session,
    step_id,
):
    deleted = delete_task_step(
        db,
        step_id,
    )

    if not deleted:
        raise ValueError(
            "Task step not found."
        )

    return True