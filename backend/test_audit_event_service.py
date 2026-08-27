import pytest

from app.services.audit_event_service import (
    create_audit_event_service,
    get_audit_event_service,
    get_audit_events_service,
    get_audit_events_by_actor_service,
    get_audit_events_by_target_service,
)


def test_create_audit_event_empty_actor_type(db):

    with pytest.raises(
        ValueError,
        match="Actor type is required",
    ):
        create_audit_event_service(
            db=db,
            actor_type="",
            action="create",
            target_type="task",
        )


def test_create_audit_event_empty_action(db):

    with pytest.raises(
        ValueError,
        match="Action is required",
    ):
        create_audit_event_service(
            db=db,
            actor_type="user",
            action="",
            target_type="task",
        )


def test_create_audit_event_empty_target_type(db):

    with pytest.raises(
        ValueError,
        match="Target type is required",
    ):
        create_audit_event_service(
            db=db,
            actor_type="user",
            action="create",
            target_type="",
        )


def test_create_audit_event_invalid_actor_type(db):

    with pytest.raises(
        ValueError,
        match="Invalid actor type",
    ):
        create_audit_event_service(
            db=db,
            actor_type="invalid",
            action="create",
            target_type="task",
        )


def test_get_audit_event_not_found(db):

    with pytest.raises(
        ValueError,
        match="Audit event not found",
    ):
        get_audit_event_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )


def test_get_audit_events_invalid_limit(db):

    with pytest.raises(
        ValueError,
        match="Limit must be greater than 0",
    ):
        get_audit_events_service(
            db,
            0,
        )


def test_get_audit_events_by_actor_empty_actor_type(db):

    with pytest.raises(
        ValueError,
        match="Actor type is required",
    ):
        get_audit_events_by_actor_service(
            db=db,
            actor_type="",
        )


def test_get_audit_events_by_actor_invalid_actor_type(db):

    with pytest.raises(
        ValueError,
        match="Invalid actor type",
    ):
        get_audit_events_by_actor_service(
            db=db,
            actor_type="invalid",
        )


def test_get_audit_events_by_target_empty_target_type(db):

    with pytest.raises(
        ValueError,
        match="Target type is required",
    ):
        get_audit_events_by_target_service(
            db=db,
            target_type="",
        )