from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


def create_chunk(
    db: Session,
    document_id,
    chunk_index: int,
    text: str,
    page_no: int = None,
    region_json: dict = None,
    qdrant_point_id: str = None,
):
    chunk = DocumentChunk(
        document_id=document_id,
        chunk_index=chunk_index,
        page_no=page_no,
        region_json=region_json,
        text=text,
        qdrant_point_id=qdrant_point_id,
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


def get_chunk(
    db: Session,
    chunk_id,
):
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.chunk_id == chunk_id)
        .first()
    )


def get_chunks_by_document(
    db: Session,
    document_id,
):
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )


def get_chunk_by_index(
    db: Session,
    document_id,
    chunk_index: int,
):
    return (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.chunk_index == chunk_index,
        )
        .first()
    )


def get_chunks(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(DocumentChunk)
        .limit(limit)
        .all()
    )


def update_chunk(
    db: Session,
    chunk_id,
    text: str = None,
    page_no: int = None,
    region_json: dict = None,
    qdrant_point_id: str = None,
):
    chunk = get_chunk(db, chunk_id)

    if chunk is None:
        return None

    if text is not None:
        chunk.text = text

    if page_no is not None:
        chunk.page_no = page_no

    if region_json is not None:
        chunk.region_json = region_json

    if qdrant_point_id is not None:
        chunk.qdrant_point_id = qdrant_point_id

    db.commit()
    db.refresh(chunk)

    return chunk


def delete_chunk(
    db: Session,
    chunk_id,
):
    chunk = get_chunk(db, chunk_id)

    if chunk is None:
        return False

    db.delete(chunk)
    db.commit()

    return True