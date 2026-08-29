from services.governance.security.authorization import authorize_workspace
from services.governance.security.rbac import Role, Permission
from services.governance.security.access_grants import (
    access_grants,
    grant_access,
    revoke_access,
)
from services.governance.security.access_request import AccessRequest


def setup_function():
    access_grants.clear()


def test_admin_can_access_any_workspace():
    result = authorize_workspace(
        role=Role.ADMIN,
        user_team_id="team-a",
        workspace_team_id="team-b",
        permission=Permission.READ_DOCUMENT,
    )

    assert result is True


def test_same_team_user_can_access_workspace():
    result = authorize_workspace(
        role=Role.USER,
        user_team_id="team-a",
        workspace_team_id="team-a",
        permission=Permission.READ_DOCUMENT,
    )

    assert result is True


def test_cross_team_user_is_denied_without_grant():
    result = authorize_workspace(
        role=Role.USER,
        user_team_id="team-a",
        workspace_team_id="team-b",
        permission=Permission.READ_DOCUMENT,
        resource="document-1",
    )

    assert result is False


def test_cross_team_access_can_be_granted():
    request = AccessRequest(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission=Permission.READ_DOCUMENT.value,
        status="APPROVED",
    )

    assert grant_access(request) == "ACCESS GRANTED"

    result = authorize_workspace(
        role=Role.USER,
        user_team_id="team-a",
        workspace_team_id="team-b",
        permission=Permission.READ_DOCUMENT,
        resource="document-1",
    )

    assert result is True


def test_revoked_grant_removes_access():
    request = AccessRequest(
        requester_team="team-a",
        target_team="team-b",
        resource="document-1",
        permission=Permission.READ_DOCUMENT.value,
        status="APPROVED",
    )

    assert grant_access(request) == "ACCESS GRANTED"

    assert revoke_access(
        "team-a",
        "team-b",
        "document-1",
        Permission.READ_DOCUMENT.value,
    ) == "ACCESS REVOKED"

    result = authorize_workspace(
        role=Role.USER,
        user_team_id="team-a",
        workspace_team_id="team-b",
        permission=Permission.READ_DOCUMENT,
        resource="document-1",
    )

    assert result is False