from app.db.session import SessionLocal

from app.repositories.task_repository import (
    create_task,
    get_task,
    get_tasks_by_project,
    get_tasks_by_user,
    get_tasks,
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

        task = create_task(
            db=db,
            project_id=project.project_id,
            created_by=user.user_id,
            title="Repository Test Task",
            intent="Test task repository operations",
        )

        print("Created Task:")
        print(task.task_id)
        print(task.project_id)
        print(task.created_by)
        print(task.title)
        print(task.intent)
        print(task.status)
        print(task.sensitivity_class)

        found = get_task(
            db,
            task.task_id,
        )

        print("\nGet Task:")
        print(found.title)

        project_tasks = get_tasks_by_project(
            db,
            project.project_id,
        )

        print(
            "\nTasks in Project:",
            len(project_tasks),
        )

        user_tasks = get_tasks_by_user(
            db,
            user.user_id,
        )

        print(
            "Tasks created by User:",
            len(user_tasks),
        )

        tasks = get_tasks(db)

        print(
            "Total Tasks:",
            len(tasks),
        )

finally:
    db.close()