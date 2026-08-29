from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.backend.app.db.repository import repo
from ..models.run import RunResult
from services.model_control.errors import ModelControlError
from services.model_control.registry.registry_instance import default_registry as model_registry
from services.model_control.router.router import select_model
from services.orchestrator.errors import ModelUnavailableError, PlannerError, PramaanError
from services.orchestrator.planner.planner import create_model_backed_plan, create_plan
from services.orchestrator.state_graph.agent_state import AgentState
from services.orchestrator.state_graph.executor import run_plan
from services.orchestrator.tools.registry_instance import default_registry
from ..services.deliverable import generate_approval_note

router=APIRouter(prefix="/tasks",tags=["runs"])
run_lookup_router=APIRouter(prefix="/runs",tags=["runs"])

def _status(state:AgentState)->str:
    if state.approval_status=="pending": return "awaiting_approval"
    if state.errors:return "failed"
    if state.plan and all(s.status.value=="done" for s in state.plan.steps):return "completed"
    return "running" if state.completed_steps else "queued"

def _progress(state:AgentState)->int:
    return int(len(state.completed_steps)/len(state.plan.steps)*100) if state.plan and state.plan.steps else 0

def _plan(state):
    out=[]
    for step in state.plan.steps if state.plan else []:
        model=next((c.model_id for c in reversed(state.model_calls) if c.purpose==step.capability),None)
        out.append({"id":step.id,"label":step.capability.replace("_"," ").upper(),"status":{"pending":"queued","running":"running","done":"completed","failed":"failed","skipped":"blocked"}[step.status.value],"toolId":step.tool,"modelId":model,"startedAt":None,"durationMs":0,"evidenceCount":0,"details":None,"warning":None})
    return out

def _result(task_id,state,run_id):
    now=state.events[-1]["timestamp"] if state.events else ""
    routings=[{"stepId":state.current_step or "model","taskLabel":c.purpose.replace("_"," ").upper(),"modelId":c.model_id,"modelName":c.model_id,"reason":"Selected by the capability-driven Model Router.","local":True,"status":"completed"} for c in state.model_calls]
    tools=[]
    for i,c in enumerate(state.tool_calls,1):
        tools.append({"id":f"inv_{task_id}_{i}","tool":c.tool_id,"status":"failed" if c.error else "completed","permission":"blocked" if c.error and "denied" in c.error.lower() else "allowed","reason":c.error or "Allowed by Policy Engine.","timestamp":now,"inputSummary":str(c.inputs),"outputSummary":str(c.output) if c.output is not None else c.error})
    return RunResult(run_id=run_id,task_id=task_id,status=_status(state),completed_steps=state.completed_steps,errors=[e.model_dump() for e in state.errors],evidence=[e.model_dump() for e in state.evidence],final_output=state.final_output,id=run_id,taskId=task_id,progress=_progress(state),currentStepId=state.current_step,plan=_plan(state),modelRoutings=routings,toolInvocations=tools,startedAt=state.events[0]["timestamp"] if state.events else now,updatedAt=now)

def _build_plan(task_id:str, intent:str, file_path:str|None):
    """Decide deterministic vs. model-backed planning.

    services/orchestrator/README.md documents the production path as
    "Task -> Model-backed Planner (Ollama via Model Control) -> validated
    Plan -> ..." with the deterministic planner reserved for unit tests.
    This used to be decided by checking whether the REASONING_MODEL_NAME env
    var was literally set -- but services/model_control auto-discovers local
    Ollama models even when that env var is absent (see
    registry_instance.py's AUTO_DISCOVER_OLLAMA_MODELS), so a real,
    available model would still be skipped in favour of the deterministic
    planner. Ask the Model Router what it would actually select instead, so
    "is a real model available" is answered the same way everywhere in the
    system.
    """
    use_model_backed = False
    try:
        model = select_model(model_registry, capability="reasoning", modality="text")
        use_model_backed = model.metadata().get("runtime") != "demo-offline"
    except ModelControlError:
        use_model_backed = False

    if use_model_backed:
        try:
            # Pass the same registry we just checked availability against --
            # create_model_backed_plan()'s default `registry` parameter is
            # bound to model_control's own module-level singleton at def
            # time, which is not necessarily the same object this function
            # resolved `model` from (e.g. in tests, or if either module is
            # reloaded/patched independently).
            return create_model_backed_plan(task_id, intent, file_path=file_path, registry=model_registry)
        except (ModelUnavailableError, PlannerError):
            # A real model is registered but planning itself failed (model
            # invocation error, malformed JSON, etc). Degrade to the
            # deterministic planner rather than failing the task outright --
            # this mirrors the demo-fallback-model degradation pattern used
            # elsewhere in services/model_control.
            pass

    return create_plan(task_id, intent, file_path=file_path)


def _load(task_id:str):
    found=repo.get_state(task_id)
    if not found: raise HTTPException(status_code=404,detail="task not found")
    task,run=found
    state=AgentState.model_validate(run.state_json) if run.state_json.get("plan") else AgentState(task_id=task_id,user_id=repo.get_user(task.created_by).email,intent=task.intent,files=[x["id"] for x in repo.files_for_task(task_id)])
    if state.plan is None:
        state.plan=_build_plan(task_id,task.intent,repo.file_path_for_task(task_id))
    return task,run,state

def _persist(task_id,state,status):
    data=state.model_dump(mode="json")
    repo.update_run(task_id,data,status)
    repo.persist_state_artifacts(data)
    for ev in state.events:
        key=f"{ev.get('type')}"; 
        # Keep durable lifecycle events; policy layer remains authoritative for policy records.
    return data


def _ensure_draft_deliverable(task_id:str, state:AgentState, title:str, intent:str):
    if state.approval_status != "pending" or repo.has_deliverable(task_id):
        return
    generate_approval_note(task_id, title, intent, state.model_dump(mode="json"))

@router.post("/{task_id}/run",response_model=RunResult)
def run_task(task_id:str):
    task,run,state=_load(task_id)
    try: state=run_plan(state,default_registry)
    except PramaanError: _persist(task_id,state,_status(state)); raise
    status=_status(state); _persist(task_id,state,status)
    repo.add_audit(state.user_id,"task.run","task",task_id,"allow" if status!="failed" else "deny",f"Task run reached status {status}.")
    if status=="awaiting_approval":
        repo.ensure_pending_approval(task_id,state.user_id)
        _ensure_draft_deliverable(task_id,state,task.title,task.intent)
    if status=="completed":
        repo.add_audit(state.user_id,"task.completed","task",task_id,"allow","Task completed locally.")
    return _result(task_id,state,run.run_id)

@router.post("/{task_id}/approve",response_model=RunResult)
def approve_task(task_id:str, actor: str | None = None):
    task,run,state=_load(task_id)
    if state.approval_status!="pending": raise HTTPException(status_code=409,detail="task has no step currently awaiting approval")
    state.approval_status="approved"
    state=run_plan(state,default_registry)
    status=_status(state); _persist(task_id,state,status); repo.set_approval(task_id,"approved",actor or state.user_id); repo.add_audit(state.user_id,"approval.resumed","task",task_id,"allow","Approved execution resumed.")
    if status == "completed":
        from ..services.deliverable import generate_approval_note
        draft = generate_approval_note(task_id, task.title, task.intent, state.model_dump(mode="json"))
        repo.create_deliverable(task_id, draft["file_id"], "docx", "approved")
        repo.add_audit(actor or state.user_id, "deliverable.generated", "task", task_id, "allow", "Final approval note generated locally.")
    return _result(task_id,state,run.run_id)

@router.get("/{task_id}/events")
def get_task_events(task_id:str):
    found=repo.get_state(task_id)
    if not found: raise HTTPException(status_code=404,detail="task not found")
    return AgentState.model_validate(found[1].state_json).events

@run_lookup_router.get("/{run_id}",response_model=RunResult)
def get_run(run_id:str):
    state_json=repo.get_run(run_id)
    if not state_json: raise HTTPException(status_code=404,detail="run not found")
    state=AgentState.model_validate(state_json)
    return _result(state.task_id,state,run_id)
