from sqlalchemy.orm import Session

from app.repositories.model_call_repository import (
    create_model_call,
    get_model_call,
    get_model_calls_by_task,
    get_model_calls_by_model_version,
    get_model_calls,
    update_model_call,
    delete_model_call,
)


VALID_STATUSES = {
    "pending",
    "running",
    "completed",
    "failed",
}


def create_model_call_service(
    db: Session,
    task_id,
    model_version_id,
    purpose: str,
    input_tokens: int = None,
    output_tokens: int = None,
    latency_ms: int = None,
    status: str = "pending",
):
    if not purpose or not purpose.strip():
        raise ValueError(
            "Model call purpose is required."
        )

    if status not in VALID_STATUSES:
        raise ValueError(
            "Invalid model call status."
        )

    if input_tokens is not None and input_tokens < 0:
        raise ValueError(
            "Input tokens cannot be negative."
        )

    if output_tokens is not None and output_tokens < 0:
        raise ValueError(
            "Output tokens cannot be negative."
        )

    if latency_ms is not None and latency_ms < 0:
        raise ValueError(
            "Latency cannot be negative."
        )

    return create_model_call(
        db=db,
        task_id=task_id,
        model_version_id=model_version_id,
        purpose=purpose.strip(),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        status=status,
    )


def get_model_call_service(
    db: Session,
    model_call_id,
):
    model_call = get_model_call(
        db,
        model_call_id,
    )

    if model_call is None:
        raise ValueError(
            "Model call not found."
        )

    return model_call


def get_model_calls_by_task_service(
    db: Session,
    task_id,
):
    return get_model_calls_by_task(
        db,
        task_id,
    )


def get_model_calls_by_model_version_service(
    db: Session,
    model_version_id,
):
    return get_model_calls_by_model_version(
        db,
        model_version_id,
    )


def get_model_calls_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_model_calls(
        db,
        limit=limit,
    )


def update_model_call_service(
    db: Session,
    model_call_id,
    purpose: str = None,
    input_tokens: int = None,
    output_tokens: int = None,
    latency_ms: int = None,
    status: str = None,
):
    if purpose is not None and not purpose.strip():
        raise ValueError(
            "Purpose cannot be empty."
        )

    if status is not None and status not in VALID_STATUSES:
        raise ValueError(
            "Invalid model call status."
        )

    if input_tokens is not None and input_tokens < 0:
        raise ValueError(
            "Input tokens cannot be negative."
        )

    if output_tokens is not None and output_tokens < 0:
        raise ValueError(
            "Output tokens cannot be negative."
        )

    if latency_ms is not None and latency_ms < 0:
        raise ValueError(
            "Latency cannot be negative."
        )

    model_call = update_model_call(
        db=db,
        model_call_id=model_call_id,
        purpose=(
            purpose.strip()
            if purpose is not None
            else None
        ),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        status=status,
    )

    if model_call is None:
        raise ValueError(
            "Model call not found."
        )

    return model_call


def delete_model_call_service(
    db: Session,
    model_call_id,
):
    deleted = delete_model_call(
        db,
        model_call_id,
    )

    if not deleted:
        raise ValueError(
            "Model call not found."
        )

    return True