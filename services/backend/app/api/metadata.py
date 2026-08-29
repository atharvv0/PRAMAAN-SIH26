from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..db.database import Project, Workspace, session_scope
from services.backend.app.db.repository import repo
from services.governance.audit.log import default_audit_log
from services.model_control.registry.registry_instance import default_registry as model_registry
from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter

router=APIRouter(tags=["metadata"])

def _network_events():
    return [{"id":f"network-{i}","timestamp":e.timestamp,"kind":"policy_decision","message":e.policy_reason,"decision":"blocked" if e.decision=="deny" else "allowed","reason":e.policy_reason,"destination":e.target} for i,e in enumerate(default_audit_log.all(),1)]

@router.get("/workspaces")
def get_workspaces(): return repo.list_workspaces()

@router.get("/workspaces/{workspace_id}")
def get_workspace(workspace_id:str):
    item=next((x for x in repo.list_workspaces() if x["id"]==workspace_id),None)
    if not item: raise HTTPException(status_code=404,detail="workspace not found")
    return item

@router.get("/overview")
def get_overview():
    tasks=repo.list_tasks(); approvals=repo.approvals(); deliverables=repo.deliverables(); events=repo.audits()
    models=get_models(); net=_network_events()
    return {"sovereignty":_sovereignty_payload(models,sum(1 for x in net if x.get("decision")=="blocked")),"activeTasks":sum(1 for t in tasks if t["status"] in {"queued","running","awaiting_approval"}),"pendingApprovals":len(approvals),"recentDeliverables":len(deliverables),"recentSecurityEvents":sum(1 for x in net if x.get("decision")=="blocked"),"activity":events[:20],"currentTasks":tasks[:20],"networkEvents":net}

@router.get("/evidence")
def get_evidence(taskId:str|None=None,runId:str|None=None): return repo.evidence(taskId)

@router.get("/evidence/{evidence_id}")
def get_evidence_by_id(evidence_id:str):
    found=next((x for x in repo.evidence() if x["id"]==evidence_id),None)
    if not found: raise HTTPException(status_code=404,detail="evidence not found")
    return found

@router.get("/audit")
def get_audit(taskId:str|None=None): return repo.audits(taskId)

@router.get("/models")
def get_models():
    out=[]
    for m in model_registry.all():
        md=m.metadata(); healthy=m.health_check(); out.append({"id":m.id,"name":md.get("model_name",m.id),"version":"runtime","runtime":"local","capabilities":list(m.capabilities),"status":"healthy" if healthy else "offline","description":"Local Ollama model adapter","active":healthy,"vramGb":None})
    vision=OllamaVlmAdapter()
    out.append({"id":vision.id,"name":vision.metadata()["model_name"],"version":"runtime","runtime":"local","capabilities":vision.capabilities,"status":"healthy" if vision.health_check() else "offline","description":"Local multimodal vision model","active":vision.health_check(),"vramGb":None})
    return out

def _sovereignty_payload(models,blocked): return {"mode":"active","egressPolicy":"deny_by_default","externalAllowed":0,"externalBlocked":blocked,"localProcessingPercent":100,"auditRecording":True,"healthyModels":sum(1 for m in models if m["status"]=="healthy"),"totalModels":len(models)}

@router.get("/sovereignty")
def get_sovereignty():
    models=get_models(); net=_network_events(); return _sovereignty_payload(models,sum(1 for x in net if x.get("decision")=="blocked"))

@router.get("/network-events")
def get_network_events(): return _network_events()

@router.get("/deliverables")
def get_deliverables(taskId:str|None=None): return repo.deliverables(taskId)

@router.get("/approvals")
def get_approvals(): return repo.approvals()

@router.post("/approvals/decide")
def decide_approval(payload:dict):
    decision=payload.get("decision"); approval_id=payload.get("deliverableId")
    pending=repo.approvals(); item=next((x for x in pending if x["id"]==approval_id or x.get("deliverableId")==approval_id),None)
    if not item: raise HTTPException(status_code=404,detail="approval not found")
    if decision not in {"approved","changes_requested","rejected"}: raise HTTPException(status_code=422,detail="invalid approval decision")
    actor=payload.get("actor") or "demo.operator@local"
    repo.add_audit(actor,"approval.decision","task",item["taskId"],"allow" if decision=="approved" else "deny",f"Approval decision: {decision}")
    if decision=="approved":
        from ..api.runs import approve_task
        return approve_task(item["taskId"], actor=actor).model_dump(mode="json")
    repo.set_approval(item["taskId"],decision,actor,payload.get("comment"))
    if decision in {"rejected","changes_requested"}:
        repo.set_task_status(item["taskId"], "failed" if decision == "rejected" else "awaiting_approval")
    return {**item,"approvalStatus":decision,"status":"failed" if decision=="rejected" else "warning"}
