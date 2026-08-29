from datetime import datetime


audit_events = []


def log_event(
    role,
    permission,
    decision,
    reason,
    team_id=None,
    workspace_id=None,
    resource=None
):
    event = {
        "timestamp": datetime.now().isoformat(),
        "role": role.value,
        "permission": permission.value,
        "decision": decision,
        "reason": reason,
        "team_id": team_id,
        "workspace_id": workspace_id,
        "resource": resource
    }

    audit_events.append(event)

    return event