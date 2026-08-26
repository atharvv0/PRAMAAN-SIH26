"""
PRAMAAN Core API entrypoint.

Run locally:    uvicorn app.main:app --reload --port 8000
Run via Docker: see services/backend/Dockerfile

Do not add business logic here — this file only wires up routers and middleware.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import health, runs, tasks
from app.core.config import settings
from services.orchestrator.errors import PramaanError

logger = logging.getLogger("pramaan.backend")

app = FastAPI(title="PRAMAAN Core API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO(Role 4/Security): tighten before anything beyond MVP demo
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error shape — see docs/api-contract.md "Error Shape (all non-2xx responses)".
# Every PramaanError subclass (services/orchestrator/errors.py) reaching this layer
# — from the orchestrator directly, or from services/model_control via
# services/orchestrator/tools/model_backed.py's translation — gets mapped to this
# shape instead of propagating as an unhandled 500 with a raw traceback.
@app.exception_handler(PramaanError)
def pramaan_error_handler(request: Request, exc: PramaanError) -> JSONResponse:  # noqa: ARG001
    logger.warning("PramaanError: code=%s message=%s detail=%s", exc.code, exc.message, exc.detail)
    status_code = 503 if exc.code == "MODEL_UNAVAILABLE" else 500
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": exc.code, "message": exc.message, "retryable": exc.retryable}},
    )


# Last-resort handler: never leak an internal stack trace to the frontend (see
# docs/api-contract.md "Never expose stack traces or internal detail in the
# response body"). Full detail still goes to the server log.
@app.exception_handler(Exception)
def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    logger.exception("Unhandled exception in request")
    return JSONResponse(
        status_code=500,
        content={
            "error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred.", "retryable": False}
        },
    )


app.include_router(health.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {"service": "pramaan-backend", "env": settings.app_env, "docs": "/docs"}
