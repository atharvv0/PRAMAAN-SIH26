# Final Apply / Run Guide

1. Replace the existing `services/` folder with this corrected `services/` folder.
2. Do not copy `__pycache__`, `node_modules`, or a previous `dist` tree back over the corrected source.
3. From the repository root, create/activate `.venv` and install `services/requirements.txt`.
4. Configure `.env` using `services/.env.example`.
5. Start PostgreSQL, Qdrant (6333) and Ollama (11434).
6. Make sure these Ollama models exist:
   - qwen3:4b
   - gemma3:4b
   - nomic-embed-text
7. Start the backend:
   `python -m uvicorn services.backend.app.main:app --reload --port 8000`
8. Start the frontend:
   `cd services/frontend`
   `npm install`
   `npm run dev`
9. Log in as one user, create/run a task, then switch to another user to confirm history isolation.
10. For a file-output test, use:
    "Summarize this file in 10 lines and give me the summary in a .txt file."
11. The run should finish only after artifact generation and deliverable registration, and the Run page should show the final response plus a generated `summary.txt` link.

Production note: replace the local `X-User-Email` identity mechanism with verified Firebase/OIDC/JWT authentication before deployment.
