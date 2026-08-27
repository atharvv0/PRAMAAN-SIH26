from app.db.session import SessionLocal

from app.services.task_file_service import (
    attach_file_to_task_service,
    get_task_file_service,
    get_files_for_task_service,
    get_tasks_for_file_service,
    update_task_file_role_service,
    detach_file_from_task_service,
)

from app.models.task import Task
from app.models.file import File


db = SessionLocal()

try:

    task = db.query(Task).first()
    file = db.query(File).first()

    if task is None:
        raise RuntimeError(
            "No task found in database. Create a task first."
        )

    if file is None:
        raise RuntimeError(
            "No file found in database. Create a file first."
        )

    print("Using Task:")
    print("Task ID:", task.task_id)

    print("\nUsing File:")
    print("File ID:", file.file_id)

    # --------------------------------------------------
    # CREATE / ATTACH
    # --------------------------------------------------

    existing = get_task_file_service(
        db,
        task.task_id,
        file.file_id,
    ) if db.query(
        __import__(
            "app.models.task_file",
            fromlist=["TaskFile"]
        ).TaskFile
    ).filter(
        __import__(
            "app.models.task_file",
            fromlist=["TaskFile"]
        ).TaskFile.task_id == task.task_id,
        __import__(
            "app.models.task_file",
            fromlist=["TaskFile"]
        ).TaskFile.file_id == file.file_id,
    ).first() else None

    if existing is not None:
        print("\nTask file already exists.")
        print("Role:", existing.role)
        task_file = existing
    else:
        task_file = attach_file_to_task_service(
            db=db,
            task_id=task.task_id,
            file_id=file.file_id,
            role="input",
        )

        print("\nAttached File To Task:")
        print("Task ID:", task_file.task_id)
        print("File ID:", task_file.file_id)
        print("Role:", task_file.role)

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    found = get_task_file_service(
        db,
        task.task_id,
        file.file_id,
    )

    print("\nGet Task File:")
    print("Role:", found.role)

    # --------------------------------------------------
    # GET FILES FOR TASK
    # --------------------------------------------------

    files = get_files_for_task_service(
        db,
        task.task_id,
    )

    print("\nFiles For Task:")
    print("Total:", len(files))

    # --------------------------------------------------
    # GET TASKS FOR FILE
    # --------------------------------------------------

    tasks = get_tasks_for_file_service(
        db,
        file.file_id,
    )

    print("\nTasks For File:")
    print("Total:", len(tasks))

    # --------------------------------------------------
    # UPDATE ROLE
    # --------------------------------------------------

    updated = update_task_file_role_service(
        db=db,
        task_id=task.task_id,
        file_id=file.file_id,
        role="reference",
    )

    print("\nUpdated Task File:")
    print("Role:", updated.role)

    # --------------------------------------------------
    # RESTORE ROLE
    # --------------------------------------------------

    updated = update_task_file_role_service(
        db=db,
        task_id=task.task_id,
        file_id=file.file_id,
        role="input",
    )

    print("\nRestored Role:")
    print("Role:", updated.role)

    # --------------------------------------------------
    # DELETE / DETACH
    # --------------------------------------------------

    deleted = detach_file_from_task_service(
        db,
        task.task_id,
        file.file_id,
    )

    print("\nDetached File From Task:")
    print(deleted)

finally:
    db.close()