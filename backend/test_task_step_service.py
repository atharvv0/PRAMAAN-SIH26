import pytest

from app.services.task_step_service import (
    create_task_step_service,
    get_task_step_service,
    get_task_steps_by_task_service,
    get_task_step_by_number_service,
    get_task_steps_service,
    update_task_step_service,
    start_task_step_service,
    complete_task_step_service,
    fail_task_step_service,
    delete_task_step_service,
)


def test_create_task_step_empty_step_type(db):
    with pytest.raises(ValueError, match="Step type is required"):
        create_task_step_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            step_no=1,
            step_type="",
        )


def test_create_task_step_invalid_step_number(db):
    with pytest.raises(
        ValueError,
        match="Step number must be greater than 0",
    ):
        create_task_step_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            step_no=0,
            step_type="document_processing",
        )


def test_create_task_step_invalid_status(db):
    with pytest.raises(
        ValueError,
        match="Invalid task step status",
    ):
        create_task_step_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            step_no=1,
            step_type="document_processing",
            status="invalid",
        )


def test_get_task_step_not_found(db):
    with pytest.raises(
        ValueError,
        match="Task step not found",
    ):
        get_task_step_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )


def test_get_task_step_by_number_invalid_step_number(db):
    with pytest.raises(
        ValueError,
        match="Step number must be greater than 0",
    ):
        get_task_step_by_number_service(
            db,
            "00000000-0000-0000-0000-000000000000",
            0,
        )


def test_get_task_steps_invalid_limit(db):
    with pytest.raises(
        ValueError,
        match="Limit must be greater than 0",
    ):
        get_task_steps_service(db, 0)


def test_update_task_step_invalid_step_number(db):
    with pytest.raises(
        ValueError,
        match="Step number must be greater than 0",
    ):
        update_task_step_service(
            db=db,
            step_id="00000000-0000-0000-0000-000000000000",
            step_no=0,
        )


def test_update_task_step_invalid_status(db):
    with pytest.raises(
        ValueError,
        match="Invalid task step status",
    ):
        update_task_step_service(
            db=db,
            step_id="00000000-0000-0000-0000-000000000000",
            status="invalid",
        )


def test_update_task_step_empty_step_type(db):
    with pytest.raises(
        ValueError,
        match="Step type cannot be empty",
    ):
        update_task_step_service(
            db=db,
            step_id="00000000-0000-0000-0000-000000000000",
            step_type="",
        )


def test_update_task_step_not_found(db):
    with pytest.raises(
        ValueError,
        match="Task step not found",
    ):
        update_task_step_service(
            db=db,
            step_id="00000000-0000-0000-0000-000000000000",
            status="completed",
        )


def test_start_task_step_not_found(db):
    with pytest.raises(
        ValueError,
        match="Task step not found",
    ):
        start_task_step_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )


def test_complete_task_step_not_found(db):
    with pytest.raises(
        ValueError,
        match="Task step not found",
    ):
        complete_task_step_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )


def test_fail_task_step_empty_error_message(db):
    with pytest.raises(
        ValueError,
        match="Error message is required",
    ):
        fail_task_step_service(
            db=db,
            step_id="00000000-0000-0000-0000-000000000000",
            error_message="",
        )


def test_fail_task_step_not_found(db):
    with pytest.raises(
        ValueError,
        match="Task step not found",
    ):
        fail_task_step_service(
            db=db,
            step_id="00000000-0000-0000-0000-000000000000",
            error_message="Processing failed",
        )


def test_delete_task_step_not_found(db):
    with pytest.raises(
        ValueError,
        match="Task step not found",
    ):
        delete_task_step_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )