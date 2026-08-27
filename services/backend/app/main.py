from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, tasks
from app.core.config import settings

app = FastAPI(
    title="PRAMAAN Core API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health.router,
    prefix="/api/v1",
)

app.include_router(
    tasks.router,
    prefix="/api/v1",
)


@app.get("/")
def root() -> dict:
    return {
        "service": "pramaan-backend",
        "env": settings.app_env,
        "docs": "/docs",
    }