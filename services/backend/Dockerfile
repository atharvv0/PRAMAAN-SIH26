FROM python:3.11-slim

WORKDIR /app

# Build context is the repo root (see docker-compose.yml) because this service
# imports services/orchestrator directly — see docs/architecture.md
# "Deployment Topology" for why these aren't separate containers yet.
COPY services/backend/requirements.txt services/backend/requirements.txt
COPY services/model_control/requirements.txt services/model_control/requirements.txt
RUN pip install --no-cache-dir -r services/backend/requirements.txt \
    && pip install --no-cache-dir -r services/model_control/requirements.txt

COPY services/__init__.py services/__init__.py
COPY services/backend services/backend
COPY services/orchestrator services/orchestrator
# services/model_control: backend imports this in-process (see
# docs/architecture.md "Deployment Topology") via
# services/orchestrator/tools/model_backed.py, so it must ship in the same image.
COPY services/model_control services/model_control
COPY data/samples data/samples

ENV PYTHONPATH=/app:/app/services/backend
WORKDIR /app/services/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
