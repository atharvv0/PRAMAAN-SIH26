"""
PRAMAAN Core API entrypoint.

Run locally:    uvicorn app.main:app --reload --port 8000
Run via Docker: see services/backend/Dockerfile

Do not add business logic here — this file only wires up routers and middleware.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, runs, tasks
from app.core.config import settings

app = FastAPI(title="PRAMAAN Core API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO(Role 4/Security): tighten before anything beyond MVP demo
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {"service": "pramaan-backend", "env": settings.app_env, "docs": "/docs"}
