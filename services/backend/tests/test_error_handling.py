from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_run_on_missing_task_returns_404_not_a_traceback():
    resp = client.post("/api/v1/tasks/task_does_not_exist/run")
    assert resp.status_code == 404


def test_agent_loop_limit_error_maps_to_documented_error_shape(monkeypatch):
    """See docs/api-contract.md 'Error Shape (all non-2xx responses)'. Forces a
    PramaanError out of run_plan without needing a real 20-step plan."""
    from services.orchestrator.errors import AgentLoopLimitError, PramaanError

    def _boom(*args, **kwargs):
        raise AgentLoopLimitError("executor exceeded max_steps=20 for task X")

    import app.api.runs as runs_module

    monkeypatch.setattr(runs_module, "run_plan", _boom)

    create = client.post("/api/v1/tasks", json={"intent": "anything"})
    task_id = create.json()["task_id"]

    resp = client.post(f"/api/v1/tasks/{task_id}/run")
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "AGENT_LOOP_LIMIT"
    assert body["error"]["retryable"] is False
    assert "traceback" not in str(body).lower()
