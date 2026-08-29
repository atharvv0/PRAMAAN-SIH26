from .rbac import Role


def can_access_workspace(role, user_team_id, workspace_team_id):
    # Admin has organization-level authority
    if role == Role.ADMIN:
        return True

    # Normal users can access only their own team's workspace
    return user_team_id == workspace_team_id