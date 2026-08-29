# PRAMAAN Final Runbook

## Local development

1. Start PostgreSQL and Qdrant.
2. Start Ollama locally with `OLLAMA_NO_CLOUD=1` and `OLLAMA_MODELS` pointing to the model disk.
3. Pull/verify the configured models before the first run.
4. Copy `.env.example` to `.env` and keep the model names aligned with `ollama list`.
5. Start the backend: `uvicorn app.main:app --app-dir services/backend --reload --port 8000`.
6. Start the frontend from `services/frontend` with `npm run dev`.

## Recommended local AI roles

- `REASONING_MODEL_NAME=qwen3:4b`
- `CODING_MODEL_NAME=qwen3:4b` (same local model through a distinct coding capability route)
- `VISION_MODEL_NAME=gemma3:4b`
- `OCR_MODEL_NAME=gemma3:4b`
- `EMBEDDING_MODEL_NAME=nomic-embed-text`

## Canonical browser test

Create a task, upload an inspection PDF/image, add the SOP, submit, watch the run, inspect evidence, handle approval if requested, then download the generated Word approval note.

## Sovereignty test

After all model weights and runtime dependencies are installed, disconnect the workstation from the internet and repeat the browser test. The AI path should remain local to Ollama, PostgreSQL and Qdrant. The demo sovereignty screen should show local processing and any blocked network attempt.
