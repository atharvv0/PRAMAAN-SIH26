from pathlib import Path

from .rbac import Permission
from .authorization import authorize_workspace
from .audit import log_event


def check_access(
    role,
    user_team_id,
    workspace_team_id,
    permission,
    file_path
):
    allowed = authorize_workspace(
        role,
        user_team_id,
        workspace_team_id,
        permission,
        file_path
    )

    decision = "ALLOW" if allowed else "DENY"

    reason = (
        "Workspace and permission access granted"
        if allowed
        else "Workspace or permission access denied"
    )

    log_event(
        role,
        permission,
        decision,
        reason,
        user_team_id,
        workspace_team_id,
        file_path
    )

    return allowed


def create_file(role, user_team_id, workspace_team_id, file_path, content):
    if not check_access(
        role,
        user_team_id,
        workspace_team_id,
        Permission.CREATE_DOCUMENT,
        file_path
    ):
        return "DENIED"

    Path(file_path).write_text(content)
    return "FILE CREATED"


def read_file(role, user_team_id, workspace_team_id, file_path):
    if not check_access(
        role,
        user_team_id,
        workspace_team_id,
        Permission.READ_DOCUMENT,
        file_path
    ):
        return "DENIED"

    return Path(file_path).read_text()


def modify_file(role, user_team_id, workspace_team_id, file_path, content):
    if not check_access(
        role,
        user_team_id,
        workspace_team_id,
        Permission.MODIFY_DOCUMENT,
        file_path
    ):
        return "DENIED"

    Path(file_path).write_text(content)
    return "FILE MODIFIED"


def delete_file(role, user_team_id, workspace_team_id, file_path):
    if not check_access(
        role,
        user_team_id,
        workspace_team_id,
        Permission.DELETE_DOCUMENT,
        file_path
    ):
        return "DENIED"

    Path(file_path).unlink()
    return "FILE DELETED"