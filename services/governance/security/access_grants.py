from services.governance.audit.log import AuditLog, default_audit_log


access_grants = []


def grant_access(
    request,
    audit_log: AuditLog = default_audit_log,
):
    if request.status != "APPROVED":
        return "ACCESS NOT GRANTED"

    for grant in access_grants:
        if (
            grant["requester_team"] == request.requester_team
            and grant["target_team"] == request.target_team
            and grant["resource"] == request.resource
            and grant["permission"] == request.permission
            and grant["status"] == "ACTIVE"
        ):
            return "ACCESS ALREADY GRANTED"

    grant = {
        "requester_team": request.requester_team,
        "target_team": request.target_team,
        "resource": request.resource,
        "permission": request.permission,
        "status": "ACTIVE",
    }

    access_grants.append(grant)

    audit_log.record(
        actor=request.requester_team,
        action="ACCESS_GRANT",
        target=request.resource,
        decision="allow",
        policy_reason=(
            f"Approved cross-team access from "
            f"{request.requester_team} to {request.target_team}"
        ),
    )

    return "ACCESS GRANTED"


def has_granted_access(
    requester_team,
    target_team,
    resource,
    permission,
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
    permission,
    audit_log: AuditLog = default_audit_log,
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

            audit_log.record(
                actor=requester_team,
                action="ACCESS_REVOKE",
                target=resource,
                decision="deny",
                policy_reason=(
                    f"Access revoked from "
                    f"{requester_team} to {target_team}"
                ),
            )

            return "ACCESS REVOKED"

    return "ACTIVE GRANT NOT FOUND"