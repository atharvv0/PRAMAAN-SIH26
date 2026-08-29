from dataclasses import dataclass
from datetime import datetime

from .audit import audit_events


@dataclass
class AccessRequest:
    requester_team: str
    target_team: str
    resource: str
    permission: str
    status: str = "PENDING"
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


access_requests = []


def create_access_request(
    requester_team,
    target_team,
    resource,
    permission
):
    request = AccessRequest(
        requester_team=requester_team,
        target_team=target_team,
        resource=resource,
        permission=permission
    )

    access_requests.append(request)

    audit_events.append({
        "timestamp": datetime.now().isoformat(),
        "action": "ACCESS_REQUEST",
        "requester_team": requester_team,
        "target_team": target_team,
        "resource": resource,
        "permission": permission,
        "decision": "PENDING"
    })

    return request