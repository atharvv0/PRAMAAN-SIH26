import pytest

from app.services.approval_service import (
    create_approval_service,
    get_approval_service,
    get_approvals_by_task_service,
    get_approvals_by_user_service,
    get_approvals_service,
    update_approval_service,
    delete_approval_service,
)


def test_create_approval_invalid_status(db):
    with pytest.raises(
        ValueError,
        match="Invalid approval status",
    ):
        create_approval_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            requested_from="00000000-0000-0000-0000-000000000000",
            status="invalid",
        )


def test_create_approval_invalid_decision(db):
    with pytest.raises(
        ValueError,
        match="Invalid approval decision",
    ):
        create_approval_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            requested_from="00000000-0000-0000-0000-000000000000",
            decision="invalid",
        )


def test_create_approval_approved_status_wrong_decision(db):
    with pytest.raises(
        ValueError,
        match="Approved status requires approved decision",
    ):
        create_approval_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            requested_from="00000000-0000-0000-0000-000000000000",
            status="approved",
            decision="rejected",
        )


def test_create_approval_rejected_status_wrong_decision(db):
    with pytest.raises(
        ValueError,
        match="Rejected status requires rejected decision",
    ):
        create_approval_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            requested_from="00000000-0000-0000-0000-000000000000",
            status="rejected",
            decision="approved",
        )


def test_get_approval_not_found(db):
    with pytest.raises(
        ValueError,
        match="Approval not found",
    ):
        get_approval_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )


def test_get_approvals_invalid_limit(db):
    with pytest.raises(
        ValueError,
        match="Limit must be greater than 0",
    ):
        get_approvals_service(
            db,
            0,
        )


def test_update_approval_invalid_status(db):
    with pytest.raises(
        ValueError,
        match="Invalid approval status",
    ):
        update_approval_service(
            db=db,
            approval_id="00000000-0000-0000-0000-000000000000",
            status="invalid",
        )


def test_update_approval_invalid_decision(db):
    with pytest.raises(
        ValueError,
        match="Invalid approval decision",
    ):
        update_approval_service(
            db=db,
            approval_id="00000000-0000-0000-0000-000000000000",
            decision="invalid",
        )


def test_update_approval_empty_comment(db):
    with pytest.raises(
        ValueError,
        match="Comment cannot be empty",
    ):
        update_approval_service(
            db=db,
            approval_id="00000000-0000-0000-0000-000000000000",
            comment="",
        )


def test_update_approval_not_found(db):
    with pytest.raises(
        ValueError,
        match="Approval not found",
    ):
        update_approval_service(
            db=db,
            approval_id="00000000-0000-0000-0000-000000000000",
            status="pending",
        )


def test_get_approvals_by_task(db):
    result = get_approvals_by_task_service(
        db,
        "00000000-0000-0000-0000-000000000000",
    )

    assert result == []


def test_get_approvals_by_user(db):
    result = get_approvals_by_user_service(
        db,
        "00000000-0000-0000-0000-000000000000",
    )

    assert result == []


def test_delete_approval_not_found(db):
    with pytest.raises(
        ValueError,
        match="Approval not found",
    ):
        delete_approval_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )