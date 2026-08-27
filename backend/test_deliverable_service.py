import pytest

from app.services.deliverable_service import (
    create_deliverable_service,
    get_deliverable_service,
    get_deliverables_by_task_service,
    get_deliverables_by_file_service,
    get_deliverables_service,
    update_deliverable_service,
    delete_deliverable_service,
)


def test_create_deliverable_empty_format(db):
    with pytest.raises(
        ValueError,
        match="Deliverable format is required",
    ):
        create_deliverable_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            file_id="00000000-0000-0000-0000-000000000000",
            format="",
            version="v1",
        )


def test_create_deliverable_invalid_approval_state(db):
    with pytest.raises(
        ValueError,
        match="Invalid approval state",
    ):
        create_deliverable_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            file_id="00000000-0000-0000-0000-000000000000",
            format="pdf",
            version="v1",
            approval_state="invalid",
        )


def test_create_deliverable_empty_version(db):
    with pytest.raises(
        ValueError,
        match="Deliverable version is required",
    ):
        create_deliverable_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            file_id="00000000-0000-0000-0000-000000000000",
            format="pdf",
            version="",
        )


def test_get_deliverable_not_found(db):
    with pytest.raises(
        ValueError,
        match="Deliverable not found",
    ):
        get_deliverable_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )


def test_get_deliverables_invalid_limit(db):
    with pytest.raises(
        ValueError,
        match="Limit must be greater than 0",
    ):
        get_deliverables_service(db, 0)


def test_update_deliverable_empty_format(db):
    with pytest.raises(
        ValueError,
        match="Format cannot be empty",
    ):
        update_deliverable_service(
            db=db,
            deliverable_id="00000000-0000-0000-0000-000000000000",
            format="",
        )


def test_update_deliverable_invalid_approval_state(db):
    with pytest.raises(
        ValueError,
        match="Invalid approval state",
    ):
        update_deliverable_service(
            db=db,
            deliverable_id="00000000-0000-0000-0000-000000000000",
            approval_state="invalid",
        )


def test_update_deliverable_empty_version(db):
    with pytest.raises(
        ValueError,
        match="Version cannot be empty",
    ):
        update_deliverable_service(
            db=db,
            deliverable_id="00000000-0000-0000-0000-000000000000",
            version="",
        )


def test_update_deliverable_not_found(db):
    with pytest.raises(
        ValueError,
        match="Deliverable not found",
    ):
        update_deliverable_service(
            db=db,
            deliverable_id="00000000-0000-0000-0000-000000000000",
            version="v2",
        )


def test_get_deliverables_by_task(db):
    result = get_deliverables_by_task_service(
        db,
        "00000000-0000-0000-0000-000000000000",
    )

    assert isinstance(result, list)


def test_get_deliverables_by_file(db):
    result = get_deliverables_by_file_service(
        db,
        "00000000-0000-0000-0000-000000000000",
    )

    assert isinstance(result, list)


def test_delete_deliverable_not_found(db):
    with pytest.raises(
        ValueError,
        match="Deliverable not found",
    ):
        delete_deliverable_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )