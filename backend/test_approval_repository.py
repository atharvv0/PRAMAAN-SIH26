from app.db.session import SessionLocal

from app.repositories.approval_repository import (
    create_approval,
    get_approval,
    get_approvals_by_task,
    get_approvals_by_user,
    get_approvals,
    update_approval,
)

from app.models.task import Task
from app.models.user import User


db = SessionLocal()

try:

    task = db.query(Task).first()
    user = db.query(User).first()

    if task is None:
        print("No task found.")

    elif user is None:
        print("No user found.")

    else:

        approval = create_approval(
            db=db,
            task_id=task.task_id,
            requested_from=user.user_id,
            status="pending",
            comment="Repository test approval.",
        )

        print("Created Approval:")
        print("Approval ID:", approval.approval_id)
        print("Task ID:", approval.task_id)
        print("Requested From:", approval.requested_from)
        print("Status:", approval.status)
        print("Decision:", approval.decision)
        print("Comment:", approval.comment)
        print("Decided At:", approval.decided_at)

        found = get_approval(
            db,
            approval.approval_id,
        )

        print("\nGet Approval:")
        print(found.status)

        task_approvals = get_approvals_by_task(
            db,
            task.task_id,
        )

        print(
            "\nApprovals for Task:",
            len(task_approvals),
        )

        user_approvals = get_approvals_by_user(
            db,
            user.user_id,
        )

        print(
            "Approvals for User:",
            len(user_approvals),
        )

        updated = update_approval(
            db,
            approval.approval_id,
            status="approved",
            decision="approved",
            comment="Repository test approved.",
        )

        print("\nUpdated Approval:")
        print("Status:", updated.status)
        print("Decision:", updated.decision)
        print("Comment:", updated.comment)
        print("Decided At:", updated.decided_at)

        all_approvals = get_approvals(db)

        print(
            "\nTotal Approvals:",
            len(all_approvals),
        )

finally:
    db.close()