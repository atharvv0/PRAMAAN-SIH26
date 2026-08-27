from datetime import datetime

from .audit import audit_events


def request_network_access(role, destination):
    decision = "DENY"
    reason = "Outbound network access is blocked by default"

    event = {
        "timestamp": datetime.now().isoformat(),
        "role": role.value,
        "permission": "network_access",
        "decision": decision,
        "reason": reason,
        "destination": destination
    }

    audit_events.append(event)

    if decision == "DENY":
        return {
            "status": "BLOCKED",
            "event": event
        }

    return {
        "status": "ALLOWED",
        "event": event
    }