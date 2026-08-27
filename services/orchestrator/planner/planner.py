"""
Planner — turns TaskDefinition.intent into a Plan (docs/agent-contract.md).

Phase 3 status: rule-based, NOT the real LLM-driven planner. create_plan() branches
on simple keyword matching so the executor loop has something real to run end-to-end
(master prompt section 30's "read this file and summarize it" demo, plus a
multimodal-shaped "scanned report" branch) before model routing
(services/model_control) exists. TODO(Phase 3/5): replace the branching body with a
real capability-aware, model-backed planning call — keep this function's signature
stable so callers (services/backend) don't need to change.
"""
from __future__ import annotations

from services.orchestrator.planner.schemas import Plan, PlanStep


def create_plan(task_id: str, intent: str, file_path: str | None = None) -> Plan:
    intent_lower = intent.lower()

    network_keywords = ("network", "outbound", "external call", "sovereignty proof", "sovereign proof")
    if any(k in intent_lower for k in network_keywords):
        # Demo-only branch: proves the live "outbound request blocked" sovereignty
        # story (docs/architecture.md). This tool is denied by the PolicyEngine
        # before it ever runs — see services/orchestrator/tools/examples.py.
        return Plan(
            task_id=task_id,
            goal=intent,
            steps=[PlanStep(capability="network_egress_test", tool="network.fetch_demo", inputs={})],
        )

    knowledge_keywords = ("sop", "search the knowledge", "what does the sop", "search sop", "look up")
    if any(k in intent_lower for k in knowledge_keywords):
        # Real capability, not a demo placeholder: services/knowledge's RAG tool
        # (HashingVectorizer + Qdrant), pre-seeded with a demo sample document —
        # see services/orchestrator/tools/registry_instance.py.
        return Plan(
            task_id=task_id,
            goal=intent,
            steps=[PlanStep(capability="knowledge_search", tool="knowledge.search", inputs={"query": intent})],
        )

    multimodal_keywords = (
        "scan", "scanned", "p&id", "pid drawing", "drawing", "ocr",
        "vision", "image", "photo", "handwrit", "inspection package",
    )
    if file_path and any(k in intent_lower for k in multimodal_keywords):
        ocr_step = PlanStep(
            capability="document_analysis", tool="ocr.process_naive", inputs={"path": file_path}
        )
        summarize_step = PlanStep(
            capability="summarize_text",
            tool="text.summarize_naive",
            inputs={},
            depends_on=[ocr_step.id],
        )
        return Plan(task_id=task_id, goal=intent, steps=[ocr_step, summarize_step])

    if file_path and "summar" in intent_lower:
        read_step = PlanStep(
            capability="document_analysis", tool="file.read", inputs={"path": file_path}
        )
        summarize_step = PlanStep(
            capability="summarize_text",
            tool="text.summarize_naive",
            inputs={},
            depends_on=[read_step.id],
        )
        return Plan(task_id=task_id, goal=intent, steps=[read_step, summarize_step])

    # Fallback: no file, or an intent we don't have a real decomposition for yet.
    steps = [
        PlanStep(capability="understand_intent", inputs={"intent": intent}),
        PlanStep(capability="respond", depends_on=[], inputs={}),
    ]
    steps[1].depends_on = [steps[0].id]
    # Demo-only: an "approval"-flavoured intent marks the final step as requiring
    # human approval, so the pause/resume flow (executor + /tasks/{id}/approve) is
    # provable end-to-end — matches the dossier's flagship "approval note" step.
    if "approval" in intent_lower or "approve" in intent_lower:
        steps[1].requires_approval = True
    return Plan(task_id=task_id, goal=intent, steps=steps)
