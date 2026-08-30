from __future__ import annotations

from typing import Iterable

from fastapi import Depends, Header, HTTPException

from services.backend.app.db.repository import repo


def get_current_user(
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    authorization: str | None = Header(default=None),
):
    """Resolve the current local identity.

    The current SIH development build uses the browser-local authenticated email
    as the identity bridge. The backend database owns the user's role. A real
    deployment should replace this bridge with verified Firebase/OIDC/JWT claims.
    """
    value = (x_user_email or "").strip().lower()
    if not value and authorization and authorization.lower().startswith("bearer "):
        value = ""

    if not value or "@" not in value:
        raise HTTPException(status_code=401, detail="Authenticated user identity is required")

    return repo.get_or_create_user(value)


def require_roles(*roles: str):
    allowed = {role.strip().lower() for role in roles}

    def dependency(current_user=Depends(get_current_user)):
        role = str(getattr(current_user, "role", "operator")).lower()
        if role not in allowed:
            raise HTTPException(status_code=403, detail="This action is not permitted for your role")
        return current_user

    return dependency
