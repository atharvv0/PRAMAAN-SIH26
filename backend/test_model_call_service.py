from uuid import uuid4

from app.db.session import SessionLocal

from app.repositories.user_repository import create_user

from app.services.workspace_service import (
    create_workspace_service,
)

from app.services.project_service import (
    create_project_service,
)

from app.services.task_service import (
    create_task_service,
)

from app.services.model_service import (
    create_model_service,
)

from app.services.model_version_service import (
    create_model_version_service,
    get_model_versions_service,
)

from app.services.model_call_service import (
    create_model_call_service,
    get_model_call_service,
    get_model_calls_by_task_service,
    get_model_calls_by_model_version_service,
    get_model_calls_service,
    update_model_call_service,
)


def test_model_call_service():

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # CREATE USER
        # --------------------------------------------------

        user = create_user(
            db,
            email=f"model-call-{uuid4().hex}@pramaan.local",
            display_name="Model Call Test User",
        )

        # --------------------------------------------------
        # CREATE WORKSPACE
        # --------------------------------------------------

        workspace = create_workspace_service(
            db=db,
            name=f"Model-Call-Workspace-{uuid4().hex[:8]}",
            description="Model call service test workspace.",
            sensitivity_class="confidential",
        )

        # --------------------------------------------------
        # CREATE PROJECT
        # --------------------------------------------------

        project = create_project_service(
            db=db,
            workspace_id=workspace.workspace_id,
            name=f"Model-Call-Project-{uuid4().hex[:8]}",
            description="Model call service test project.",
        )

        # --------------------------------------------------
        # CREATE TASK
        # --------------------------------------------------

        task = create_task_service(
            db=db,
            project_id=project.project_id,
            created_by=user.user_id,
            title="Model Call Test Task",
            intent="Test the model call service.",
        )

        # --------------------------------------------------
        # CREATE MODEL
        # --------------------------------------------------

        model = create_model_service(
            db=db,
            name=f"Test-Model-{uuid4().hex[:8]}",
            runtime="test",
        )

        # --------------------------------------------------
        # CREATE MODEL VERSION
        # --------------------------------------------------

        model_version = create_model_version_service(
            db=db,
            model_id=model.model_id,
            version="1.0",
            weights_path="test/model/weights",
            license="MIT",
            quantization="none",
            vram_required_gb=4,
            status="active",
        )

        # --------------------------------------------------
        # VERIFY MODEL VERSION
        # --------------------------------------------------

        versions = get_model_versions_service(
            db,
            limit=100,
        )

        assert len(versions) >= 1

        # --------------------------------------------------
        # CREATE MODEL CALL
        # --------------------------------------------------

        model_call = create_model_call_service(
            db=db,
            task_id=task.task_id,
            model_version_id=model_version.model_version_id,
            purpose="PRAMAAN model call service test",
            input_tokens=100,
            output_tokens=50,
            latency_ms=250,
            status="pending",
        )

        assert model_call is not None
        assert model_call.task_id == task.task_id
        assert (
            model_call.model_version_id
            == model_version.model_version_id
        )

        # --------------------------------------------------
        # GET BY ID
        # --------------------------------------------------

        found = get_model_call_service(
            db,
            model_call.model_call_id,
        )

        assert found is not None
        assert found.model_call_id == model_call.model_call_id

        # --------------------------------------------------
        # GET BY TASK
        # --------------------------------------------------

        task_calls = get_model_calls_by_task_service(
            db,
            task.task_id,
        )

        assert len(task_calls) >= 1

        # --------------------------------------------------
        # GET BY MODEL VERSION
        # --------------------------------------------------

        version_calls = (
            get_model_calls_by_model_version_service(
                db,
                model_version.model_version_id,
            )
        )

        assert len(version_calls) >= 1

        # --------------------------------------------------
        # GET ALL
        # --------------------------------------------------

        all_calls = get_model_calls_service(
            db,
            limit=100,
        )

        assert len(all_calls) >= 1

        # --------------------------------------------------
        # UPDATE
        # --------------------------------------------------

        updated = update_model_call_service(
            db=db,
            model_call_id=model_call.model_call_id,
            output_tokens=75,
            latency_ms=300,
            status="completed",
        )

        assert updated is not None
        assert updated.output_tokens == 75
        assert updated.latency_ms == 300
        assert updated.status == "completed"

    finally:
        db.close()