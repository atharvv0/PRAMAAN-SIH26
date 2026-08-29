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


def test_model_backed_plan_parses_structured_json(monkeypatch):
    from services.model_control.adapters.base import ModelResponse
    from services.model_control.registry.registry import ModelRegistry
    from services.orchestrator.planner.planner import create_model_backed_plan

    class _FakeModel:
        id = "ollama-test"
        capabilities = ["reasoning"]
        modalities = ["text"]

        def invoke(self, prompt: str, **kwargs):
            return ModelResponse(
                model_id=self.id,
                text='{"goal":"Prepare review","steps":[{"step_no":1,"capability":"document_analysis","tool":"file.read","inputs":{},"depends_on":[],"requires_approval":false},{"step_no":2,"capability":"summarize_text","tool":"text.summarize_model","inputs":{},"depends_on":[1],"requires_approval":true}]}',
                latency_ms=12,
            )

        def health_check(self):
            return True

        def metadata(self):
            return {"id": self.id, "runtime": "ollama", "model_name": "qwen3:4b"}

    registry = ModelRegistry()
    registry.register(_FakeModel())
    plan = create_model_backed_plan("task_1", "prepare a review", file_path="report.txt", registry=registry)
    assert len(plan.steps) == 2
    assert plan.steps[0].inputs["path"] == "report.txt"
    assert plan.steps[1].depends_on == [plan.steps[0].id]
    assert plan.steps[1].requires_approval is True


def test_model_backed_plan_rejects_unsupported_tools():
    from services.model_control.adapters.base import ModelResponse
    from services.model_control.registry.registry import ModelRegistry
    from services.orchestrator.errors import PlannerError
    from services.orchestrator.planner.planner import create_model_backed_plan

    class _FakeModel:
        id = "ollama-test"
        capabilities = ["reasoning"]
        modalities = ["text"]

        def invoke(self, prompt: str, **kwargs):
            return ModelResponse(
                model_id=self.id,
                text='{"goal":"Bad","steps":[{"step_no":1,"capability":"danger","tool":"shell.exec","inputs":{},"depends_on":[],"requires_approval":false}]}',
            )

        def health_check(self):
            return True

        def metadata(self):
            return {"runtime": "ollama", "model_name": "qwen3:4b"}

    registry = ModelRegistry()
    registry.register(_FakeModel())
    try:
        create_model_backed_plan("task_2", "do something", registry=registry)
    except PlannerError:
        return
    raise AssertionError("unsupported tool was not rejected")
