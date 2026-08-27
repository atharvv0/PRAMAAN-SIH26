from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.task_step import TaskStep


def create_task_step(
    db: Session,
    task_id,
    step_no: int,
    step_type: str,
    status: str = "pending",
    input_ref: dict = None,
    output_ref: dict = None,
):
    task_step = TaskStep(
        task_id=task_id,
        step_no=step_no,
        step_type=step_type,
        status=status,
        input_ref=input_ref,
        output_ref=output_ref,
    )

    db.add(task_step)
    db.commit()
    db.refresh(task_step)

    return task_step


def get_task_step(
    db: Session,
    step_id,
):
    return (
        db.query(TaskStep)
        .filter(
            TaskStep.step_id == step_id
        )
        .first()
    )


def get_task_steps_by_task(
    db: Session,
    task_id,
):
    return (
        db.query(TaskStep)
        .filter(
            TaskStep.task_id == task_id
        )
        .order_by(TaskStep.step_no)
        .all()
    )


def get_task_step_by_number(
    db: Session,
    task_id,
    step_no: int,
):
    return (
        db.query(TaskStep)
        .filter(
            TaskStep.task_id == task_id,
            TaskStep.step_no == step_no,
        )
        .first()
    )


def get_task_steps(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(TaskStep)
        .order_by(
            TaskStep.task_id,
            TaskStep.step_no,
        )
        .limit(limit)
        .all()
    )


def update_task_step(
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
    task_step = get_task_step(
        db,
        step_id,
    )

    if task_step is None:
        return None

    if step_no is not None:
        task_step.step_no = step_no

    if step_type is not None:
        task_step.step_type = step_type

    if status is not None:
        task_step.status = status

    if input_ref is not None:
        task_step.input_ref = input_ref

    if output_ref is not None:
        task_step.output_ref = output_ref

    if started_at is not None:
        task_step.started_at = started_at

    if completed_at is not None:
        task_step.completed_at = completed_at

    if error_message is not None:
        task_step.error_message = error_message

    db.commit()
    db.refresh(task_step)

    return task_step


def start_task_step(
    db: Session,
    step_id,
):
    task_step = get_task_step(
        db,
        step_id,
    )

    if task_step is None:
        return None

    task_step.status = "running"
    task_step.started_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task_step)

    return task_step


def complete_task_step(
    db: Session,
    step_id,
    output_ref: dict = None,
):
    task_step = get_task_step(
        db,
        step_id,
    )

    if task_step is None:
        return None

    task_step.status = "completed"
    task_step.completed_at = datetime.now(timezone.utc)

    if output_ref is not None:
        task_step.output_ref = output_ref

    db.commit()
    db.refresh(task_step)

    return task_step


def fail_task_step(
    db: Session,
    step_id,
    error_message: str,
):
    task_step = get_task_step(
        db,
        step_id,
    )

    if task_step is None:
        return None

    task_step.status = "failed"
    task_step.completed_at = datetime.now(timezone.utc)
    task_step.error_message = error_message

    db.commit()
    db.refresh(task_step)

    return task_step


def delete_task_step(
    db: Session,
    step_id,
):
    task_step = get_task_step(
        db,
        step_id,
    )

    if task_step is None:
        return False

    db.delete(task_step)
    db.commit()

    return True