from app.db.session import SessionLocal

from app.services.workspace_service import (
    create_workspace_service,
    get_workspace_service,
    get_workspaces_service,
    update_workspace_service,
    delete_workspace_service,
)


db = SessionLocal()

try:

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------
    workspace = create_workspace_service(
        db=db,
        name="PRAMAAN-Test-Workspace",
        description="Workspace service test.",
        sensitivity_class="confidential",
    )

    print("Created Workspace:")
    print("ID:", workspace.workspace_id)
    print("Name:", workspace.name)
    print("Description:", workspace.description)
    print("Sensitivity:", workspace.sensitivity_class)

    # -------------------------------------------------
    # GET
    # -------------------------------------------------
    found = get_workspace_service(
        db,
        workspace.workspace_id,
    )

    print("\nGet Workspace:")
    print("Name:", found.name)

    # -------------------------------------------------
    # GET ALL
    # -------------------------------------------------
    workspaces = get_workspaces_service(
        db,
        limit=100,
    )

    print("\nTotal Workspaces:")
    print(len(workspaces))

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    updated = update_workspace_service(
        db=db,
        workspace_id=workspace.workspace_id,
        name="PRAMAAN-Test-Workspace-Updated",
        description="Updated workspace service test.",
        sensitivity_class="restricted",
    )

    print("\nUpdated Workspace:")
    print("Name:", updated.name)
    print("Description:", updated.description)
    print("Sensitivity:", updated.sensitivity_class)

    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------
    deleted = delete_workspace_service(
        db,
        workspace.workspace_id,
    )

    print("\nDeleted Workspace:")
    print(deleted)

finally:
    db.close()