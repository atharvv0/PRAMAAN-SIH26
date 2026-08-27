from app.db.session import SessionLocal

from app.repositories.audit_event_repository import (
    create_audit_event,
    get_audit_event,
    get_audit_events,
    get_audit_events_by_actor,
    get_audit_events_by_target,
)

from app.models.user import User
from app.models.task import Task


db = SessionLocal()

try:

    user = db.query(User).first()
    task = db.query(Task).first()

    if user is None:
        print("No user found.")

    elif task is None:
        print("No task found.")

    else:

        event = create_audit_event(
            db=db,
            actor_type="user",
            actor_id=user.user_id,
            action="repository_test",
            target_type="task",
            target_id=task.task_id,
            decision="approved",
            reason="Testing audit event repository.",
        )

        print("Created Audit Event:")
        print(
            "Audit Event ID:",
            event.audit_event_id,
        )
        print(
            "Actor Type:",
            event.actor_type,
        )
        print(
            "Actor ID:",
            event.actor_id,
        )
        print(
            "Action:",
            event.action,
        )
        print(
            "Target Type:",
            event.target_type,
        )
        print(
            "Target ID:",
            event.target_id,
        )
        print(
            "Decision:",
            event.decision,
        )
        print(
            "Reason:",
            event.reason,
        )
        print(
            "Created At:",
            event.created_at,
        )

        found = get_audit_event(
            db,
            event.audit_event_id,
        )

        print("\nGet Audit Event:")
        print(found.action)

        actor_events = get_audit_events_by_actor(
            db,
            actor_type="user",
            actor_id=user.user_id,
        )

        print(
            "\nEvents for Actor:",
            len(actor_events),
        )

        target_events = get_audit_events_by_target(
            db,
            target_type="task",
            target_id=task.task_id,
        )

        print(
            "Events for Target:",
            len(target_events),
        )

        all_events = get_audit_events(db)

        print(
            "Total Audit Events:",
            len(all_events),
        )

finally:
    db.close()