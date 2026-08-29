import pytest

def test_workspace_service(db):

    from app.services.workspace_service import (
        create_workspace_service,
        get_workspace_service,
        get_workspaces_service,
        update_workspace_service,
        delete_workspace_service,
    )

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------

    workspace = create_workspace_service(
        db=db,
        name="PRAMAAN-Test-Workspace",
        description="Workspace service test.",
        sensitivity_class="confidential",
    )

    assert workspace.name == "PRAMAAN-Test-Workspace"
    assert workspace.description == "Workspace service test."
    assert workspace.sensitivity_class == "confidential"

    # -------------------------------------------------
    # GET
    # -------------------------------------------------

    found = get_workspace_service(
        db,
        workspace.workspace_id,
    )

    assert found.workspace_id == workspace.workspace_id
    assert found.name == "PRAMAAN-Test-Workspace"

    # -------------------------------------------------
    # GET ALL
    # -------------------------------------------------

    workspaces = get_workspaces_service(
        db,
        limit=100,
    )

    assert any(
        item.workspace_id == workspace.workspace_id
        for item in workspaces
    )

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

    assert updated.name == "PRAMAAN-Test-Workspace-Updated"
    assert updated.description == "Updated workspace service test."
    assert updated.sensitivity_class == "restricted"

    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------

    deleted = delete_workspace_service(
        db,
        workspace.workspace_id,
    )

    assert deleted is True

    # -------------------------------------------------
    # VERIFY DELETE
    # -------------------------------------------------

    with pytest.raises(ValueError):
        get_workspace_service(
            db,
            workspace.workspace_id,
        )