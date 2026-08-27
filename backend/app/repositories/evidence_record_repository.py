from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.evidence_record import EvidenceRecord


def create_evidence_record(
    db: Session,
    task_id,
    claim_text: str,
    document_id=None,
    chunk_id=None,
    model_call_id=None,
    confidence: float = None,
    validation_status: str = "pending",
):
    evidence = EvidenceRecord(
        task_id=task_id,
        claim_text=claim_text,
        document_id=document_id,
        chunk_id=chunk_id,
        model_call_id=model_call_id,
        confidence=confidence,
        validation_status=validation_status,
        created_at=datetime.now(timezone.utc),
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def get_evidence_record(
    db: Session,
    evidence_id,
):
    return (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.evidence_id == evidence_id
        )
        .first()
    )


def get_evidence_by_task(
    db: Session,
    task_id,
):
    return (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.task_id == task_id
        )
        .order_by(EvidenceRecord.created_at)
        .all()
    )


def get_evidence_by_document(
    db: Session,
    document_id,
):
    return (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.document_id == document_id
        )
        .order_by(EvidenceRecord.created_at)
        .all()
    )


def get_evidence_by_chunk(
    db: Session,
    chunk_id,
):
    return (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.chunk_id == chunk_id
        )
        .order_by(EvidenceRecord.created_at)
        .all()
    )


def get_evidence_by_model_call(
    db: Session,
    model_call_id,
):
    return (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.model_call_id == model_call_id
        )
        .order_by(EvidenceRecord.created_at)
        .all()
    )


def get_evidence_records(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(EvidenceRecord)
        .order_by(EvidenceRecord.created_at)
        .limit(limit)
        .all()
    )


def update_evidence_record(
    db: Session,
    evidence_id,
    claim_text: str = None,
    confidence: float = None,
    validation_status: str = None,
):
    evidence = get_evidence_record(
        db,
        evidence_id,
    )

    if evidence is None:
        return None

    if claim_text is not None:
        evidence.claim_text = claim_text

    if confidence is not None:
        evidence.confidence = confidence

    if validation_status is not None:
        evidence.validation_status = validation_status

    db.commit()
    db.refresh(evidence)

    return evidence


def delete_evidence_record(
    db: Session,
    evidence_id,
):
    evidence = get_evidence_record(
        db,
        evidence_id,
    )

    if evidence is None:
        return False

    db.delete(evidence)
    db.commit()

    return True