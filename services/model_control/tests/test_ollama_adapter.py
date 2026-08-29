from services.model_control.adapters.ollama_adapter import OllamaAdapter


def test_ollama_adapter_exact_health_match(monkeypatch):
    class Response:
        status_code = 200

        def json(self):
            return {"models": [{"name": "qwen3:4b"}, {"name": "other:1b"}]}

    monkeypatch.setattr(
        "services.model_control.adapters.ollama_adapter.httpx.get",
        lambda *args, **kwargs: Response(),
    )

    assert OllamaAdapter("qwen", "qwen3:4b", ["reasoning"]).health_check() is True
    assert OllamaAdapter("missing", "qwen3:8b", ["reasoning"]).health_check() is False


def test_ollama_adapter_sends_think_flag_and_json_format(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": "{}"}

    def fake_post(url, json, timeout):
        captured.update(json)
        return Response()

    monkeypatch.setattr(
        "services.model_control.adapters.ollama_adapter.httpx.post",
        fake_post,
    )

    adapter = OllamaAdapter("qwen", "qwen3:4b", ["reasoning"])
    response = adapter.invoke(
        "Return JSON",
        think=False,
        format={"type": "object"},
        options={"temperature": 0},
    )

    assert response.text == "{}"
    assert captured["model"] == "qwen3:4b"
    assert captured["think"] is False
    assert captured["format"] == {"type": "object"}
