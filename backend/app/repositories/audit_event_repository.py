from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def create_audit_event(
    db: Session,
    actor_type: str,
    action: str,
    target_type: str,
    actor_id=None,
    target_id=None,
    decision: str = None,
    reason: str = None,
):
    event = AuditEvent(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        decision=decision,
        reason=reason,
        created_at=datetime.now(timezone.utc),
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_audit_event(
    db: Session,
    audit_event_id,
):
    return (
        db.query(AuditEvent)
        .filter(
            AuditEvent.audit_event_id == audit_event_id
        )
        .first()
    )


def get_audit_events(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(AuditEvent)
        .order_by(AuditEvent.created_at)
        .limit(limit)
        .all()
    )


def get_audit_events_by_actor(
    db: Session,
    actor_type: str,
    actor_id=None,
):
    query = db.query(AuditEvent).filter(
        AuditEvent.actor_type == actor_type
    )

    if actor_id is not None:
        query = query.filter(
            AuditEvent.actor_id == actor_id
        )

    return (
        query
        .order_by(AuditEvent.created_at)
        .all()
    )


def get_audit_events_by_target(
    db: Session,
    target_type: str,
    target_id=None,
):
    query = db.query(AuditEvent).filter(
        AuditEvent.target_type == target_type
    )

    if target_id is not None:
        query = query.filter(
            AuditEvent.target_id == target_id
        )

    return (
        query
        .order_by(AuditEvent.created_at)
        .all()
    )