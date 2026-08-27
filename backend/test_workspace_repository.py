from app.db.session import SessionLocal

from app.repositories.workspace_repository import (
    create_workspace,
    get_workspace,
    get_workspaces,
)


db = SessionLocal()

try:

    workspace = create_workspace(
        db,
        name="Repository Test Workspace",
        description="Testing workspace repository",
        sensitivity_class="confidential",
    )

    print("Created Workspace:")
    print(workspace.workspace_id)
    print(workspace.name)
    print(workspace.description)
    print(workspace.sensitivity_class)

    found = get_workspace(
        db,
        workspace.workspace_id,
    )

    print("\nGet Workspace:")
    print(found.name)

    workspaces = get_workspaces(db)

    print("\nTotal Workspaces:", len(workspaces))

finally:
    db.close()