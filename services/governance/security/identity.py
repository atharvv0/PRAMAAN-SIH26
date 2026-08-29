from dataclasses import dataclass

from .rbac import Role


@dataclass(frozen=True)
class SecurityIdentity:
    user_id: str
    role: Role
    team_id: str


DEMO_IDENTITIES = {
    # Existing orchestrator/backend test identity.
    "user_1": SecurityIdentity(
        user_id="user_1",
        role=Role.USER,
        team_id="demo-team",
    ),

    # Governance demo identities.
    "demo-user": SecurityIdentity(
        user_id="demo-user",
        role=Role.USER,
        team_id="demo-team",
    ),

    "demo-reviewer": SecurityIdentity(
        user_id="demo-reviewer",
        role=Role.REVIEWER,
        team_id="demo-team",
    ),

    "demo-admin": SecurityIdentity(
        user_id="demo-admin",
        role=Role.ADMIN,
        team_id="admin-team",
    ),
}


def resolve_identity(user_id: str) -> SecurityIdentity:
    identity = DEMO_IDENTITIES.get(user_id)

    if identity is None:
        raise ValueError(f"Unknown security identity: {user_id}")

    return identity