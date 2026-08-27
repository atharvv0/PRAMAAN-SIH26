from sqlalchemy.orm import Session

from app.models.model_version import ModelVersion


def create_model_version(
    db: Session,
    model_id,
    version: str,
    weights_path: str,
    license: str,
    quantization: str = None,
    vram_required_gb: float = None,
    status: str = "active",
):
    model_version = ModelVersion(
        model_id=model_id,
        version=version,
        weights_path=weights_path,
        quantization=quantization,
        vram_required_gb=vram_required_gb,
        license=license,
        status=status,
    )

    db.add(model_version)
    db.commit()
    db.refresh(model_version)

    return model_version


def get_model_version(
    db: Session,
    model_version_id,
):
    return (
        db.query(ModelVersion)
        .filter(
            ModelVersion.model_version_id == model_version_id
        )
        .first()
    )


def get_model_versions_by_model(
    db: Session,
    model_id,
):
    return (
        db.query(ModelVersion)
        .filter(ModelVersion.model_id == model_id)
        .all()
    )


def get_model_version_by_version(
    db: Session,
    model_id,
    version: str,
):
    return (
        db.query(ModelVersion)
        .filter(
            ModelVersion.model_id == model_id,
            ModelVersion.version == version,
        )
        .first()
    )


def get_model_versions(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(ModelVersion)
        .limit(limit)
        .all()
    )


def update_model_version(
    db: Session,
    model_version_id,
    version: str = None,
    weights_path: str = None,
    quantization: str = None,
    vram_required_gb: float = None,
    license: str = None,
    status: str = None,
):
    model_version = get_model_version(
        db,
        model_version_id,
    )

    if model_version is None:
        return None

    if version is not None:
        model_version.version = version

    if weights_path is not None:
        model_version.weights_path = weights_path

    if quantization is not None:
        model_version.quantization = quantization

    if vram_required_gb is not None:
        model_version.vram_required_gb = vram_required_gb

    if license is not None:
        model_version.license = license

    if status is not None:
        model_version.status = status

    db.commit()
    db.refresh(model_version)

    return model_version


def delete_model_version(
    db: Session,
    model_version_id,
):
    model_version = get_model_version(
        db,
        model_version_id,
    )

    if model_version is None:
        return False

    db.delete(model_version)
    db.commit()

    return True