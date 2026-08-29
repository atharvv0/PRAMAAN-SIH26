from fastapi.testclient import TestClient

from ..app.main import app


client = TestClient(app)


def test_frontend_api_surface_is_reachable():
    for path in [
        "/api/v1/overview",
        "/api/v1/workspaces",
        "/api/v1/evidence",
        "/api/v1/deliverables",
        "/api/v1/approvals",
        "/api/v1/audit",
        "/api/v1/models",
        "/api/v1/sovereignty",
        "/api/v1/network-events",
    ]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.headers["content-type"].startswith("application/json")


def test_run_id_lookup_and_task_list_contract():
    created = client.post("/api/v1/tasks", json={"intent": "summarize this file"})
    assert created.status_code == 201
    task = created.json()
    assert task["task_id"] == task["id"]
    assert task["runId"]

    listed = client.get("/api/v1/tasks")
    assert listed.status_code == 200
    assert any(item["id"] == task["id"] for item in listed.json())

    run = client.post(f"/api/v1/tasks/{task['id']}/run")
    assert run.status_code == 200
    run_body = run.json()
    assert run_body["id"] == run_body["run_id"] == task["runId"]

    lookup = client.get(f"/api/v1/runs/{task['runId']}")
    assert lookup.status_code == 200
    assert lookup.json()["taskId"] == task["id"]
