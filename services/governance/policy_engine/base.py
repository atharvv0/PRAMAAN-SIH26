from __future__ import annotations

from dataclasses import dataclass

from services.governance.security.identity import resolve_identity
from services.governance.security.rbac import Permission, is_allowed


@dataclass(frozen=True)
class PolicyDecision:
    allow: bool
    reason: str


class PolicyEngine:
    def check(
        self,
        actor: str,
        action: str,
        tool_id: str,
        required_permissions: list[str] | None = None,
        declares_network_access: bool = False,
    ) -> PolicyDecision:
        # Sovereignty rule always comes first.
        if declares_network_access:
            return PolicyDecision(
                allow=False,
                reason="Network access is denied by the default sovereignty policy",
            )

        identity = resolve_identity(actor)
        permissions = required_permissions or []

        # No additional permission required.
        if not permissions:
            return PolicyDecision(
                allow=True,
                reason="Tool requires no additional permissions",
            )

        permission_map = {
            "file.read": Permission.READ_DOCUMENT,
            "file.create": Permission.CREATE_DOCUMENT,
            "file.modify": Permission.MODIFY_DOCUMENT,
            "file.delete": Permission.DELETE_DOCUMENT,
            "tool.execute": Permission.EXECUTE_TOOL,
            "document.approve": Permission.APPROVE_DOCUMENT,
            "user.manage": Permission.MANAGE_USERS,
        }

        for required in permissions:
            permission = permission_map.get(required)

            if permission is None:
                return PolicyDecision(
                    allow=False,
                    reason=f"Unknown required permission: {required}",
                )

            if not is_allowed(identity.role, permission):
                return PolicyDecision(
                    allow=False,
                    reason=(
                        f"Role '{identity.role.value}' is not authorized "
                        f"for permission '{required}'"
                    ),
                )

        return PolicyDecision(
            allow=True,
            reason=(
                f"Role '{identity.role.value}' is authorized "
                f"for tool '{tool_id}'"
            ),
        )


default_policy_engine = PolicyEngine()