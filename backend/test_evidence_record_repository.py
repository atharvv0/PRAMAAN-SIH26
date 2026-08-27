from app.db.session import SessionLocal

from app.repositories.evidence_record_repository import (
    create_evidence_record,
    get_evidence_record,
    get_evidence_by_task,
    get_evidence_by_document,
    get_evidence_by_chunk,
    get_evidence_by_model_call,
    get_evidence_records,
    update_evidence_record,
)

from app.models.task import Task
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.model_call import ModelCall


db = SessionLocal()

try:

    task = db.query(Task).first()
    document = db.query(Document).first()
    chunk = db.query(DocumentChunk).first()
    model_call = db.query(ModelCall).first()

    if task is None:
        print("No task found.")

    else:

        evidence = create_evidence_record(
            db=db,
            task_id=task.task_id,
            claim_text="Repository test evidence claim.",
            document_id=document.document_id if document else None,
            chunk_id=chunk.chunk_id if chunk else None,
            model_call_id=(
                model_call.model_call_id
                if model_call
                else None
            ),
            confidence=0.95,
            validation_status="pending",
        )

        print("Created Evidence Record:")
        print(
            "Evidence ID:",
            evidence.evidence_id,
        )
        print(
            "Task ID:",
            evidence.task_id,
        )
        print(
            "Claim:",
            evidence.claim_text,
        )
        print(
            "Document ID:",
            evidence.document_id,
        )
        print(
            "Chunk ID:",
            evidence.chunk_id,
        )
        print(
            "Model Call ID:",
            evidence.model_call_id,
        )
        print(
            "Confidence:",
            evidence.confidence,
        )
        print(
            "Validation Status:",
            evidence.validation_status,
        )
        print(
            "Created At:",
            evidence.created_at,
        )

        found = get_evidence_record(
            db,
            evidence.evidence_id,
        )

        print("\nGet Evidence:")
        print(found.claim_text)

        task_evidence = get_evidence_by_task(
            db,
            task.task_id,
        )

        print(
            "\nEvidence for Task:",
            len(task_evidence),
        )

        if document:
            document_evidence = get_evidence_by_document(
                db,
                document.document_id,
            )

            print(
                "Evidence for Document:",
                len(document_evidence),
            )

        if chunk:
            chunk_evidence = get_evidence_by_chunk(
                db,
                chunk.chunk_id,
            )

            print(
                "Evidence for Chunk:",
                len(chunk_evidence),
            )

        if model_call:
            model_call_evidence = get_evidence_by_model_call(
                db,
                model_call.model_call_id,
            )

            print(
                "Evidence for Model Call:",
                len(model_call_evidence),
            )

        updated = update_evidence_record(
            db,
            evidence.evidence_id,
            confidence=0.98,
            validation_status="validated",
        )

        print("\nUpdated Evidence:")
        print(
            "Confidence:",
            updated.confidence,
        )
        print(
            "Validation Status:",
            updated.validation_status,
        )

        all_evidence = get_evidence_records(db)

        print(
            "\nTotal Evidence Records:",
            len(all_evidence),
        )

finally:
    db.close()