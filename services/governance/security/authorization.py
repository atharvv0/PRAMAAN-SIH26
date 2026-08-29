from .rbac import Role, Permission, is_allowed
from .access import can_access_workspace
from .access_grants import has_granted_access


def authorize_workspace(
    role,
    user_team_id,
    workspace_team_id,
    permission,
    resource=None
):
    # Admin has highest authority
    if role == Role.ADMIN:
        return True

    # Same-team access
    if can_access_workspace(role, user_team_id, workspace_team_id):
        return is_allowed(role, permission)

    # Cross-team access requires an approved grant
    if resource is not None:
        return has_granted_access(
            user_team_id,
            workspace_team_id,
            resource,
            permission.value
        )

    return False