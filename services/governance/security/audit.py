from datetime import datetime


audit_events = []


def log_event(role, permission, decision, reason):
    event = {
        "timestamp": datetime.now().isoformat(),
        "role": role.value,
        "permission": permission.value,
        "decision": decision,
        "reason": reason
    }

    audit_events.append(event)
    return event