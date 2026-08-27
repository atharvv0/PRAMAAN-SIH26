from app.db.session import SessionLocal

from app.repositories.document_chunk_repository import (
    create_chunk,
    get_chunk,
    get_chunks_by_document,
    get_chunk_by_index,
    get_chunks,
)

from app.models.document import Document


db = SessionLocal()

try:

    document = db.query(Document).first()

    if document is None:
        print("No document found.")

    else:

        # Avoid duplicate (document_id, chunk_index)
        existing = get_chunk_by_index(
            db,
            document.document_id,
            0,
        )

        if existing:
            print("Chunk already exists:")
            print("Chunk ID:", existing.chunk_id)
            print("Document ID:", existing.document_id)
            print("Chunk Index:", existing.chunk_index)
            print("Text:", existing.text)

            chunk = existing

        else:
            chunk = create_chunk(
                db=db,
                document_id=document.document_id,
                chunk_index=0,
                text="This is a repository test chunk.",
                page_no=1,
                region_json={
                    "x": 0,
                    "y": 0,
                    "width": 100,
                    "height": 100,
                },
                qdrant_point_id="test-qdrant-point-001",
            )

            print("Created Chunk:")
            print("Chunk ID:", chunk.chunk_id)
            print("Document ID:", chunk.document_id)
            print("Chunk Index:", chunk.chunk_index)
            print("Page:", chunk.page_no)
            print("Text:", chunk.text)
            print("Qdrant Point:", chunk.qdrant_point_id)

        found = get_chunk(
            db,
            chunk.chunk_id,
        )

        print("\nGet Chunk:")
        print(found.text)

        document_chunks = get_chunks_by_document(
            db,
            document.document_id,
        )

        print(
            "\nChunks in Document:",
            len(document_chunks),
        )

        indexed_chunk = get_chunk_by_index(
            db,
            document.document_id,
            chunk.chunk_index,
        )

        print(
            "Chunk by Index:",
            indexed_chunk.text,
        )

        chunks = get_chunks(db)

        print(
            "Total Chunks:",
            len(chunks),
        )

finally:
    db.close()