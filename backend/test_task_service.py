from app.db.session import SessionLocal

from app.services.task_service import (
    create_task_service,
    get_task_service,
    get_tasks_by_project_service,
    get_tasks_by_user_service,
    get_tasks_service,
    update_task_service,
)

from app.models.project import Project
from app.models.user import User


db = SessionLocal()

try:

    project = db.query(Project).first()
    user = db.query(User).first()

    if project is None:
        print("No project found.")

    elif user is None:
        print("No user found.")

    else:

        task = create_task_service(
            db=db,
            project_id=project.project_id,
            created_by=user.user_id,
            title="Service Test Task",
            intent="Test the PRAMAAN task service.",
        )

        print("Created Task:")
        print("ID:", task.task_id)
        print("Project ID:", task.project_id)
        print("Created By:", task.created_by)
        print("Title:", task.title)
        print("Intent:", task.intent)
        print("Status:", task.status)
        print(
            "Sensitivity:",
            task.sensitivity_class,
        )

        # Get by ID
        found = get_task_service(
            db,
            task.task_id,
        )

        print("\nGet Task:")
        print(found.title)

        # Get tasks by project
        project_tasks = get_tasks_by_project_service(
            db,
            project.project_id,
        )

        print(
            "\nTasks for Project:",
            len(project_tasks),
        )

        # Get tasks by user
        user_tasks = get_tasks_by_user_service(
            db,
            user.user_id,
        )

        print(
            "Tasks for User:",
            len(user_tasks),
        )

        # Get all tasks
        tasks = get_tasks_service(
            db,
            limit=100,
        )

        print(
            "Total Tasks:",
            len(tasks),
        )

        # Update task
        updated = update_task_service(
            db=db,
            task_id=task.task_id,
            title="Updated Service Test Task",
            status="running",
        )

        print("\nUpdated Task:")
        print("Title:", updated.title)
        print("Status:", updated.status)

finally:
    db.close()