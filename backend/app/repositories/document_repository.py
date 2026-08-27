from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    knowledge_base_id,
    file_id,
    title: str,
    version: str = "1",
    source_type: str = "file",
    status: str = "pending",
):
    document = Document(
        knowledge_base_id=knowledge_base_id,
        file_id=file_id,
        title=title,
        version=version,
        source_type=source_type,
        status=status,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document(
    db: Session,
    document_id,
):
    return (
        db.query(Document)
        .filter(Document.document_id == document_id)
        .first()
    )


def get_documents_by_knowledge_base(
    db: Session,
    knowledge_base_id,
):
    return (
        db.query(Document)
        .filter(
            Document.knowledge_base_id == knowledge_base_id
        )
        .all()
    )


def get_documents_by_file(
    db: Session,
    file_id,
):
    return (
        db.query(Document)
        .filter(Document.file_id == file_id)
        .all()
    )


def get_documents(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(Document)
        .limit(limit)
        .all()
    )


def update_document(
    db: Session,
    document_id,
    title: str = None,
    version: str = None,
    source_type: str = None,
    status: str = None,
):
    document = get_document(db, document_id)

    if document is None:
        return None

    if title is not None:
        document.title = title

    if version is not None:
        document.version = version

    if source_type is not None:
        document.source_type = source_type

    if status is not None:
        document.status = status

    db.commit()
    db.refresh(document)

    return document


def delete_document(
    db: Session,
    document_id,
):
    document = get_document(db, document_id)

    if document is None:
        return False

    db.delete(document)
    db.commit()

    return True