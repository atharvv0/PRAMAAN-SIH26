FROM python:3.11-slim

WORKDIR /app

# Build context is the repo root (see docker-compose.yml) because this service
# imports services/orchestrator (and, via its tool registry, services/knowledge)
# directly — see docs/architecture.md "Deployment Topology" for why these aren't
# separate containers yet.
COPY services/backend/requirements.txt services/backend/requirements.txt
COPY services/orchestrator/requirements.txt services/orchestrator/requirements.txt
COPY services/knowledge/requirements.txt services/knowledge/requirements.txt
RUN pip install --no-cache-dir \
    -r services/backend/requirements.txt \
    -r services/orchestrator/requirements.txt \
    -r services/knowledge/requirements.txt

COPY services/__init__.py services/__init__.py
COPY services/backend services/backend
COPY services/orchestrator services/orchestrator
COPY services/knowledge services/knowledge
COPY services/governance services/governance
COPY data/samples data/samples

ENV PYTHONPATH=/app:/app/services/backend
WORKDIR /app/services/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
