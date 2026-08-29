from fastapi.testclient import TestClient

from ..app.main import app

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


def test_run_multimodal_intent_surfaces_evidence(monkeypatch):
    import os

    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "samples", "demo", "sample_note.txt"
    )
    sample_path = os.path.abspath(sample_path)

    # The real OCR pipeline (services/knowledge/ocr_vlm/ocr_tool.py, tool id
    # "ocr.process") calls a local Ollama vision model over HTTP -- there is
    # no such server in this test environment. Stub the VLM adapter's
    # invoke() so this test can verify the orchestrator's real
    # plan -> tool -> evidence wiring without needing a live model server.
    # This was previously asserting the tool id "ocr.process_naive", a
    # demo-only placeholder (services/orchestrator/tools/examples.py) that
    # is no longer registered now that the real OCR tool exists.
    def _fake_vlm_invoke(self, image_path, prompt=""):
        text = "Synthetic OCR output for offline testing."
        return {
            "content": text,
            "path": image_path,
            "model_id": self.id,
            "latency_ms": 1,
            "evidence": [
                {
                    "claim": text,
                    "source": image_path,
                    "page_or_region": None,
                    "model": self.id,
                    "confidence": None,
                    "validation_state": "unverified",
                }
            ],
        }

    monkeypatch.setattr(
        "services.knowledge.ocr_vlm.ollama_vlm_adapter.OllamaVlmAdapter.invoke",
        _fake_vlm_invoke,
    )

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
    assert body["evidence"][0]["tool"] == "ocr.process"


def test_approval_flow_pauses_then_resumes_via_approve_endpoint():
    create = client.post("/api/v1/tasks", json={"intent": "prepare an approval note"})
    task_id = create.json()["task_id"]

    run = client.post(f"/api/v1/tasks/{task_id}/run")
    assert run.status_code == 200
    assert run.json()["status"] == "awaiting_approval"

    approve = client.post(f"/api/v1/tasks/{task_id}/approve")
    assert approve.status_code == 200
    body = approve.json()
    assert body["status"] == "completed"
    # A fileless "approval note" intent produces a single, approval-gated
    # model.reason step (see create_plan()'s generic branch in
    # services/orchestrator/planner/planner.py) -- not two steps.
    assert len(body["completed_steps"]) == 1


def test_network_intent_is_denied_and_never_calls_the_tool():
    create = client.post("/api/v1/tasks", json={"intent": "test network access"})
    task_id = create.json()["task_id"]

    run = client.post(f"/api/v1/tasks/{task_id}/run")
    assert run.status_code == 200
    body = run.json()
    assert body["status"] == "failed"
    assert body["errors"][0]["code"] == "PERMISSION_DENIED"


def test_events_endpoint_returns_lifecycle_events():
    create = client.post("/api/v1/tasks", json={"intent": "do something vague"})
    task_id = create.json()["task_id"]
    client.post(f"/api/v1/tasks/{task_id}/run")

    events = client.get(f"/api/v1/tasks/{task_id}/events")
    assert events.status_code == 200
    event_types = [e["type"] for e in events.json()]
    assert event_types[0] == "TASK_CREATED"
    assert event_types[-1] == "TASK_COMPLETED"
