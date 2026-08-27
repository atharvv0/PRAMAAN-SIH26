from sqlalchemy.orm import Session

from app.repositories.document_chunk_repository import (
    create_chunk,
    get_chunk,
    get_chunks_by_document,
    get_chunk_by_index,
    get_chunks,
    update_chunk,
    delete_chunk,
)


def create_document_chunk_service(
    db: Session,
    document_id,
    chunk_index: int,
    text: str,
    page_no: int = None,
    region_json: dict = None,
    qdrant_point_id: str = None,
):
    if chunk_index < 0:
        raise ValueError(
            "Chunk index cannot be negative."
        )

    if not text or not text.strip():
        raise ValueError(
            "Chunk text is required."
        )

    if page_no is not None and page_no <= 0:
        raise ValueError(
            "Page number must be greater than 0."
        )

    existing = get_chunk_by_index(
        db,
        document_id,
        chunk_index,
    )

    if existing is not None:
        raise ValueError(
            "This chunk index already exists for this document."
        )

    return create_chunk(
        db=db,
        document_id=document_id,
        chunk_index=chunk_index,
        text=text.strip(),
        page_no=page_no,
        region_json=region_json,
        qdrant_point_id=qdrant_point_id,
    )


def get_document_chunk_service(
    db: Session,
    chunk_id,
):
    chunk = get_chunk(
        db,
        chunk_id,
    )

    if chunk is None:
        raise ValueError(
            "Document chunk not found."
        )

    return chunk


def get_document_chunks_by_document_service(
    db: Session,
    document_id,
):
    return get_chunks_by_document(
        db,
        document_id,
    )


def get_document_chunk_by_index_service(
    db: Session,
    document_id,
    chunk_index: int,
):
    if chunk_index < 0:
        raise ValueError(
            "Chunk index cannot be negative."
        )

    chunk = get_chunk_by_index(
        db,
        document_id,
        chunk_index,
    )

    if chunk is None:
        raise ValueError(
            "Document chunk not found."
        )

    return chunk


def get_document_chunks_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_chunks(
        db,
        limit=limit,
    )


def update_document_chunk_service(
    db: Session,
    chunk_id,
    text: str = None,
    page_no: int = None,
    region_json: dict = None,
    qdrant_point_id: str = None,
):
    if text is not None and not text.strip():
        raise ValueError(
            "Chunk text cannot be empty."
        )

    if page_no is not None and page_no <= 0:
        raise ValueError(
            "Page number must be greater than 0."
        )

    chunk = update_chunk(
        db=db,
        chunk_id=chunk_id,
        text=text.strip() if text is not None else None,
        page_no=page_no,
        region_json=region_json,
        qdrant_point_id=qdrant_point_id,
    )

    if chunk is None:
        raise ValueError(
            "Document chunk not found."
        )

    return chunk


def delete_document_chunk_service(
    db: Session,
    chunk_id,
):
    deleted = delete_chunk(
        db,
        chunk_id,
    )

    if not deleted:
        raise ValueError(
            "Document chunk not found."
        )

    return True