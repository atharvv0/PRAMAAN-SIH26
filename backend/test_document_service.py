from app.db.session import SessionLocal

from app.services.document_service import (
    create_document_service,
    get_document_service,
    get_documents_by_knowledge_base_service,
    get_documents_by_file_service,
    get_documents_service,
    update_document_service,
)

from app.models.knowledge_base import KnowledgeBase
from app.models.file import File


db = SessionLocal()

try:

    knowledge_base = db.query(KnowledgeBase).first()
    file = db.query(File).first()

    if knowledge_base is None:
        print("No knowledge base found.")

    elif file is None:
        print("No file found.")

    else:

        document = create_document_service(
            db=db,
            knowledge_base_id=knowledge_base.knowledge_base_id,
            file_id=file.file_id,
            title="Service Test Document",
            version="1.0",
            source_type="inspection_report",
        )

        print("Created Document:")
        print("ID:", document.document_id)
        print(
            "Knowledge Base ID:",
            document.knowledge_base_id,
        )
        print("File ID:", document.file_id)
        print("Title:", document.title)
        print("Version:", document.version)
        print("Source Type:", document.source_type)
        print("Status:", document.status)

        # Get by ID
        found = get_document_service(
            db,
            document.document_id,
        )

        print("\nGet Document:")
        print(found.title)

        # Get by knowledge base
        kb_documents = (
            get_documents_by_knowledge_base_service(
                db,
                knowledge_base.knowledge_base_id,
            )
        )

        print(
            "\nDocuments in Knowledge Base:",
            len(kb_documents),
        )

        # Get by file
        file_documents = get_documents_by_file_service(
            db,
            file.file_id,
        )

        print(
            "Documents for File:",
            len(file_documents),
        )

        # Get all documents
        documents = get_documents_service(
            db,
            limit=100,
        )

        print(
            "Total Documents:",
            len(documents),
        )

        # Update
        updated = update_document_service(
            db=db,
            document_id=document.document_id,
            title="Updated Service Test Document",
            status="processed",
        )

        print("\nUpdated Document:")
        print("Title:", updated.title)
        print("Status:", updated.status)

finally:
    db.close()