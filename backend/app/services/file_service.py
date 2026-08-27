from sqlalchemy.orm import Session

from app.repositories.file_repository import (
    create_file,
    get_file,
    get_files_by_project,
    get_files_by_user,
    get_file_by_sha256,
    get_files,
    update_file,
    delete_file,
)


VALID_SENSITIVITY_CLASSES = {
    "public",
    "internal",
    "confidential",
    "restricted",
}


def create_file_service(
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
    if not filename or not filename.strip():
        raise ValueError("Filename is required.")

    if not mime_type or not mime_type.strip():
        raise ValueError("MIME type is required.")

    if size_bytes is None or size_bytes < 0:
        raise ValueError("File size cannot be negative.")

    if not storage_path or not storage_path.strip():
        raise ValueError("Storage path is required.")

    if not sha256 or not sha256.strip():
        raise ValueError("SHA256 is required.")

    if sensitivity_class not in VALID_SENSITIVITY_CLASSES:
        raise ValueError("Invalid sensitivity class.")

    existing = get_file_by_sha256(
        db,
        sha256.strip(),
    )

    if existing is not None:
        raise ValueError(
            "A file with this SHA256 already exists."
        )

    return create_file(
        db=db,
        project_id=project_id,
        uploaded_by=uploaded_by,
        filename=filename.strip(),
        mime_type=mime_type.strip(),
        size_bytes=size_bytes,
        storage_path=storage_path.strip(),
        sha256=sha256.strip(),
        sensitivity_class=sensitivity_class,
    )


def get_file_service(
    db: Session,
    file_id,
):
    file = get_file(
        db,
        file_id,
    )

    if file is None:
        raise ValueError("File not found.")

    return file


def get_files_by_project_service(
    db: Session,
    project_id,
):
    return get_files_by_project(
        db,
        project_id,
    )


def get_files_by_user_service(
    db: Session,
    uploaded_by,
):
    return get_files_by_user(
        db,
        uploaded_by,
    )


def get_file_by_sha256_service(
    db: Session,
    sha256: str,
):
    if not sha256 or not sha256.strip():
        raise ValueError("SHA256 is required.")

    file = get_file_by_sha256(
        db,
        sha256.strip(),
    )

    if file is None:
        raise ValueError("File not found.")

    return file


def get_files_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_files(
        db,
        limit=limit,
    )


def update_file_service(
    db: Session,
    file_id,
    filename: str = None,
    sensitivity_class: str = None,
):
    if filename is not None and not filename.strip():
        raise ValueError(
            "Filename cannot be empty."
        )

    if (
        sensitivity_class is not None
        and sensitivity_class not in VALID_SENSITIVITY_CLASSES
    ):
        raise ValueError(
            "Invalid sensitivity class."
        )

    file = update_file(
        db=db,
        file_id=file_id,
        filename=(
            filename.strip()
            if filename is not None
            else None
        ),
        sensitivity_class=sensitivity_class,
    )

    if file is None:
        raise ValueError("File not found.")

    return file


def delete_file_service(
    db: Session,
    file_id,
):
    deleted = delete_file(
        db,
        file_id,
    )

    if not deleted:
        raise ValueError("File not found.")

    return True