from sqlalchemy.orm import Session

from app.repositories.audit_event_repository import (
    create_audit_event,
    get_audit_event,
    get_audit_events,
    get_audit_events_by_actor,
    get_audit_events_by_target,
)


VALID_ACTOR_TYPES = {
    "user",
    "agent",
    "system",
}


def create_audit_event_service(
    db: Session,
    actor_type: str,
    action: str,
    target_type: str,
    actor_id=None,
    target_id=None,
    decision: str = None,
    reason: str = None,
):
    if not actor_type or not actor_type.strip():
        raise ValueError(
            "Actor type is required."
        )

    if not action or not action.strip():
        raise ValueError(
            "Action is required."
        )

    if not target_type or not target_type.strip():
        raise ValueError(
            "Target type is required."
        )

    actor_type = actor_type.strip().lower()

    if actor_type not in VALID_ACTOR_TYPES:
        raise ValueError(
            "Invalid actor type."
        )

    return create_audit_event(
        db=db,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action.strip(),
        target_type=target_type.strip(),
        target_id=target_id,
        decision=(
            decision.strip()
            if decision is not None
            else None
        ),
        reason=(
            reason.strip()
            if reason is not None
            else None
        ),
    )


def get_audit_event_service(
    db: Session,
    audit_event_id,
):
    event = get_audit_event(
        db,
        audit_event_id,
    )

    if event is None:
        raise ValueError(
            "Audit event not found."
        )

    return event


def get_audit_events_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_audit_events(
        db,
        limit=limit,
    )


def get_audit_events_by_actor_service(
    db: Session,
    actor_type: str,
    actor_id=None,
):
    if not actor_type or not actor_type.strip():
        raise ValueError(
            "Actor type is required."
        )

    actor_type = actor_type.strip().lower()

    if actor_type not in VALID_ACTOR_TYPES:
        raise ValueError(
            "Invalid actor type."
        )

    return get_audit_events_by_actor(
        db,
        actor_type,
        actor_id,
    )


def get_audit_events_by_target_service(
    db: Session,
    target_type: str,
    target_id=None,
):
    if not target_type or not target_type.strip():
        raise ValueError(
            "Target type is required."
        )

    return get_audit_events_by_target(
        db,
        target_type.strip(),
        target_id,
    )