from app.db.session import SessionLocal

from app.services.project_service import (
    create_project_service,
    get_project_service,
    get_projects_service,
)

from app.models.workspace import Workspace


db = SessionLocal()

try:

    workspace = db.query(Workspace).first()

    if workspace is None:
        print("No workspace found.")
    else:

        project = create_project_service(
            db=db,
            workspace_id=workspace.workspace_id,
            name="Service Test Project",
            description="Project service test.",
        )

        print("Created Project:")
        print("ID:", project.project_id)
        print("Workspace ID:", project.workspace_id)
        print("Name:", project.name)
        print("Description:", project.description)

        found = get_project_service(
            db,
            project.project_id,
        )

        print("\nGet Project:")
        print(found.name)

        projects = get_projects_service(
        db,
        limit=100,
)

        print(
            "\nProjects in Workspace:",
            len(projects),
        )

finally:
    db.close()