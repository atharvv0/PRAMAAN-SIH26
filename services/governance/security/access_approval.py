from datetime import datetime

from .access_request import access_requests
from .audit import audit_events


def approve_request(request):
    if request not in access_requests:
        return "REQUEST NOT FOUND"

    if request.status != "PENDING":
        return "REQUEST ALREADY FINALIZED"

    request.status = "APPROVED"

    audit_events.append({
        "timestamp": datetime.now().isoformat(),
        "action": "ACCESS_APPROVAL",
        "requester_team": request.requester_team,
        "target_team": request.target_team,
        "resource": request.resource,
        "permission": request.permission,
        "decision": "APPROVED"
    })

    return "ACCESS APPROVED"


def deny_request(request):
    if request not in access_requests:
        return "REQUEST NOT FOUND"

    if request.status != "PENDING":
        return "REQUEST ALREADY FINALIZED"

    request.status = "DENIED"

    audit_events.append({
        "timestamp": datetime.now().isoformat(),
        "action": "ACCESS_APPROVAL",
        "requester_team": request.requester_team,
        "target_team": request.target_team,
        "resource": request.resource,
        "permission": request.permission,
        "decision": "DENIED"
    })

    return "ACCESS DENIED"