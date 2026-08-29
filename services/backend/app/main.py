from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from services.backend.app.api import files, health, runs, tasks
from services.backend.app.api.metadata import router as metadata_router
from services.backend.app.core.config import settings
from services.orchestrator.errors import PramaanError

app = FastAPI(title="PRAMAAN Core API", version="1.0.0")


@app.on_event("startup")
def startup_db():
    from services.backend.app.db.database import init_db
    init_db()


def _error_payload(code: str, message: str, retryable: bool = False) -> dict:
    return {"error": {"code": code, "message": message, "retryable": retryable}}


@app.exception_handler(PramaanError)
async def pramaan_error_handler(request: Request, exc: PramaanError):
    return JSONResponse(
        status_code=500,
        content=_error_payload(exc.code, exc.message, exc.retryable),
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 409:
        code = "CONFLICT"
    else:
        code = "HTTP_ERROR"
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(code, str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=_error_payload("VALIDATION_ERROR", "Request validation failed."),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
app.include_router(runs.run_lookup_router, prefix="/api/v1")
app.include_router(metadata_router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {
        "service": "pramaan-backend",
        "env": settings.app_env,
        "docs": "/docs",
        "api_base": "/api/v1",
    }
