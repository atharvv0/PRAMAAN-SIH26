from sqlalchemy.orm import Session

from app.models.model import Model


def create_model(
    db: Session,
    name: str,
    runtime: str,
    provider_family: str = None,
    status: str = "active",
):
    model = Model(
        name=name,
        provider_family=provider_family,
        runtime=runtime,
        status=status,
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    return model


def get_model(
    db: Session,
    model_id,
):
    return (
        db.query(Model)
        .filter(Model.model_id == model_id)
        .first()
    )


def get_model_by_name(
    db: Session,
    name: str,
):
    return (
        db.query(Model)
        .filter(Model.name == name)
        .first()
    )


def get_models(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Model)
        .limit(limit)
        .all()
    )


def get_models_by_runtime(
    db: Session,
    runtime: str,
):
    return (
        db.query(Model)
        .filter(Model.runtime == runtime)
        .all()
    )


def update_model(
    db: Session,
    model_id,
    name: str = None,
    provider_family: str = None,
    runtime: str = None,
    status: str = None,
):
    model = get_model(db, model_id)

    if model is None:
        return None

    if name is not None:
        model.name = name

    if provider_family is not None:
        model.provider_family = provider_family

    if runtime is not None:
        model.runtime = runtime

    if status is not None:
        model.status = status

    db.commit()
    db.refresh(model)

    return model


def delete_model(
    db: Session,
    model_id,
):
    model = get_model(db, model_id)

    if model is None:
        return False

    db.delete(model)
    db.commit()

    return True