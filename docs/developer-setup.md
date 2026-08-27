# PRAMAAN — Developer Setup

## Prerequisites

- Docker + Docker Compose
- Python 3.11+ (for running/testing `backend` and `orchestrator` outside Docker)
- Node not required for MVP frontend (plain HTML/CSS/JS per `services/frontend/README.md`)

## First-time setup

```bash
git clone <repo-url> && cd PRAMAAN
cp .env.example .env
docker compose up --build
```

This currently boots: `postgres`, `qdrant`, `backend` (FastAPI, `GET /api/v1/health`),
`frontend` (static placeholder page). Everything else (`model_control`, `knowledge`,
`governance`, `sandbox`, `orchestrator`) is imported as a Python package by `backend` —
see `docs/architecture.md` "Deployment Topology".

Verify it worked:
```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","service":"pramaan-backend","version":"0.1.0"}
```

## Working on your own module without the full stack

Each service under `services/<name>/` has its own `README.md` with:
- what belongs there and what doesn't
- the contract it must satisfy (from `docs/agent-contract.md`)
- how to install its dependencies and run its own tests in isolation
- Definition of Done

You do **not** need `docker compose up` running to develop most modules — install that
service's `requirements.txt` in a venv and run its own test suite.

```bash
cd services/<your-service>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Backend (Role 3) — full local dev loop

Backend imports `services/orchestrator` directly, so it needs the repo root on
`PYTHONPATH`, not just its own directory — see `services/backend/README.md`.

```bash
# from repo root
cd services/backend
python -m venv .venv && source .venv/bin/activate
cd ../..  # back to repo root before installing/running
pip install -r services/backend/requirements.txt -r services/orchestrator/requirements.txt
PYTHONPATH=. uvicorn app.main:app --app-dir services/backend --reload --port 8000
```

Try the full loop once it's up:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"intent": "summarize this file", "demo_file_path": "'"$(pwd)"'/data/samples/demo/sample_note.txt"}'
# -> {"task_id": "task_...", ...}

curl -X POST http://localhost:8000/api/v1/tasks/<task_id>/run
# -> {"status": "completed", "final_output": {...}}
```

**Note:** backend startup is noticeably slower now (~5-8s) because it imports
`paddleocr`/`scikit-learn` at module load time via `services/knowledge`. This is
expected, not a hang — give it a few seconds before your first request.

## Verifying OCR/VLM on real hardware (not verifiable in every dev environment)

`services/knowledge/ocr_vlm/paddle_adapter.py` (PaddleOCR) and
`ollama_vlm_adapter.py` (Ollama vision models) both need things a sandboxed dev
environment may not have — internet access to download PaddleOCR's model weights,
and a running Ollama server with a vision model pulled, respectively. Verify both
before relying on them for a demo:

```bash
# from repo root, with PYTHONPATH=.
python -c "from services.knowledge.ocr_vlm.paddle_adapter import PaddleOcrAdapter; print('PaddleOCR ready:', PaddleOcrAdapter().health_check())"
python -c "from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter; print('Ollama VLM ready:', OllamaVlmAdapter(model='llava').health_check())"
```
If either prints `False`, see that adapter's module docstring for what to check.

## Orchestrator (Role 1) — running its test suite

```bash
cd services/orchestrator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Conventions

- Never commit `.env` — only `.env.example`.
- Never hard-code model names, DB URLs, ports, or secrets — read from config (`.env` /
  `app/core/config.py`).
- Branch naming: `feature/<short-name>` (e.g. `feature/tool-registry`). Commit messages:
  `feat:`, `fix:`, `test:`, `docs:` prefixes — see `docs/team-structure.md` "Definition of Done".
- Before opening a PR: tests pass, lint passes, `docs/api-contract.md` /
  `docs/agent-contract.md` updated if you changed a shared interface.

## Where do I start?

Check `docs/roadmap.md` for the current phase, then your own `services/<name>/README.md`
for the Definition of Done on your slice of it.
