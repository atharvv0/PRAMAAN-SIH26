from sqlalchemy.orm import Session

from app.models.task import Task


def create_task(
    db: Session,
    project_id,
    created_by,
    title: str,
    intent: str,
):
    task = Task(
        project_id=project_id,
        created_by=created_by,
        title=title,
        intent=intent,
        status="queued",
        sensitivity_class="confidential",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_task(
    db: Session,
    task_id,
):
    return (
        db.query(Task)
        .filter(Task.task_id == task_id)
        .first()
    )


def get_tasks_by_project(
    db: Session,
    project_id,
):
    return (
        db.query(Task)
        .filter(Task.project_id == project_id)
        .all()
    )


def get_tasks_by_user(
    db: Session,
    created_by,
):
    return (
        db.query(Task)
        .filter(Task.created_by == created_by)
        .all()
    )


def get_tasks(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Task)
        .limit(limit)
        .all()
    )


def update_task(
    db: Session,
    task_id,
    title: str = None,
    intent: str = None,
    status: str = None,
    sensitivity_class: str = None,
):
    task = get_task(db, task_id)

    if task is None:
        return None

    if title is not None:
        task.title = title

    if intent is not None:
        task.intent = intent

    if status is not None:
        task.status = status

    if sensitivity_class is not None:
        task.sensitivity_class = sensitivity_class

    db.commit()
    db.refresh(task)

    return task


def delete_task(
    db: Session,
    task_id,
):
    task = get_task(db, task_id)

    if task is None:
        return False

    db.delete(task)
    db.commit()

    return True