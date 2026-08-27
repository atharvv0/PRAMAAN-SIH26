import pytest

from services.model_control.adapters.base import ModelAdapter, ModelResponse
from services.model_control.adapters.demo_adapter import DemoModelAdapter
from services.model_control.errors import ModelUnavailableError
from services.model_control.registry.registry import ModelRegistry
from services.model_control.router.router import select_model


class _AlwaysHealthy(ModelAdapter):
    def __init__(self, id: str, capabilities: list[str]):  # noqa: A002
        self.id = id
        self.capabilities = capabilities
        self.modalities = ["text"]

    def invoke(self, prompt: str, **kwargs) -> ModelResponse:
        return ModelResponse(model_id=self.id, text=f"echo:{prompt}")

    def health_check(self) -> bool:
        return True


class _AlwaysDown(ModelAdapter):
    def __init__(self, id: str, capabilities: list[str]):  # noqa: A002
        self.id = id
        self.capabilities = capabilities
        self.modalities = ["text"]

    def invoke(self, prompt: str, **kwargs) -> ModelResponse:
        raise RuntimeError("unreachable")

    def health_check(self) -> bool:
        return False


def test_registry_register_and_list_by_capability():
    registry = ModelRegistry()
    registry.register(_AlwaysHealthy("m1", ["reasoning"]))
    registry.register(_AlwaysHealthy("m2", ["coding"]))
    assert registry.list_ids() == ["m1", "m2"]
    assert [m.id for m in registry.list_by_capability("reasoning")] == ["m1"]
    assert registry.list_by_capability("vision") == []


def test_registry_duplicate_id_rejected():
    registry = ModelRegistry()
    registry.register(_AlwaysHealthy("m1", ["reasoning"]))
    with pytest.raises(ValueError):
        registry.register(_AlwaysHealthy("m1", ["coding"]))


def test_select_model_prefers_healthy_candidate():
    registry = ModelRegistry()
    registry.register(_AlwaysDown("down", ["reasoning"]))
    registry.register(_AlwaysHealthy("up", ["reasoning"]))

    selected = select_model(registry, capability="reasoning")
    assert selected.id == "up"


def test_select_model_falls_back_to_last_candidate_when_none_healthy():
    registry = ModelRegistry()
    registry.register(_AlwaysDown("down1", ["reasoning"]))
    registry.register(_AlwaysDown("down2", ["reasoning"]))

    selected = select_model(registry, capability="reasoning")
    assert selected.id == "down2"  # last-registered = conventional fallback slot


def test_select_model_raises_when_no_candidates():
    registry = ModelRegistry()
    with pytest.raises(ModelUnavailableError):
        select_model(registry, capability="reasoning")


def test_select_model_is_capability_driven_not_hardcoded():
    """No model id/name may appear in router.py logic itself — verify router
    picks purely off registered capabilities by using unfamiliar ids."""
    registry = ModelRegistry()
    registry.register(_AlwaysHealthy("totally-arbitrary-name-42", ["coding"]))
    selected = select_model(registry, capability="coding")
    assert selected.id == "totally-arbitrary-name-42"


def test_select_model_respects_modality_filter():
    registry = ModelRegistry()
    text_model = _AlwaysHealthy("text-model", ["ocr"])
    registry.register(text_model)
    assert select_model(registry, capability="ocr", modality="text").id == "text-model"
    with pytest.raises(ModelUnavailableError):
        select_model(registry, capability="ocr", modality="image")


def test_demo_adapter_always_healthy_and_deterministic():
    adapter = DemoModelAdapter()
    assert adapter.health_check() is True
    response = adapter.invoke("First sentence. Second sentence. Third. Fourth sentence.")
    assert response.text == "First sentence. Second sentence. Third."
    assert response.raw == {"demo": True}


def test_default_registry_has_at_least_the_offline_fallback():
    """services/model_control/README.md DoD: 'at least two models available
    through one ModelAdapter interface' once a *_MODEL_NAME env var is set.
    Without any env configured (this test's default CI state), the offline
    DemoModelAdapter must still be present so select_model() never raises for
    an MVP capability."""
    from services.model_control.registry.registry_instance import build_default_registry

    registry = build_default_registry()
    assert "demo-fallback" in registry.list_ids()
    selected = select_model(registry, capability="summarize_text")
    assert selected.health_check() is True
