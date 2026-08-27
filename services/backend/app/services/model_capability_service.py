from sqlalchemy.orm import Session

from app.repositories.model_capability_repository import (
    create_capability,
    get_capability,
    get_capabilities_by_model_version,
    get_capabilities,
    update_capability,
    delete_capability,
)


def create_model_capability_service(
    db: Session,
    model_version_id,
    capability: str,
    score: float = None,
):
    if not capability or not capability.strip():
        raise ValueError(
            "Capability is required."
        )

    if score is not None and not 0 <= score <= 1:
        raise ValueError(
            "Capability score must be between 0 and 1."
        )

    capability = capability.strip()

    existing = get_capability(
        db,
        model_version_id,
        capability,
    )

    if existing is not None:
        raise ValueError(
            "This capability already exists for this model version."
        )

    return create_capability(
        db=db,
        model_version_id=model_version_id,
        capability=capability,
        score=score,
    )


def get_model_capability_service(
    db: Session,
    model_version_id,
    capability: str,
):
    if not capability or not capability.strip():
        raise ValueError(
            "Capability is required."
        )

    result = get_capability(
        db,
        model_version_id,
        capability.strip(),
    )

    if result is None:
        raise ValueError(
            "Model capability not found."
        )

    return result


def get_model_capabilities_by_version_service(
    db: Session,
    model_version_id,
):
    return get_capabilities_by_model_version(
        db,
        model_version_id,
    )


def get_model_capabilities_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_capabilities(
        db,
        limit=limit,
    )


def update_model_capability_service(
    db: Session,
    model_version_id,
    capability: str,
    score: float = None,
):
    if not capability or not capability.strip():
        raise ValueError(
            "Capability is required."
        )

    if score is not None and not 0 <= score <= 1:
        raise ValueError(
            "Capability score must be between 0 and 1."
        )

    result = update_capability(
        db=db,
        model_version_id=model_version_id,
        capability=capability.strip(),
        score=score,
    )

    if result is None:
        raise ValueError(
            "Model capability not found."
        )

    return result


def delete_model_capability_service(
    db: Session,
    model_version_id,
    capability: str,
):
    if not capability or not capability.strip():
        raise ValueError(
            "Capability is required."
        )

    deleted = delete_capability(
        db,
        model_version_id,
        capability.strip(),
    )

    if not deleted:
        raise ValueError(
            "Model capability not found."
        )

    return True