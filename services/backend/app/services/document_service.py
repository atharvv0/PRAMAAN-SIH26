from sqlalchemy.orm import Session

from app.repositories.document_repository import (
    create_document,
    get_document,
    get_documents_by_knowledge_base,
    get_documents_by_file,
    get_documents,
    update_document,
    delete_document,
)


VALID_STATUSES = {
    "pending",
    "processing",
    "processed",
    "completed",
    "failed",
}

VALID_SOURCE_TYPES = {
    "file",
    "text",
    "url",
    "inspection_report",
}

def create_document_service(
    db: Session,
    knowledge_base_id,
    file_id,
    title: str,
    version: str = "1",
    source_type: str = "file",
    status: str = "pending",
):
    if not title or not title.strip():
        raise ValueError("Document title is required.")

    if not version or not version.strip():
        raise ValueError("Document version is required.")

    if source_type not in VALID_SOURCE_TYPES:
        raise ValueError("Invalid document source type.")

    if status not in VALID_STATUSES:
        raise ValueError("Invalid document status.")

    return create_document(
        db=db,
        knowledge_base_id=knowledge_base_id,
        file_id=file_id,
        title=title.strip(),
        version=version.strip(),
        source_type=source_type,
        status=status,
    )


def get_document_service(
    db: Session,
    document_id,
):
    document = get_document(
        db,
        document_id,
    )

    if document is None:
        raise ValueError("Document not found.")

    return document


def get_documents_by_knowledge_base_service(
    db: Session,
    knowledge_base_id,
):
    return get_documents_by_knowledge_base(
        db,
        knowledge_base_id,
    )


def get_documents_by_file_service(
    db: Session,
    file_id,
):
    return get_documents_by_file(
        db,
        file_id,
    )


def get_documents_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_documents(
        db,
        limit=limit,
    )


def update_document_service(
    db: Session,
    document_id,
    title: str = None,
    version: str = None,
    source_type: str = None,
    status: str = None,
):
    if title is not None and not title.strip():
        raise ValueError(
            "Document title cannot be empty."
        )

    if version is not None and not version.strip():
        raise ValueError(
            "Document version cannot be empty."
        )

    if (
        source_type is not None
        and source_type not in VALID_SOURCE_TYPES
    ):
        raise ValueError(
            "Invalid document source type."
        )

    if (
        status is not None
        and status not in VALID_STATUSES
    ):
        raise ValueError(
            "Invalid document status."
        )

    document = update_document(
        db=db,
        document_id=document_id,
        title=(
            title.strip()
            if title is not None
            else None
        ),
        version=(
            version.strip()
            if version is not None
            else None
        ),
        source_type=source_type,
        status=status,
    )

    if document is None:
        raise ValueError("Document not found.")

    return document


def delete_document_service(
    db: Session,
    document_id,
):
    deleted = delete_document(
        db,
        document_id,
    )

    if not deleted:
        raise ValueError("Document not found.")

    return True