from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import health, runs, tasks
from app.core.config import settings
from services.orchestrator.errors import AgentLoopLimitError, PramaanError


app = FastAPI(title="PRAMAAN Core API", version="0.1.0")


@app.exception_handler(PramaanError)
async def pramaan_error_handler(request: Request, exc: PramaanError):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable,
            }
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {
        "service": "pramaan-backend",
        "env": settings.app_env,
        "docs": "/docs",
    }