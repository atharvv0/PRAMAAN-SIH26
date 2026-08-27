from sqlalchemy.orm import Session

from app.repositories.evidence_record_repository import (
    create_evidence_record,
    get_evidence_record,
    get_evidence_by_task,
    get_evidence_by_document,
    get_evidence_by_chunk,
    get_evidence_by_model_call,
    get_evidence_records,
    update_evidence_record,
    delete_evidence_record,
)


VALID_VALIDATION_STATUSES = {
    "pending",
    "validated",
    "rejected",
}


def create_evidence_record_service(
    db: Session,
    task_id,
    claim_text: str,
    document_id=None,
    chunk_id=None,
    model_call_id=None,
    confidence: float = None,
    validation_status: str = "pending",
):
    if not claim_text or not claim_text.strip():
        raise ValueError(
            "Claim text is required."
        )

    if (
        confidence is not None
        and not 0 <= confidence <= 1
    ):
        raise ValueError(
            "Confidence must be between 0 and 1."
        )

    if validation_status not in VALID_VALIDATION_STATUSES:
        raise ValueError(
            "Invalid validation status."
        )

    return create_evidence_record(
        db=db,
        task_id=task_id,
        claim_text=claim_text.strip(),
        document_id=document_id,
        chunk_id=chunk_id,
        model_call_id=model_call_id,
        confidence=confidence,
        validation_status=validation_status,
    )


def get_evidence_record_service(
    db: Session,
    evidence_id,
):
    evidence = get_evidence_record(
        db,
        evidence_id,
    )

    if evidence is None:
        raise ValueError(
            "Evidence record not found."
        )

    return evidence


def get_evidence_by_task_service(
    db: Session,
    task_id,
):
    return get_evidence_by_task(
        db,
        task_id,
    )


def get_evidence_by_document_service(
    db: Session,
    document_id,
):
    return get_evidence_by_document(
        db,
        document_id,
    )


def get_evidence_by_chunk_service(
    db: Session,
    chunk_id,
):
    return get_evidence_by_chunk(
        db,
        chunk_id,
    )


def get_evidence_by_model_call_service(
    db: Session,
    model_call_id,
):
    return get_evidence_by_model_call(
        db,
        model_call_id,
    )


def get_evidence_records_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_evidence_records(
        db,
        limit=limit,
    )


def update_evidence_record_service(
    db: Session,
    evidence_id,
    claim_text: str = None,
    confidence: float = None,
    validation_status: str = None,
):
    if claim_text is not None and not claim_text.strip():
        raise ValueError(
            "Claim text cannot be empty."
        )

    if (
        confidence is not None
        and not 0 <= confidence <= 1
    ):
        raise ValueError(
            "Confidence must be between 0 and 1."
        )

    if (
        validation_status is not None
        and validation_status not in VALID_VALIDATION_STATUSES
    ):
        raise ValueError(
            "Invalid validation status."
        )

    evidence = update_evidence_record(
        db=db,
        evidence_id=evidence_id,
        claim_text=(
            claim_text.strip()
            if claim_text is not None
            else None
        ),
        confidence=confidence,
        validation_status=validation_status,
    )

    if evidence is None:
        raise ValueError(
            "Evidence record not found."
        )

    return evidence


def delete_evidence_record_service(
    db: Session,
    evidence_id,
):
    deleted = delete_evidence_record(
        db,
        evidence_id,
    )

    if not deleted:
        raise ValueError(
            "Evidence record not found."
        )

    return True