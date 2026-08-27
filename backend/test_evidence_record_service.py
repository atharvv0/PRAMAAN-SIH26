import pytest

from app.services.evidence_record_service import (
    create_evidence_record_service,
    get_evidence_record_service,
    get_evidence_by_task_service,
    get_evidence_by_document_service,
    get_evidence_by_chunk_service,
    get_evidence_by_model_call_service,
    get_evidence_records_service,
    update_evidence_record_service,
    delete_evidence_record_service,
)


def test_create_evidence_record_empty_claim_text(db):

    with pytest.raises(
        ValueError,
        match="Claim text is required",
    ):
        create_evidence_record_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            claim_text="",
        )


def test_create_evidence_record_invalid_confidence(db):

    with pytest.raises(
        ValueError,
        match="Confidence must be between 0 and 1",
    ):
        create_evidence_record_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            claim_text="Test claim",
            confidence=1.5,
        )


def test_create_evidence_record_negative_confidence(db):

    with pytest.raises(
        ValueError,
        match="Confidence must be between 0 and 1",
    ):
        create_evidence_record_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            claim_text="Test claim",
            confidence=-0.1,
        )


def test_create_evidence_record_invalid_validation_status(db):

    with pytest.raises(
        ValueError,
        match="Invalid validation status",
    ):
        create_evidence_record_service(
            db=db,
            task_id="00000000-0000-0000-0000-000000000000",
            claim_text="Test claim",
            validation_status="invalid",
        )


def test_get_evidence_record_not_found(db):

    with pytest.raises(
        ValueError,
        match="Evidence record not found",
    ):
        get_evidence_record_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )


def test_get_evidence_records_invalid_limit(db):

    with pytest.raises(
        ValueError,
        match="Limit must be greater than 0",
    ):
        get_evidence_records_service(
            db,
            0,
        )


def test_update_evidence_record_empty_claim_text(db):

    with pytest.raises(
        ValueError,
        match="Claim text cannot be empty",
    ):
        update_evidence_record_service(
            db=db,
            evidence_id="00000000-0000-0000-0000-000000000000",
            claim_text="",
        )


def test_update_evidence_record_invalid_confidence(db):

    with pytest.raises(
        ValueError,
        match="Confidence must be between 0 and 1",
    ):
        update_evidence_record_service(
            db=db,
            evidence_id="00000000-0000-0000-0000-000000000000",
            confidence=2,
        )


def test_update_evidence_record_invalid_validation_status(db):

    with pytest.raises(
        ValueError,
        match="Invalid validation status",
    ):
        update_evidence_record_service(
            db=db,
            evidence_id="00000000-0000-0000-0000-000000000000",
            validation_status="invalid",
        )


def test_update_evidence_record_not_found(db):

    with pytest.raises(
        ValueError,
        match="Evidence record not found",
    ):
        update_evidence_record_service(
            db=db,
            evidence_id="00000000-0000-0000-0000-000000000000",
            claim_text="Updated claim",
        )


def test_delete_evidence_record_not_found(db):

    with pytest.raises(
        ValueError,
        match="Evidence record not found",
    ):
        delete_evidence_record_service(
            db,
            "00000000-0000-0000-0000-000000000000",
        )