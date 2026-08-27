from sqlalchemy.orm import Session

from app.models.task_file import TaskFile


def attach_file_to_task(
    db: Session,
    task_id,
    file_id,
    role: str = "input",
):
    task_file = TaskFile(
        task_id=task_id,
        file_id=file_id,
        role=role,
    )

    db.add(task_file)
    db.commit()
    db.refresh(task_file)

    return task_file


def get_task_file(
    db: Session,
    task_id,
    file_id,
):
    return (
        db.query(TaskFile)
        .filter(
            TaskFile.task_id == task_id,
            TaskFile.file_id == file_id,
        )
        .first()
    )


def get_files_for_task(
    db: Session,
    task_id,
):
    return (
        db.query(TaskFile)
        .filter(TaskFile.task_id == task_id)
        .all()
    )


def get_tasks_for_file(
    db: Session,
    file_id,
):
    return (
        db.query(TaskFile)
        .filter(TaskFile.file_id == file_id)
        .all()
    )


def update_task_file_role(
    db: Session,
    task_id,
    file_id,
    role: str,
):
    task_file = get_task_file(
        db,
        task_id,
        file_id,
    )

    if task_file is None:
        return None

    task_file.role = role

    db.commit()
    db.refresh(task_file)

    return task_file


def detach_file_from_task(
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
        return False

    db.delete(task_file)
    db.commit()

    return True