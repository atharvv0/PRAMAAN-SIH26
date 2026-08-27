from app.db.session import SessionLocal

from app.repositories.deliverable_repository import (
    create_deliverable,
    get_deliverable,
    get_deliverables_by_task,
    get_deliverables_by_file,
    get_deliverables,
    update_deliverable,
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

        deliverable = create_deliverable(
            db=db,
            task_id=task.task_id,
            file_id=file.file_id,
            format="pdf",
            version="1.0",
            approval_state="pending",
        )

        print("Created Deliverable:")
        print(
            "Deliverable ID:",
            deliverable.deliverable_id,
        )
        print(
            "Task ID:",
            deliverable.task_id,
        )
        print(
            "File ID:",
            deliverable.file_id,
        )
        print(
            "Format:",
            deliverable.format,
        )
        print(
            "Version:",
            deliverable.version,
        )
        print(
            "Approval State:",
            deliverable.approval_state,
        )

        found = get_deliverable(
            db,
            deliverable.deliverable_id,
        )

        print("\nGet Deliverable:")
        print(found.format)

        task_deliverables = get_deliverables_by_task(
            db,
            task.task_id,
        )

        print(
            "\nDeliverables for Task:",
            len(task_deliverables),
        )

        file_deliverables = get_deliverables_by_file(
            db,
            file.file_id,
        )

        print(
            "Deliverables for File:",
            len(file_deliverables),
        )

        updated = update_deliverable(
            db,
            deliverable.deliverable_id,
            version="1.1",
            approval_state="approved",
        )

        print("\nUpdated Deliverable:")
        print(
            "Version:",
            updated.version,
        )
        print(
            "Approval State:",
            updated.approval_state,
        )

        all_deliverables = get_deliverables(db)

        print(
            "\nTotal Deliverables:",
            len(all_deliverables),
        )

finally:
    db.close()