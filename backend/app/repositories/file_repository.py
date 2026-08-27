from sqlalchemy.orm import Session

from app.models.file import File


def create_file(
    db: Session,
    project_id,
    uploaded_by,
    filename: str,
    mime_type: str,
    size_bytes: int,
    storage_path: str,
    sha256: str,
    sensitivity_class: str = "confidential",
):
    file = File(
        project_id=project_id,
        uploaded_by=uploaded_by,
        filename=filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
        storage_path=storage_path,
        sha256=sha256,
        sensitivity_class=sensitivity_class,
    )

    db.add(file)
    db.commit()
    db.refresh(file)

    return file


def get_file(
    db: Session,
    file_id,
):
    return (
        db.query(File)
        .filter(File.file_id == file_id)
        .first()
    )


def get_files_by_project(
    db: Session,
    project_id,
):
    return (
        db.query(File)
        .filter(File.project_id == project_id)
        .all()
    )


def get_files_by_user(
    db: Session,
    uploaded_by,
):
    return (
        db.query(File)
        .filter(File.uploaded_by == uploaded_by)
        .all()
    )


def get_file_by_sha256(
    db: Session,
    sha256: str,
):
    return (
        db.query(File)
        .filter(File.sha256 == sha256)
        .first()
    )


def get_files(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(File)
        .limit(limit)
        .all()
    )


def update_file(
    db: Session,
    file_id,
    filename: str = None,
    sensitivity_class: str = None,
):
    file = get_file(db, file_id)

    if file is None:
        return None

    if filename is not None:
        file.filename = filename

    if sensitivity_class is not None:
        file.sensitivity_class = sensitivity_class

    db.commit()
    db.refresh(file)

    return file


def delete_file(
    db: Session,
    file_id,
):
    file = get_file(db, file_id)

    if file is None:
        return False

    db.delete(file)
    db.commit()

    return True