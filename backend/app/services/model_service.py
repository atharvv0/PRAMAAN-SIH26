from sqlalchemy.orm import Session

from app.repositories.model_repository import (
    create_model,
    get_model,
    get_model_by_name,
    get_models,
    get_models_by_runtime,
    update_model,
    delete_model,
)


def create_model_service(
    db: Session,
    name: str,
    runtime: str,
    provider_family: str = None,
):
    if not name or not name.strip():
        raise ValueError("Model name is required.")

    if not runtime or not runtime.strip():
        raise ValueError("Model runtime is required.")

    existing = get_model_by_name(
        db,
        name.strip(),
    )

    if existing is not None:
        raise ValueError(
            "A model with this name already exists."
        )

    return create_model(
        db=db,
        name=name.strip(),
        runtime=runtime.strip(),
        provider_family=provider_family,
        status="active",
    )


def get_model_service(
    db: Session,
    model_id,
):
    model = get_model(
        db,
        model_id,
    )

    if model is None:
        raise ValueError("Model not found.")

    return model


def get_model_by_name_service(
    db: Session,
    name: str,
):
    model = get_model_by_name(
        db,
        name,
    )

    if model is None:
        raise ValueError("Model not found.")

    return model


def get_models_service(
    db: Session,
    limit: int = 100,
):
    return get_models(
        db,
        limit=limit,
    )


def get_models_by_runtime_service(
    db: Session,
    runtime: str,
):
    if not runtime or not runtime.strip():
        raise ValueError("Runtime is required.")

    return get_models_by_runtime(
        db,
        runtime.strip(),
    )


def update_model_service(
    db: Session,
    model_id,
    name: str = None,
    provider_family: str = None,
    runtime: str = None,
    status: str = None,
):
    model = get_model(
        db,
        model_id,
    )

    if model is None:
        raise ValueError("Model not found.")

    if name is not None and not name.strip():
        raise ValueError("Model name cannot be empty.")

    if runtime is not None and not runtime.strip():
        raise ValueError("Model runtime cannot be empty.")

    return update_model(
        db=db,
        model_id=model_id,
        name=name.strip() if name is not None else None,
        provider_family=provider_family,
        runtime=runtime.strip() if runtime is not None else None,
        status=status,
    )


def delete_model_service(
    db: Session,
    model_id,
):
    deleted = delete_model(
        db,
        model_id,
    )

    if not deleted:
        raise ValueError("Model not found.")

    return True