from __future__ import annotations

from dataclasses import dataclass


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
        declares_network_access: bool = False,
    ) -> PolicyDecision:
        if declares_network_access:
            return PolicyDecision(
                allow=False,
                reason="Network access is denied by the default sovereignty policy",
            )

        return PolicyDecision(
            allow=True,
            reason="Tool call allowed by the default policy",
        )


default_policy_engine = PolicyEngine()
