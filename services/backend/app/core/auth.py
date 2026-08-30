from __future__ import annotations

from fastapi import Depends, Header, HTTPException

from services.backend.app.db.repository import repo


def get_current_user(
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    authorization: str | None = Header(default=None),
):
    """Resolve the current local-development identity.

    For local development, the frontend supplies X-User-Email after login.
    The database owns the user's role. Production should replace this bridge
    with verification of Firebase/OIDC/JWT claims.
    """
    value = (x_user_email or "").strip().lower()
    if not value and authorization and authorization.lower().startswith("bearer "):
        # Do not treat an opaque bearer token as an email. Plug in a real
        # token verifier for production authentication.
        value = ""

    if not value or "@" not in value:
        raise HTTPException(status_code=401, detail="Authenticated user identity is required")

    return repo.get_or_create_user(value)


def require_roles(*roles: str):
    """FastAPI dependency that permits only the supplied database roles."""
    allowed = {role.strip().lower() for role in roles}

    if not allowed:
        raise ValueError("require_roles() requires at least one role")

    def dependency(current_user=Depends(get_current_user)):
        role = str(getattr(current_user, "role", "operator")).strip().lower()
        if role not in allowed:
            raise HTTPException(
                status_code=403,
                detail="This action is not permitted for your role",
            )
        return current_user

    return dependency
