from uuid import uuid4

from app.db.session import SessionLocal

from app.services.workspace_service import (
    create_workspace_service,
)

from app.services.project_service import (
    create_project_service,
)

from app.services.file_service import (
    create_file_service,
    get_file_service,
    get_files_by_project_service,
    get_files_by_user_service,
    get_file_by_sha256_service,
    get_files_service,
    update_file_service,
    delete_file_service,
)

from app.repositories.user_repository import (
    create_user,
)


def test_file_service():

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # CREATE USER
        # --------------------------------------------------

        user = create_user(
            db,
            email=f"file-test-{uuid4().hex}@pramaan.local",
            display_name="File Test User",
        )

        # --------------------------------------------------
        # CREATE WORKSPACE
        # --------------------------------------------------

        workspace = create_workspace_service(
            db=db,
            name=f"File-Test-Workspace-{uuid4().hex[:8]}",
            description="File service test workspace.",
            sensitivity_class="confidential",
        )

        # --------------------------------------------------
        # CREATE PROJECT
        # --------------------------------------------------

        project = create_project_service(
            db=db,
            workspace_id=workspace.workspace_id,
            name=f"File-Test-Project-{uuid4().hex[:8]}",
            description="File service test project.",
        )

        # --------------------------------------------------
        # CREATE FILE
        # --------------------------------------------------

        sha256 = f"test-sha256-{uuid4().hex}"

        file = create_file_service(
            db=db,
            project_id=project.project_id,
            uploaded_by=user.user_id,
            filename="PRAMAAN-Test-File.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            storage_path="test/pramaan-test-file.pdf",
            sha256=sha256,
            sensitivity_class="confidential",
        )

        assert file is not None
        assert file.filename == "PRAMAAN-Test-File.pdf"
        assert file.project_id == project.project_id
        assert file.uploaded_by == user.user_id

        # --------------------------------------------------
        # GET FILE
        # --------------------------------------------------

        found = get_file_service(
            db,
            file.file_id,
        )

        assert found is not None
        assert found.file_id == file.file_id

        # --------------------------------------------------
        # GET BY SHA256
        # --------------------------------------------------

        found_by_sha256 = get_file_by_sha256_service(
            db,
            sha256,
        )

        assert found_by_sha256 is not None
        assert found_by_sha256.file_id == file.file_id

        # --------------------------------------------------
        # GET FILES BY PROJECT
        # --------------------------------------------------

        project_files = get_files_by_project_service(
            db,
            project.project_id,
        )

        assert len(project_files) >= 1

        # --------------------------------------------------
        # GET FILES BY USER
        # --------------------------------------------------

        user_files = get_files_by_user_service(
            db,
            user.user_id,
        )

        assert len(user_files) >= 1

        # --------------------------------------------------
        # GET ALL FILES
        # --------------------------------------------------

        files = get_files_service(
            db,
            limit=100,
        )

        assert len(files) >= 1

        # --------------------------------------------------
        # UPDATE FILE
        # --------------------------------------------------

        updated = update_file_service(
            db=db,
            file_id=file.file_id,
            filename="PRAMAAN-Test-File-Updated.pdf",
            sensitivity_class="restricted",
        )

        assert updated is not None
        assert updated.filename == "PRAMAAN-Test-File-Updated.pdf"
        assert updated.sensitivity_class == "restricted"

        # --------------------------------------------------
        # DELETE FILE
        # --------------------------------------------------

        deleted = delete_file_service(
            db,
            file.file_id,
        )

        assert deleted is True

    finally:
        db.close()