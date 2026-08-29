import pytest

from app.services.task_service import (
    create_task_service,
    get_task_service,
    get_tasks_by_project_service,
    get_tasks_by_user_service,
    get_tasks_service,
    update_task_service,
)

from app.services.workspace_service import (
    create_workspace_service,
)

from app.services.project_service import (
    create_project_service,
)

from app.repositories.user_repository import (
    get_users,
)


def test_task_service(db):

    # --------------------------------------------------
    # GET EXISTING USER
    # --------------------------------------------------

    users = get_users(
        db,
        limit=1,
    )

    if not users:
        pytest.skip(
            "No user found. Create a user first."
        )

    user = users[0]

    # --------------------------------------------------
    # CREATE WORKSPACE
    # --------------------------------------------------

    workspace = create_workspace_service(
        db=db,
        name="Task Test Workspace",
        description="Workspace for task service test.",
        sensitivity_class="confidential",
    )

    # --------------------------------------------------
    # CREATE PROJECT
    # --------------------------------------------------

    project = create_project_service(
        db=db,
        workspace_id=workspace.workspace_id,
        name="Task Test Project",
        description="Project for task service test.",
    )

    # --------------------------------------------------
    # CREATE TASK
    # --------------------------------------------------

    task = create_task_service(
        db=db,
        project_id=project.project_id,
        created_by=user.user_id,
        title="Service Test Task",
        intent="Test the PRAMAAN task service.",
    )

    assert task.project_id == project.project_id
    assert task.created_by == user.user_id
    assert task.title == "Service Test Task"
    assert task.intent == "Test the PRAMAAN task service."
    assert task.status == "queued"
    assert task.sensitivity_class == "confidential"

    # --------------------------------------------------
    # GET BY ID
    # --------------------------------------------------

    found = get_task_service(
        db,
        task.task_id,
    )

    assert found.task_id == task.task_id
    assert found.title == "Service Test Task"

    # --------------------------------------------------
    # GET TASKS BY PROJECT
    # --------------------------------------------------

    project_tasks = get_tasks_by_project_service(
        db,
        project.project_id,
    )

    assert any(
        item.task_id == task.task_id
        for item in project_tasks
    )

    # --------------------------------------------------
    # GET TASKS BY USER
    # --------------------------------------------------

    user_tasks = get_tasks_by_user_service(
        db,
        user.user_id,
    )

    assert any(
        item.task_id == task.task_id
        for item in user_tasks
    )

    # --------------------------------------------------
    # GET ALL TASKS
    # --------------------------------------------------

    tasks = get_tasks_service(
        db,
        limit=100,
    )

    assert any(
        item.task_id == task.task_id
        for item in tasks
    )

    # --------------------------------------------------
    # UPDATE TASK
    # --------------------------------------------------

    updated = update_task_service(
        db=db,
        task_id=task.task_id,
        title="Updated Service Test Task",
        status="running",
    )

    assert updated.title == "Updated Service Test Task"
    assert updated.status == "running"

    # --------------------------------------------------
    # VERIFY UPDATE
    # --------------------------------------------------

    found = get_task_service(
        db,
        task.task_id,
    )

    assert found.title == "Updated Service Test Task"
    assert found.status == "running"

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    deleted = (
        __import__(
            "app.services.task_service",
            fromlist=["delete_task_service"],
        ).delete_task_service(
            db,
            task.task_id,
        )
    )

    assert deleted is True

    # --------------------------------------------------
    # VERIFY DELETE
    # --------------------------------------------------

    with pytest.raises(ValueError):
        get_task_service(
            db,
            task.task_id,
        )