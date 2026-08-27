from app.db.session import SessionLocal

from app.services.document_chunk_service import (
    create_document_chunk_service,
    get_document_chunk_service,
    get_document_chunks_by_document_service,
    get_document_chunk_by_index_service,
    get_document_chunks_service,
    update_document_chunk_service,
)

from app.models.document import Document


db = SessionLocal()

try:

    # --------------------------------------------------
    # GET EXISTING DOCUMENT
    # --------------------------------------------------

    document = db.query(Document).first()

    if document is None:
        print("No document found.")
    else:

        # --------------------------------------------------
        # GET EXISTING CHUNKS
        # --------------------------------------------------

        existing_chunks = (
            get_document_chunks_by_document_service(
                db,
                document.document_id,
            )
        )

        # --------------------------------------------------
        # GENERATE UNIQUE CHUNK INDEX
        # --------------------------------------------------

        if existing_chunks:
            chunk_index = max(
                chunk.chunk_index
                for chunk in existing_chunks
            ) + 1
        else:
            chunk_index = 1

        print("Using Chunk Index:", chunk_index)

        # --------------------------------------------------
        # CREATE DOCUMENT CHUNK
        # --------------------------------------------------

        chunk = create_document_chunk_service(
            db=db,
            document_id=document.document_id,
            chunk_index=chunk_index,
            text="This is a test document chunk for PRAMAAN.",
            page_no=1,
            region_json={
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            },
            qdrant_point_id=(
                "test-qdrant-point-"
                + str(chunk_index)
            ),
        )

        print("\nCreated Document Chunk:")
        print("Chunk ID:", chunk.chunk_id)
        print("Document ID:", chunk.document_id)
        print("Chunk Index:", chunk.chunk_index)
        print("Text:", chunk.text)
        print("Page No:", chunk.page_no)
        print("Region:", chunk.region_json)
        print("Qdrant Point ID:", chunk.qdrant_point_id)

        # --------------------------------------------------
        # GET BY CHUNK ID
        # --------------------------------------------------

        found = get_document_chunk_service(
            db,
            chunk.chunk_id,
        )

        print("\nGet Document Chunk:")
        print("Chunk ID:", found.chunk_id)
        print("Text:", found.text)

        # --------------------------------------------------
        # GET ALL CHUNKS FOR DOCUMENT
        # --------------------------------------------------

        document_chunks = (
            get_document_chunks_by_document_service(
                db,
                document.document_id,
            )
        )

        print(
            "\nChunks for Document:",
            len(document_chunks),
        )

        # --------------------------------------------------
        # GET BY DOCUMENT + CHUNK INDEX
        # --------------------------------------------------

        indexed_chunk = (
            get_document_chunk_by_index_service(
                db,
                document.document_id,
                chunk_index,
            )
        )

        print("\nGet By Index:")
        print("Chunk ID:", indexed_chunk.chunk_id)
        print("Chunk Index:", indexed_chunk.chunk_index)
        print("Text:", indexed_chunk.text)

        # --------------------------------------------------
        # UPDATE CHUNK
        # --------------------------------------------------

        updated = update_document_chunk_service(
            db=db,
            chunk_id=chunk.chunk_id,
            text="Updated test document chunk.",
            page_no=2,
        )

        print("\nUpdated Chunk:")
        print("Chunk ID:", updated.chunk_id)
        print("Text:", updated.text)
        print("Page No:", updated.page_no)

        # --------------------------------------------------
        # GET ALL DOCUMENT CHUNKS
        # --------------------------------------------------

        all_chunks = get_document_chunks_service(
            db,
            limit=100,
        )

        print(
            "\nTotal Document Chunks:",
            len(all_chunks),
        )

finally:
    db.close()