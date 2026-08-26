from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "pramaan-backend"


def test_create_and_get_task():
    create = client.post("/api/v1/tasks", json={"intent": "test task"})
    assert create.status_code == 201
    task_id = create.json()["task_id"]

    get = client.get(f"/api/v1/tasks/{task_id}")
    assert get.status_code == 200
    assert get.json()["task_id"] == task_id


def test_run_multimodal_intent_surfaces_evidence():
    import os

    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "samples", "demo", "sample_note.txt"
    )
    sample_path = os.path.abspath(sample_path)

    create = client.post(
        "/api/v1/tasks",
        json={"intent": "review this scanned p&id drawing", "demo_file_path": sample_path},
    )
    task_id = create.json()["task_id"]

    run = client.post(f"/api/v1/tasks/{task_id}/run")
    assert run.status_code == 200
    body = run.json()
    assert body["status"] == "completed"
    assert len(body["evidence"]) == 1
    assert body["evidence"][0]["tool"] == "ocr.process_naive"
