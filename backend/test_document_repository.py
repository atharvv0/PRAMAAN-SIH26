from app.db.session import SessionLocal

from app.repositories.document_repository import (
    create_document,
    get_document,
    get_documents_by_knowledge_base,
    get_documents_by_file,
    get_documents,
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

        document = create_document(
            db=db,
            knowledge_base_id=knowledge_base.knowledge_base_id,
            file_id=file.file_id,
            title="Repository Test Document",
            version="1",
            source_type="file",
            status="pending",
        )

        print("Created Document:")
        print("Document ID:", document.document_id)
        print("Knowledge Base ID:", document.knowledge_base_id)
        print("File ID:", document.file_id)
        print("Title:", document.title)
        print("Version:", document.version)
        print("Source Type:", document.source_type)
        print("Status:", document.status)

        found = get_document(
            db,
            document.document_id,
        )

        print("\nGet Document:")
        print(found.title)

        kb_documents = get_documents_by_knowledge_base(
            db,
            knowledge_base.knowledge_base_id,
        )

        print(
            "\nDocuments in Knowledge Base:",
            len(kb_documents),
        )

        file_documents = get_documents_by_file(
            db,
            file.file_id,
        )

        print(
            "Documents for File:",
            len(file_documents),
        )

        documents = get_documents(db)

        print(
            "Total Documents:",
            len(documents),
        )

finally:
    db.close()