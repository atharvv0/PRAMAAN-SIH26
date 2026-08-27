from sqlalchemy.orm import Session

from app.models.model_capability import ModelCapability


def create_capability(
    db: Session,
    model_version_id,
    capability: str,
    score: float = None,
):
    model_capability = ModelCapability(
        model_version_id=model_version_id,
        capability=capability,
        score=score,
    )

    db.add(model_capability)
    db.commit()
    db.refresh(model_capability)

    return model_capability


def get_capability(
    db: Session,
    model_version_id,
    capability: str,
):
    return (
        db.query(ModelCapability)
        .filter(
            ModelCapability.model_version_id == model_version_id,
            ModelCapability.capability == capability,
        )
        .first()
    )


def get_capabilities_by_model_version(
    db: Session,
    model_version_id,
):
    return (
        db.query(ModelCapability)
        .filter(
            ModelCapability.model_version_id == model_version_id
        )
        .all()
    )


def get_capabilities(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(ModelCapability)
        .limit(limit)
        .all()
    )


def update_capability(
    db: Session,
    model_version_id,
    capability: str,
    score: float = None,
):
    model_capability = get_capability(
        db,
        model_version_id,
        capability,
    )

    if model_capability is None:
        return None

    if score is not None:
        model_capability.score = score

    db.commit()
    db.refresh(model_capability)

    return model_capability


def delete_capability(
    db: Session,
    model_version_id,
    capability: str,
):
    model_capability = get_capability(
        db,
        model_version_id,
        capability,
    )

    if model_capability is None:
        return False

    db.delete(model_capability)
    db.commit()

    return True