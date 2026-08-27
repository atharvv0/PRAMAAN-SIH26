from app.db.session import SessionLocal

from app.repositories.project_repository import (
    create_project,
    get_project,
    get_projects_by_workspace,
    get_projects,
)

from app.models.workspace import Workspace


db = SessionLocal()

try:

    workspace = (
        db.query(Workspace)
        .first()
    )

    if workspace is None:
        print("No workspace found. Create a workspace first.")
    else:

        project = create_project(
            db,
            workspace_id=workspace.workspace_id,
            name="Repository Test Project",
            description="Testing project repository",
            status="active",
        )

        print("Created Project:")
        print(project.project_id)
        print(project.workspace_id)
        print(project.name)
        print(project.description)
        print(project.status)

        found = get_project(
            db,
            project.project_id,
        )

        print("\nGet Project:")
        print(found.name)

        workspace_projects = get_projects_by_workspace(
            db,
            workspace.workspace_id,
        )

        print(
            "\nProjects in Workspace:",
            len(workspace_projects)
        )

        projects = get_projects(db)

        print(
            "Total Projects:",
            len(projects)
        )

finally:
    db.close()