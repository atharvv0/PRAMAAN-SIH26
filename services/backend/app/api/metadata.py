from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends

from ..db.database import Workspace
from services.backend.app.core.auth import get_current_user, require_roles
from services.backend.app.db.repository import repo
from services.governance.audit.log import default_audit_log
from services.model_control.registry.registry_instance import default_registry as model_registry
from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter

router = APIRouter(tags=["metadata"])


def _network_events():
    return [{"id": f"network-{i}", "timestamp": e.timestamp, "kind": "policy_decision", "message": e.policy_reason, "decision": "blocked" if e.decision == "deny" else "allowed", "reason": e.policy_reason, "destination": e.target} for i, e in enumerate(default_audit_log.all(), 1)]


@router.get("/workspaces")
def get_workspaces(current_user=Depends(get_current_user)):
    return repo.list_workspaces()


@router.get("/workspaces/{workspace_id}")
def get_workspace(workspace_id: str, current_user=Depends(get_current_user)):
    item = next((x for x in repo.list_workspaces() if x["id"] == workspace_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="workspace not found")
    return item


@router.get("/overview")
def get_overview(current_user=Depends(get_current_user)):
    role = str(getattr(current_user, "role", "operator")).lower()
    tasks = repo.list_tasks(user_id=current_user.user_id, include_all=role in {"reviewer", "admin"})
    approvals = repo.approvals(current_user.user_id, include_all=role in {"reviewer", "admin"})
    deliverables = repo.deliverables(user_id=current_user.user_id)
    events = repo.audits(user_id=current_user.user_id)
    models = get_models()
    net = _network_events()
    return {"sovereignty": _sovereignty_payload(models, sum(1 for x in net if x.get("decision") == "blocked")), "activeTasks": sum(1 for t in tasks if t["status"] in {"queued", "running", "awaiting_approval"}), "pendingApprovals": len(approvals), "recentDeliverables": len(deliverables), "recentSecurityEvents": sum(1 for x in net if x.get("decision") == "blocked"), "activity": events[:20], "currentTasks": tasks[:20], "networkEvents": net}


@router.get("/evidence")
def get_evidence(taskId: str | None = None, runId: str | None = None, current_user=Depends(get_current_user)):
    if taskId:
        owner = repo.get_task_owner(taskId)
        if str(owner) != str(current_user.user_id) and getattr(current_user, "role", "operator") not in {"reviewer", "admin"}:
            raise HTTPException(status_code=403, detail="not authorized for this task")
    user_scope = None if getattr(current_user, "role", "operator") in {"reviewer", "admin"} and not taskId else current_user.user_id
    return repo.evidence(taskId, user_scope)


@router.get("/evidence/{evidence_id}")
def get_evidence_by_id(evidence_id: str, current_user=Depends(get_current_user)):
    found = next((x for x in repo.evidence(user_id=current_user.user_id) if x["id"] == evidence_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="evidence not found")
    return found


@router.get("/audit")
def get_audit(taskId: str | None = None, current_user=Depends(require_roles("admin"))):
    if taskId:
        owner = repo.get_task_owner(taskId)
        if str(owner) != str(current_user.user_id):
            raise HTTPException(status_code=403, detail="not authorized for this task")
    return repo.audits(taskId, current_user.user_id)




@router.get("/auth/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.user_id),
        "email": current_user.email,
        "name": current_user.display_name,
        "role": getattr(current_user, "role", "operator"),
        "active": bool(current_user.is_active),
    }


@router.get("/admin/users")
def list_users(current_user=Depends(require_roles("admin"))):
    from ..db.database import User, session_scope
    with session_scope() as s:
        users = s.scalars(__import__('sqlalchemy').select(User).order_by(User.created_at)).all()
        return [
            {"id": str(u.user_id), "email": u.email, "name": u.display_name, "role": getattr(u, "role", "operator"), "active": bool(u.is_active)}
            for u in users
        ]


@router.patch("/admin/users/{user_id}/role")
def set_user_role(user_id: str, payload: dict, current_user=Depends(require_roles("admin"))):
    role = str(payload.get("role", "")).lower()
    if role not in {"operator", "reviewer", "admin"}:
        raise HTTPException(status_code=422, detail="role must be operator, reviewer, or admin")
    from ..db.database import User, session_scope
    with session_scope() as s:
        user = s.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        user.role = role
        s.commit()
        return {"id": str(user.user_id), "email": user.email, "name": user.display_name, "role": user.role, "active": bool(user.is_active)}

@router.get("/models")
def get_models(current_user=Depends(get_current_user)):
    _ = current_user
    out = []
    for m in model_registry.all():
        md = m.metadata(); healthy = m.health_check()
        out.append({"id": m.id, "name": md.get("model_name", m.id), "version": "runtime", "runtime": "local", "capabilities": list(m.capabilities), "status": "healthy" if healthy else "offline", "description": "Local Ollama model adapter", "active": healthy, "vramGb": None})
    vision = OllamaVlmAdapter()
    vision_healthy = vision.health_check()
    out.append({"id": vision.id, "name": vision.metadata()["model_name"], "version": "runtime", "runtime": "local", "capabilities": vision.capabilities, "status": "healthy" if vision_healthy else "offline", "description": "Local multimodal vision model", "active": vision_healthy, "vramGb": None})
    return out


def _sovereignty_payload(models, blocked):
    return {"mode": "active", "egressPolicy": "deny_by_default", "externalAllowed": 0, "externalBlocked": blocked, "localProcessingPercent": 100, "auditRecording": True, "healthyModels": sum(1 for m in models if m["status"] == "healthy"), "totalModels": len(models)}


@router.get("/sovereignty")
def get_sovereignty(current_user=Depends(get_current_user)):
    models = get_models(); net = _network_events()
    return _sovereignty_payload(models, sum(1 for x in net if x.get("decision") == "blocked"))


@router.get("/network-events")
def get_network_events(current_user=Depends(get_current_user)): return _network_events()


@router.get("/deliverables")
def get_deliverables(taskId: str | None = None, current_user=Depends(get_current_user)):
    role = str(getattr(current_user, "role", "operator")).lower()
    if taskId:
        owner = repo.get_task_owner(taskId)
        if str(owner) != str(current_user.user_id) and role not in {"reviewer", "admin"}: raise HTTPException(status_code=403, detail="not authorized for this task")
    return repo.deliverables(taskId, None if role in {"reviewer", "admin"} and not taskId else current_user.user_id)


@router.get("/approvals")
def get_approvals(current_user=Depends(require_roles("reviewer", "admin"))): return repo.approvals(current_user.user_id)


@router.post("/approvals/decide")
def decide_approval(payload: dict, current_user=Depends(require_roles("reviewer", "admin"))):
    decision = payload.get("decision")
    approval_id = payload.get("deliverableId")
    pending = repo.approvals(current_user.user_id, include_all=True)
    item = next((x for x in pending if x["id"] == approval_id or x.get("deliverableId") == approval_id), None)
    if not item: raise HTTPException(status_code=404, detail="approval not found")
    if decision not in {"approved", "changes_requested", "rejected"}: raise HTTPException(status_code=422, detail="invalid approval decision")
    actor = current_user.user_id
    repo.add_audit(actor, "approval.decision", "task", item["taskId"], "allow" if decision == "approved" else "deny", f"Approval decision: {decision}")
    if decision == "approved":
        from ..api.runs import approve_task
        return approve_task(item["taskId"], actor=current_user.user_id, current_user=current_user).model_dump(mode="json")
    repo.set_approval(item["taskId"], decision, actor, payload.get("comment"))
    if decision in {"rejected", "changes_requested"}:
        repo.set_task_status(item["taskId"], "failed" if decision == "rejected" else "awaiting_approval")
    return {**item, "approvalStatus": decision, "status": "failed" if decision == "rejected" else "warning"}
