import pytest

from services.orchestrator.errors import AgentLoopLimitError
from services.orchestrator.planner.planner import create_plan
from services.orchestrator.planner.schemas import PlanStep, StepStatus
from services.orchestrator.state_graph.agent_state import AgentState
from services.orchestrator.state_graph.executor import run_plan
from services.orchestrator.tools.base import ToolAdapter, ToolRegistry
from services.orchestrator.tools.examples import ReadFileTool, SummarizeTextTool

SAMPLE_FILE = "data/samples/demo/sample_note.txt"


def _registry_with_demo_tools() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(SummarizeTextTool())
    return registry


def test_full_read_and_summarize_loop():
    """The signature demo from master prompt section 30: one instruction ->
    multi-step plan -> tool use -> completed result."""
    plan = create_plan(task_id="task_1", intent="summarize this file", file_path=SAMPLE_FILE)
    state = AgentState(task_id="task_1", user_id="user_1", intent="summarize this file")
    state.plan = plan

    result_state = run_plan(state, _registry_with_demo_tools())

    assert result_state.errors == []
    assert len(result_state.completed_steps) == 2
    assert result_state.final_output is not None
    assert "summary" in result_state.final_output["tool_outputs"][1]
    assert result_state.final_output["tool_outputs"][1]["summary"]  # non-empty


def test_fallback_plan_with_no_tools_completes():
    plan = create_plan(task_id="task_2", intent="do something vague")
    state = AgentState(task_id="task_2", user_id="user_1", intent="do something vague")
    state.plan = plan

    result_state = run_plan(state, ToolRegistry())

    assert result_state.errors == []
    assert len(result_state.completed_steps) == 2
    assert result_state.final_output is not None


def test_missing_tool_raises_tool_execution_error_and_is_recorded():
    plan = create_plan(task_id="task_3", intent="summarize this file", file_path="does/not/exist.txt")
    state = AgentState(task_id="task_3", user_id="user_1", intent="summarize this file")
    state.plan = plan

    result_state = run_plan(state, _registry_with_demo_tools())

    assert len(result_state.errors) == 1
    assert result_state.errors[0].code == "TOOL_EXECUTION_ERROR"
    assert result_state.final_output is None


def test_step_requiring_approval_pauses_execution():
    plan = create_plan(task_id="task_4", intent="do something vague")
    plan.steps[0].requires_approval = True
    state = AgentState(task_id="task_4", user_id="user_1", intent="do something vague")
    state.plan = plan

    result_state = run_plan(state, ToolRegistry())

    assert result_state.approval_status == "pending"
    assert result_state.completed_steps == []


def test_multimodal_plan_produces_ocr_then_summarize_steps():
    plan = create_plan(task_id="task_6", intent="review this scanned inspection report", file_path=SAMPLE_FILE)
    assert len(plan.steps) == 2
    assert plan.steps[0].tool == "ocr.process_naive"
    assert plan.steps[1].tool == "text.summarize_naive"
    assert plan.steps[1].depends_on == [plan.steps[0].id]


def test_multimodal_loop_populates_evidence():
    from services.orchestrator.tools.examples import OcrProcessNaiveTool

    registry = _registry_with_demo_tools()
    registry.register(OcrProcessNaiveTool())

    plan = create_plan(task_id="task_7", intent="review this scanned p&id drawing", file_path=SAMPLE_FILE)
    state = AgentState(task_id="task_7", user_id="user_1", intent="review this scanned p&id drawing")
    state.plan = plan

    result_state = run_plan(state, registry)

    assert result_state.errors == []
    assert result_state.final_output is not None
    assert len(result_state.evidence) == 1
    ev = result_state.evidence[0]
    assert ev.source == SAMPLE_FILE
    assert ev.tool == "ocr.process_naive"
    assert ev.page_or_region == "page_1"
    assert ev.validation_state == "unverified"


def test_network_tool_denied_by_default_policy_engine():
    from services.orchestrator.tools.examples import NetworkFetchDemoTool

    plan = create_plan(task_id="task_8", intent="test network access", file_path=None)
    assert plan.steps[0].tool == "network.fetch_demo"

    registry = ToolRegistry()
    registry.register(NetworkFetchDemoTool())
    state = AgentState(task_id="task_8", user_id="user_1", intent="test network access")
    state.plan = plan

    result_state = run_plan(state, registry)

    assert result_state.final_output is None
    assert len(result_state.errors) == 1
    assert result_state.errors[0].code == "PERMISSION_DENIED"
    # the tool's invoke() must never have actually run
    assert result_state.tool_calls == []


def test_network_denial_is_recorded_in_audit_log():
    from services.governance.audit.log import AuditLog
    from services.orchestrator.tools.examples import NetworkFetchDemoTool

    audit_log = AuditLog()
    registry = ToolRegistry()
    registry.register(NetworkFetchDemoTool())

    plan = create_plan(task_id="task_9", intent="test network access")
    state = AgentState(task_id="task_9", user_id="user_1", intent="test network access")
    state.plan = plan

    run_plan(state, registry, audit_log=audit_log)

    events = audit_log.all()
    assert len(events) == 1
    assert events[0].decision == "deny"
    assert events[0].target == "network.fetch_demo"


def test_approval_demo_plan_pauses_and_resumes_via_approval_status():
    plan = create_plan(task_id="task_10", intent="prepare an approval note")
    assert plan.steps[1].requires_approval is True

    state = AgentState(task_id="task_10", user_id="user_1", intent="prepare an approval note")
    state.plan = plan

    paused = run_plan(state, ToolRegistry())
    assert paused.approval_status == "pending"
    assert len(paused.completed_steps) == 1  # first step ran, second is gated

    paused.approval_status = "approved"
    resumed = run_plan(paused, ToolRegistry())
    assert resumed.approval_status == "approved"
    assert len(resumed.completed_steps) == 2
    assert resumed.final_output is not None


def test_event_log_records_expected_lifecycle_events():
    plan = create_plan(task_id="task_11", intent="do something vague")
    state = AgentState(task_id="task_11", user_id="user_1", intent="do something vague")
    state.plan = plan

    result_state = run_plan(state, ToolRegistry())

    event_types = [e["type"] for e in result_state.events]
    assert event_types[0] == "TASK_CREATED"
    assert event_types[1] == "PLAN_CREATED"
    assert "STEP_STARTED" in event_types
    assert event_types[-1] == "TASK_COMPLETED"


def test_max_steps_ceiling_raises_agent_loop_limit_error():
    class _NoopTool(ToolAdapter):
        id = "noop"

        def invoke(self, inputs: dict) -> dict:
            return {}

    steps = [PlanStep(capability="noop", tool="noop") for _ in range(5)]
    from services.orchestrator.planner.schemas import Plan

    plan = Plan(task_id="task_5", goal="stress test", steps=steps)
    state = AgentState(task_id="task_5", user_id="user_1", intent="stress test")
    state.plan = plan

    registry = ToolRegistry()
    registry.register(_NoopTool())

    with pytest.raises(AgentLoopLimitError):
        run_plan(state, registry, max_steps=2)
