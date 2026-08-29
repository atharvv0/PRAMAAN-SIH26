import uuid
import pytest

from app.services.task_file_service import (
    attach_file_to_task_service,
    get_task_file_service,
    get_files_for_task_service,
    get_tasks_for_file_service,
    update_task_file_role_service,
    detach_file_from_task_service,
)

from app.services.workspace_service import (
    create_workspace_service,
)

from app.services.project_service import (
    create_project_service,
)

from app.services.task_service import (
    create_task_service,
)

from app.services.file_service import (
    create_file_service,
)

from app.repositories.user_repository import (
    get_users,
)


def test_task_file_service(db):

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
    # UNIQUE TEST DATA
    # --------------------------------------------------

    test_id = uuid.uuid4().hex

    # --------------------------------------------------
    # CREATE WORKSPACE
    # --------------------------------------------------

    workspace = create_workspace_service(
        db=db,
        name=f"Task File Test Workspace {test_id}",
        description="Workspace for task file service test.",
        sensitivity_class="confidential",
    )

    # --------------------------------------------------
    # CREATE PROJECT
    # --------------------------------------------------

    project = create_project_service(
        db=db,
        workspace_id=workspace.workspace_id,
        name=f"Task File Test Project {test_id}",
        description="Project for task file service test.",
    )

    # --------------------------------------------------
    # CREATE TASK
    # --------------------------------------------------

    task = create_task_service(
        db=db,
        project_id=project.project_id,
        created_by=user.user_id,
        title=f"Task File Test Task {test_id}",
        intent="Test task file relationship service.",
    )

    # --------------------------------------------------
    # CREATE FILE
    # --------------------------------------------------

    file = create_file_service(
        db=db,
        project_id=project.project_id,
        uploaded_by=user.user_id,
        filename=f"task-file-test-{test_id}.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        storage_path=f"test/task-file-test-{test_id}.pdf",
        sha256=f"task-file-test-sha256-{test_id}",
        sensitivity_class="confidential",
    )

    # --------------------------------------------------
    # ATTACH FILE TO TASK
    # --------------------------------------------------

    task_file = attach_file_to_task_service(
        db=db,
        task_id=task.task_id,
        file_id=file.file_id,
        role="input",
    )

    assert task_file.task_id == task.task_id
    assert task_file.file_id == file.file_id
    assert task_file.role == "input"

    # --------------------------------------------------
    # GET TASK FILE
    # --------------------------------------------------

    found = get_task_file_service(
        db,
        task.task_id,
        file.file_id,
    )

    assert found.task_id == task.task_id
    assert found.file_id == file.file_id
    assert found.role == "input"

    # --------------------------------------------------
    # GET FILES FOR TASK
    # --------------------------------------------------

    files = get_files_for_task_service(
        db,
        task.task_id,
    )

    assert any(
        item.file_id == file.file_id
        for item in files
    )

    # --------------------------------------------------
    # GET TASKS FOR FILE
    # --------------------------------------------------

    tasks = get_tasks_for_file_service(
        db,
        file.file_id,
    )

    assert any(
        item.task_id == task.task_id
        for item in tasks
    )

    # --------------------------------------------------
    # UPDATE ROLE
    # --------------------------------------------------

    updated = update_task_file_role_service(
        db=db,
        task_id=task.task_id,
        file_id=file.file_id,
        role="reference",
    )

    assert updated.role == "reference"

    # --------------------------------------------------
    # RESTORE ROLE
    # --------------------------------------------------

    updated = update_task_file_role_service(
        db=db,
        task_id=task.task_id,
        file_id=file.file_id,
        role="input",
    )

    assert updated.role == "input"

    # --------------------------------------------------
    # DETACH FILE
    # --------------------------------------------------

    deleted = detach_file_from_task_service(
        db,
        task.task_id,
        file.file_id,
    )

    assert deleted is True

    # --------------------------------------------------
    # VERIFY DETACHED
    # --------------------------------------------------

    with pytest.raises(ValueError):
        get_task_file_service(
            db,
            task.task_id,
            file.file_id,
        )