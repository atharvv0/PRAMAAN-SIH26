from fastapi import APIRouter

router = APIRouter(tags=["health"])

SERVICE_NAME = "pramaan-backend"
SERVICE_VERSION = "0.1.0"


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}
