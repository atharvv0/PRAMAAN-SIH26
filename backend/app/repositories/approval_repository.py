from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.approval import Approval


def create_approval(
    db: Session,
    task_id,
    requested_from,
    status: str = "pending",
    decision: str = None,
    comment: str = None,
):
    approval = Approval(
        task_id=task_id,
        requested_from=requested_from,
        status=status,
        decision=decision,
        comment=comment,
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


def get_approval(
    db: Session,
    approval_id,
):
    return (
        db.query(Approval)
        .filter(
            Approval.approval_id == approval_id
        )
        .first()
    )


def get_approvals_by_task(
    db: Session,
    task_id,
):
    return (
        db.query(Approval)
        .filter(
            Approval.task_id == task_id
        )
        .order_by(Approval.approval_id)
        .all()
    )


def get_approvals_by_user(
    db: Session,
    requested_from,
):
    return (
        db.query(Approval)
        .filter(
            Approval.requested_from == requested_from
        )
        .order_by(Approval.approval_id)
        .all()
    )


def get_approvals(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Approval)
        .limit(limit)
        .all()
    )


def update_approval(
    db: Session,
    approval_id,
    status: str = None,
    decision: str = None,
    comment: str = None,
):
    approval = get_approval(
        db,
        approval_id,
    )

    if approval is None:
        return None

    if status is not None:
        approval.status = status

    if decision is not None:
        approval.decision = decision

    if comment is not None:
        approval.comment = comment

    if decision is not None:
        approval.decided_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(approval)

    return approval


def delete_approval(
    db: Session,
    approval_id,
):
    approval = get_approval(
        db,
        approval_id,
    )

    if approval is None:
        return False

    db.delete(approval)
    db.commit()

    return True