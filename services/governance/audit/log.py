from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    target: str
    decision: str
    policy_reason: str
    timestamp: str


class AuditLog:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(
        self,
        actor: str,
        action: str,
        target: str,
        decision: str,
        policy_reason: str,
    ) -> AuditEvent:
        event = AuditEvent(
            actor=actor,
            action=action,
            target=target,
            decision=decision,
            policy_reason=policy_reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._events.append(event)
        return event

    def all(self) -> list[AuditEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()


default_audit_log = AuditLog()