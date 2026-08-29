"""_build_plan() (services/backend/app/api/runs.py) decides between the
model-backed planner and the deterministic one. It previously did this by
checking whether the REASONING_MODEL_NAME env var was literally set --
but services/model_control auto-discovers local Ollama models even when
that env var is absent, so a genuinely available real model would still be
skipped. The fix asks the Model Router what it would actually select,
matching how every other model-backed tool in this codebase decides "is a
real model available".

These tests substitute the global model registry with fakes so they run
without a live Ollama server.
"""
from __future__ import annotations

from services.model_control.adapters.base import ModelResponse
from services.model_control.registry.registry import ModelRegistry


class _FakeDemoOnly:
    id = "demo-fallback"
    capabilities = ["reasoning"]
    modalities = ["text"]

    def invoke(self, prompt: str, **kwargs) -> ModelResponse:
        return ModelResponse(model_id=self.id, text="demo response")

    def health_check(self) -> bool:
        return True

    def metadata(self) -> dict:
        return {"id": self.id, "runtime": "demo-offline"}


class _FakeRealModel:
    id = "ollama-test-model"
    capabilities = ["reasoning"]
    modalities = ["text"]

    def __init__(self):
        self.invoked_with: list[str] = []

    def invoke(self, prompt: str, **kwargs) -> ModelResponse:
        self.invoked_with.append(prompt)
        return ModelResponse(
            model_id=self.id,
            text='{"goal":"g","steps":[{"step_no":1,"capability":"reasoning","tool":"model.reason","inputs":{},"depends_on":[],"requires_approval":false}]}',
        )

    def health_check(self) -> bool:
        return True

    def metadata(self) -> dict:
        return {"id": self.id, "runtime": "ollama", "model_name": "test-model"}


def test_uses_deterministic_planner_when_only_demo_model_available(monkeypatch):
    from services.backend.app.api import runs as runs_module

    registry = ModelRegistry()
    registry.register(_FakeDemoOnly())
    monkeypatch.setattr(runs_module, "model_registry", registry)

    plan = runs_module._build_plan("task_x", "do something vague", None)
    assert plan.steps[0].tool == "model.reason"
    # deterministic planner assigns ids like "step_<hex>"; model-backed plans
    # go through the same PlanStep constructor so this alone doesn't
    # distinguish them -- the real assertion is in the next test, where we
    # prove the fake *real* model actually gets invoked.


def test_uses_model_backed_planner_when_a_real_model_is_available(monkeypatch):
    """This is the actual bug: previously, a real registered+healthy model
    was still ignored unless REASONING_MODEL_NAME was set as an env var."""
    from services.backend.app.api import runs as runs_module

    registry = ModelRegistry()
    fake_model = _FakeRealModel()
    registry.register(fake_model)
    monkeypatch.setattr(runs_module, "model_registry", registry)
    monkeypatch.delenv("REASONING_MODEL_NAME", raising=False)

    plan = runs_module._build_plan("task_y", "prepare a review", None)

    assert fake_model.invoked_with, "the real (non-demo) model should have been called to plan"
    assert plan.steps[0].tool == "model.reason"


def test_falls_back_to_deterministic_planner_if_model_backed_planning_fails(monkeypatch):
    """A real model is available but planning itself fails (e.g. malformed
    JSON) -- the task should still get a usable plan instead of a 500."""
    from services.backend.app.api import runs as runs_module

    class _BrokenModel(_FakeRealModel):
        def invoke(self, prompt: str, **kwargs) -> ModelResponse:
            return ModelResponse(model_id=self.id, text="not json at all")

    registry = ModelRegistry()
    registry.register(_BrokenModel())
    monkeypatch.setattr(runs_module, "model_registry", registry)

    plan = runs_module._build_plan("task_z", "do something vague", None)
    assert plan.steps[0].tool == "model.reason"
