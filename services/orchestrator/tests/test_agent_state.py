from services.orchestrator.planner.planner import create_plan
from services.orchestrator.planner.schemas import StepStatus
from services.orchestrator.state_graph.agent_state import AgentState
from services.orchestrator.tools.base import ToolAdapter, ToolRegistry


def test_create_plan_produces_ordered_steps():
    plan = create_plan(task_id="task_1", intent="summarize this file")
    assert plan.task_id == "task_1"
    assert len(plan.steps) == 2
    assert plan.steps[0].status == StepStatus.PENDING
    assert plan.steps[1].depends_on == [plan.steps[0].id]


def test_agent_state_defaults():
    state = AgentState(task_id="task_1", user_id="user_1", intent="do the thing")
    assert state.completed_steps == []
    assert state.approval_status == "not_required"
    assert state.plan is None


class _EchoTool(ToolAdapter):
    id = "echo"

    def invoke(self, inputs: dict) -> dict:
        return {"echo": inputs}


def test_tool_registry_register_and_get():
    registry = ToolRegistry()
    registry.register(_EchoTool())
    assert registry.get("echo").invoke({"x": 1}) == {"echo": {"x": 1}}
    assert "echo" in registry.list_ids()
