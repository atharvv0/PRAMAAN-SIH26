from app.db.session import SessionLocal

from app.repositories.task_file_repository import (
    attach_file_to_task,
    get_task_file,
    get_files_for_task,
    get_tasks_for_file,
)

from app.models.task import Task
from app.models.file import File


db = SessionLocal()

try:

    task = db.query(Task).first()
    file = db.query(File).first()

    if task is None:
        print("No task found.")

    elif file is None:
        print("No file found.")

    else:

        # Check whether this relationship already exists
        existing = get_task_file(
            db,
            task.task_id,
            file.file_id,
        )

        if existing:
            print("Task File already exists:")
            print("Task ID:", existing.task_id)
            print("File ID:", existing.file_id)
            print("Role:", existing.role)

            task_file = existing

        else:
            task_file = attach_file_to_task(
                db=db,
                task_id=task.task_id,
                file_id=file.file_id,
                role="input",
            )

            print("Task File Created:")
            print("Task ID:", task_file.task_id)
            print("File ID:", task_file.file_id)
            print("Role:", task_file.role)

        found = get_task_file(
            db,
            task.task_id,
            file.file_id,
        )

        print("\nGet Task File:")
        print("Task ID:", found.task_id)
        print("File ID:", found.file_id)
        print("Role:", found.role)

        task_files = get_files_for_task(
            db,
            task.task_id,
        )

        print(
            "\nFiles attached to Task:",
            len(task_files),
        )

        file_tasks = get_tasks_for_file(
            db,
            file.file_id,
        )

        print(
            "Tasks using File:",
            len(file_tasks),
        )

finally:
    db.close()