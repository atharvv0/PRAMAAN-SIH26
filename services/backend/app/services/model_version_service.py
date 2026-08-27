from sqlalchemy.orm import Session

from app.repositories.model_version_repository import (
    create_model_version,
    get_model_version,
    get_model_versions_by_model,
    get_model_version_by_version,
    get_model_versions,
    update_model_version,
    delete_model_version,
)


VALID_STATUSES = {
    "active",
    "inactive",
    "deprecated",
}


def create_model_version_service(
    db: Session,
    model_id,
    version: str,
    weights_path: str,
    license: str,
    quantization: str = None,
    vram_required_gb: float = None,
    status: str = "active",
):
    if not version or not version.strip():
        raise ValueError(
            "Model version is required."
        )

    if not weights_path or not weights_path.strip():
        raise ValueError(
            "Weights path is required."
        )

    if not license or not license.strip():
        raise ValueError(
            "License is required."
        )

    if (
        vram_required_gb is not None
        and vram_required_gb < 0
    ):
        raise ValueError(
            "VRAM requirement cannot be negative."
        )

    if status not in VALID_STATUSES:
        raise ValueError(
            "Invalid model version status."
        )

    existing = get_model_version_by_version(
        db,
        model_id,
        version.strip(),
    )

    if existing is not None:
        raise ValueError(
            "This version already exists for this model."
        )

    return create_model_version(
        db=db,
        model_id=model_id,
        version=version.strip(),
        weights_path=weights_path.strip(),
        license=license.strip(),
        quantization=(
            quantization.strip()
            if quantization is not None
            else None
        ),
        vram_required_gb=vram_required_gb,
        status=status,
    )


def get_model_version_service(
    db: Session,
    model_version_id,
):
    model_version = get_model_version(
        db,
        model_version_id,
    )

    if model_version is None:
        raise ValueError(
            "Model version not found."
        )

    return model_version


def get_model_versions_by_model_service(
    db: Session,
    model_id,
):
    return get_model_versions_by_model(
        db,
        model_id,
    )


def get_model_version_by_version_service(
    db: Session,
    model_id,
    version: str,
):
    if not version or not version.strip():
        raise ValueError(
            "Model version is required."
        )

    model_version = get_model_version_by_version(
        db,
        model_id,
        version.strip(),
    )

    if model_version is None:
        raise ValueError(
            "Model version not found."
        )

    return model_version


def get_model_versions_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_model_versions(
        db,
        limit=limit,
    )


def update_model_version_service(
    db: Session,
    model_version_id,
    version: str = None,
    weights_path: str = None,
    quantization: str = None,
    vram_required_gb: float = None,
    license: str = None,
    status: str = None,
):
    if version is not None and not version.strip():
        raise ValueError(
            "Model version cannot be empty."
        )

    if (
        weights_path is not None
        and not weights_path.strip()
    ):
        raise ValueError(
            "Weights path cannot be empty."
        )

    if license is not None and not license.strip():
        raise ValueError(
            "License cannot be empty."
        )

    if (
        vram_required_gb is not None
        and vram_required_gb < 0
    ):
        raise ValueError(
            "VRAM requirement cannot be negative."
        )

    if (
        status is not None
        and status not in VALID_STATUSES
    ):
        raise ValueError(
            "Invalid model version status."
        )

    model_version = update_model_version(
        db=db,
        model_version_id=model_version_id,
        version=(
            version.strip()
            if version is not None
            else None
        ),
        weights_path=(
            weights_path.strip()
            if weights_path is not None
            else None
        ),
        quantization=(
            quantization.strip()
            if quantization is not None
            else None
        ),
        vram_required_gb=vram_required_gb,
        license=(
            license.strip()
            if license is not None
            else None
        ),
        status=status,
    )

    if model_version is None:
        raise ValueError(
            "Model version not found."
        )

    return model_version


def delete_model_version_service(
    db: Session,
    model_version_id,
):
    deleted = delete_model_version(
        db,
        model_version_id,
    )

    if not deleted:
        raise ValueError(
            "Model version not found."
        )

    return True