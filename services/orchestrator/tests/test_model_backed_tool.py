"""Proves the orchestrator -> services/model_control wiring end-to-end (closes the
Phase 5 TODO in tools/examples.py's SummarizeTextTool). Runs fully offline: no
Ollama/vLLM needed, since MODEL_RUNTIME env vars are unset in CI and the Model
Router (services/model_control/router) falls back to the offline
DemoModelAdapter — see services/model_control/tests for the router's own fallback
coverage."""
from services.orchestrator.planner.planner import create_plan
from services.orchestrator.planner.schemas import PlanStep
from services.orchestrator.state_graph.agent_state import AgentState
from services.orchestrator.state_graph.executor import run_plan
from services.orchestrator.tools.base import ToolRegistry
from services.orchestrator.tools.examples import ReadFileTool
from services.orchestrator.tools.model_backed import SummarizeTextModelTool

SAMPLE_FILE = "data/samples/demo/sample_note.txt"


def test_model_backed_summarize_tool_runs_end_to_end():
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(SummarizeTextModelTool())

    plan = create_plan(task_id="task_model_1", intent="summarize this file", file_path=SAMPLE_FILE)
    # Swap the naive summarizer for the model-backed one without touching the
    # planner's default branching logic.
    plan.steps[1] = PlanStep(
        id=plan.steps[1].id,
        capability="summarize_text",
        tool="text.summarize_model",
        depends_on=plan.steps[1].depends_on,
    )

    state = AgentState(task_id="task_model_1", user_id="user_1", intent="summarize this file")
    state.plan = plan

    result_state = run_plan(state, registry)

    assert result_state.errors == []
    assert result_state.final_output is not None
    summarize_output = result_state.final_output["tool_outputs"][1]
    assert summarize_output["summary"]
    assert summarize_output["model_id"] == "demo-fallback"  # no Ollama configured in CI
