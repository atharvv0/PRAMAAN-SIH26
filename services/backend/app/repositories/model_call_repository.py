from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.model_call import ModelCall


def create_model_call(
    db: Session,
    task_id,
    model_version_id,
    purpose: str,
    input_tokens: int = None,
    output_tokens: int = None,
    latency_ms: int = None,
    status: str = "pending",
):
    model_call = ModelCall(
        task_id=task_id,
        model_version_id=model_version_id,
        purpose=purpose,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        status=status,
        created_at=datetime.now(timezone.utc),
    )

    db.add(model_call)
    db.commit()
    db.refresh(model_call)

    return model_call


def get_model_call(
    db: Session,
    model_call_id,
):
    return (
        db.query(ModelCall)
        .filter(
            ModelCall.model_call_id == model_call_id
        )
        .first()
    )


def get_model_calls_by_task(
    db: Session,
    task_id,
):
    return (
        db.query(ModelCall)
        .filter(
            ModelCall.task_id == task_id
        )
        .order_by(ModelCall.created_at)
        .all()
    )


def get_model_calls_by_model_version(
    db: Session,
    model_version_id,
):
    return (
        db.query(ModelCall)
        .filter(
            ModelCall.model_version_id == model_version_id
        )
        .order_by(ModelCall.created_at)
        .all()
    )


def get_model_calls(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(ModelCall)
        .order_by(ModelCall.created_at)
        .limit(limit)
        .all()
    )


def update_model_call(
    db: Session,
    model_call_id,
    purpose: str = None,
    input_tokens: int = None,
    output_tokens: int = None,
    latency_ms: int = None,
    status: str = None,
):
    model_call = get_model_call(
        db,
        model_call_id,
    )

    if model_call is None:
        return None

    if purpose is not None:
        model_call.purpose = purpose

    if input_tokens is not None:
        model_call.input_tokens = input_tokens

    if output_tokens is not None:
        model_call.output_tokens = output_tokens

    if latency_ms is not None:
        model_call.latency_ms = latency_ms

    if status is not None:
        model_call.status = status

    db.commit()
    db.refresh(model_call)

    return model_call


def delete_model_call(
    db: Session,
    model_call_id,
):
    model_call = get_model_call(
        db,
        model_call_id,
    )

    if model_call is None:
        return False

    db.delete(model_call)
    db.commit()

    return True