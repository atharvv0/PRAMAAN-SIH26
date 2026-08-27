from sqlalchemy.orm import Session

from app.repositories.approval_repository import (
    create_approval,
    get_approval,
    get_approvals_by_task,
    get_approvals_by_user,
    get_approvals,
    update_approval,
    delete_approval,
)


VALID_STATUSES = {
    "pending",
    "approved",
    "rejected",
}


VALID_DECISIONS = {
    "approved",
    "rejected",
}


def create_approval_service(
    db: Session,
    task_id,
    requested_from,
    status: str = "pending",
    decision: str = None,
    comment: str = None,
):
    if status not in VALID_STATUSES:
        raise ValueError(
            "Invalid approval status."
        )

    if (
        decision is not None
        and decision not in VALID_DECISIONS
    ):
        raise ValueError(
            "Invalid approval decision."
        )

    if status == "approved" and decision != "approved":
        raise ValueError(
            "Approved status requires approved decision."
        )

    if status == "rejected" and decision != "rejected":
        raise ValueError(
            "Rejected status requires rejected decision."
        )

    return create_approval(
        db=db,
        task_id=task_id,
        requested_from=requested_from,
        status=status,
        decision=decision,
        comment=(
            comment.strip()
            if comment is not None
            else None
        ),
    )


def get_approval_service(
    db: Session,
    approval_id,
):
    approval = get_approval(
        db,
        approval_id,
    )

    if approval is None:
        raise ValueError(
            "Approval not found."
        )

    return approval


def get_approvals_by_task_service(
    db: Session,
    task_id,
):
    return get_approvals_by_task(
        db,
        task_id,
    )


def get_approvals_by_user_service(
    db: Session,
    requested_from,
):
    return get_approvals_by_user(
        db,
        requested_from,
    )


def get_approvals_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_approvals(
        db,
        limit=limit,
    )


def update_approval_service(
    db: Session,
    approval_id,
    status: str = None,
    decision: str = None,
    comment: str = None,
):
    if (
        status is not None
        and status not in VALID_STATUSES
    ):
        raise ValueError(
            "Invalid approval status."
        )

    if (
        decision is not None
        and decision not in VALID_DECISIONS
    ):
        raise ValueError(
            "Invalid approval decision."
        )

    if comment is not None and not comment.strip():
        raise ValueError(
            "Comment cannot be empty."
        )

    approval = update_approval(
        db=db,
        approval_id=approval_id,
        status=status,
        decision=decision,
        comment=(
            comment.strip()
            if comment is not None
            else None
        ),
    )

    if approval is None:
        raise ValueError(
            "Approval not found."
        )

    return approval


def delete_approval_service(
    db: Session,
    approval_id,
):
    deleted = delete_approval(
        db,
        approval_id,
    )

    if not deleted:
        raise ValueError(
            "Approval not found."
        )

    return True