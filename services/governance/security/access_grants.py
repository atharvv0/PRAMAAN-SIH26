from datetime import datetime

from .audit import audit_events


access_grants = []


def grant_access(request):
    if request.status != "APPROVED":
        return "ACCESS NOT GRANTED"

    grant = {
        "requester_team": request.requester_team,
        "target_team": request.target_team,
        "resource": request.resource,
        "permission": request.permission,
        "status": "ACTIVE"
    }

    access_grants.append(grant)

    audit_events.append({
        "timestamp": datetime.now().isoformat(),
        "action": "ACCESS_GRANT",
        "requester_team": request.requester_team,
        "target_team": request.target_team,
        "resource": request.resource,
        "permission": request.permission,
        "decision": "GRANTED"
    })

    return "ACCESS GRANTED"


def has_granted_access(
    requester_team,
    target_team,
    resource,
    permission
):
    for grant in access_grants:
        if (
            grant["requester_team"] == requester_team
            and grant["target_team"] == target_team
            and grant["resource"] == resource
            and grant["permission"] == permission
            and grant["status"] == "ACTIVE"
        ):
            return True

    return False


def revoke_access(
    requester_team,
    target_team,
    resource,
    permission
):
    for grant in access_grants:
        if (
            grant["requester_team"] == requester_team
            and grant["target_team"] == target_team
            and grant["resource"] == resource
            and grant["permission"] == permission
            and grant["status"] == "ACTIVE"
        ):
            grant["status"] = "REVOKED"

            audit_events.append({
                "timestamp": datetime.now().isoformat(),
                "action": "ACCESS_REVOKE",
                "requester_team": requester_team,
                "target_team": target_team,
                "resource": resource,
                "permission": permission,
                "decision": "REVOKED"
            })

            return "ACCESS REVOKED"

    return "ACTIVE GRANT NOT FOUND"