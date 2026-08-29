from services.governance.audit.log import default_audit_log
from services.governance.security.access_request import (
    access_requests,
    create_access_request,
)
from services.governance.security.access_approval import (
    approve_request,
    deny_request,
)
from services.governance.security.access_grants import (
    access_grants,
    grant_access,
    revoke_access,
)


def setup_function():
    access_requests.clear()
    access_grants.clear()
    default_audit_log.clear()


def test_create_access_request_starts_pending():
    request = create_access_request(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission="read_document",
    )

    assert request.status == "PENDING"
    assert request in access_requests

    # ACCESS_REQUEST is still recorded by the legacy workflow.
    # This assertion remains temporarily unchanged until access_request.py
    # is migrated to the canonical AuditLog.
    from services.governance.security.audit import audit_events

    assert audit_events[-1]["action"] == "ACCESS_REQUEST"
    assert audit_events[-1]["decision"] == "PENDING"


def test_approved_request_can_become_active_grant():
    request = create_access_request(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission="read_document",
    )

    assert approve_request(request) == "ACCESS APPROVED"
    assert request.status == "APPROVED"

    assert grant_access(request) == "ACCESS GRANTED"

    assert len(access_grants) == 1
    assert access_grants[0]["status"] == "ACTIVE"

    events = default_audit_log.all()
    assert events[-1].action == "ACCESS_GRANT"
    assert events[-1].decision == "allow"


def test_denied_request_cannot_become_grant():
    request = create_access_request(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission="read_document",
    )

    assert deny_request(request) == "ACCESS DENIED"
    assert request.status == "DENIED"

    assert grant_access(request) == "ACCESS NOT GRANTED"
    assert len(access_grants) == 0


def test_request_cannot_be_approved_twice():
    request = create_access_request(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission="read_document",
    )

    assert approve_request(request) == "ACCESS APPROVED"
    assert approve_request(request) == "REQUEST ALREADY FINALIZED"


def test_request_cannot_be_denied_after_approval():
    request = create_access_request(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission="read_document",
    )

    assert approve_request(request) == "ACCESS APPROVED"
    assert deny_request(request) == "REQUEST ALREADY FINALIZED"


def test_grant_can_be_revoked():
    request = create_access_request(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission="read_document",
    )

    assert approve_request(request) == "ACCESS APPROVED"
    assert grant_access(request) == "ACCESS GRANTED"

    assert revoke_access(
        "team-a",
        "team-b",
        "document-1",
        "read_document",
    ) == "ACCESS REVOKED"

    assert access_grants[0]["status"] == "REVOKED"

    events = default_audit_log.all()
    assert events[-1].action == "ACCESS_REVOKE"
    assert events[-1].decision == "deny"