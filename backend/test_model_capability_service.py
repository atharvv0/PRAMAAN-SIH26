import pytest

from app.services.model_capability_service import (
    create_model_capability_service,
    get_model_capability_service,
    get_model_capabilities_by_version_service,
    get_model_capabilities_service,
    update_model_capability_service,
    delete_model_capability_service,
)


INVALID_MODEL_VERSION_ID = "00000000-0000-0000-0000-000000000000"


def test_create_model_capability_empty_capability(db):

    with pytest.raises(
        ValueError,
        match="Capability is required",
    ):
        create_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="",
            score=0.95,
        )


def test_create_model_capability_invalid_score_low(db):

    with pytest.raises(
        ValueError,
        match="Capability score must be between 0 and 1",
    ):
        create_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="text_generation_test",
            score=-0.1,
        )


def test_create_model_capability_invalid_score_high(db):

    with pytest.raises(
        ValueError,
        match="Capability score must be between 0 and 1",
    ):
        create_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="text_generation_test",
            score=1.1,
        )


def test_get_model_capability_empty_capability(db):

    with pytest.raises(
        ValueError,
        match="Capability is required",
    ):
        get_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="",
        )


def test_get_model_capability_not_found(db):

    with pytest.raises(
        ValueError,
        match="Model capability not found",
    ):
        get_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="not_existing_capability",
        )


def test_get_model_capabilities_by_version(db):

    result = get_model_capabilities_by_version_service(
        db=db,
        model_version_id=INVALID_MODEL_VERSION_ID,
    )

    assert isinstance(result, list)


def test_get_model_capabilities_invalid_limit(db):

    with pytest.raises(
        ValueError,
        match="Limit must be greater than 0",
    ):
        get_model_capabilities_service(
            db=db,
            limit=0,
        )


def test_update_model_capability_empty_capability(db):

    with pytest.raises(
        ValueError,
        match="Capability is required",
    ):
        update_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="",
            score=0.95,
        )


def test_update_model_capability_invalid_score_low(db):

    with pytest.raises(
        ValueError,
        match="Capability score must be between 0 and 1",
    ):
        update_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="not_existing_capability",
            score=-0.1,
        )


def test_update_model_capability_invalid_score_high(db):

    with pytest.raises(
        ValueError,
        match="Capability score must be between 0 and 1",
    ):
        update_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="not_existing_capability",
            score=1.1,
        )


def test_update_model_capability_not_found(db):

    with pytest.raises(
        ValueError,
        match="Model capability not found",
    ):
        update_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="not_existing_capability",
            score=0.98,
        )


def test_delete_model_capability_empty_capability(db):

    with pytest.raises(
        ValueError,
        match="Capability is required",
    ):
        delete_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="",
        )


def test_delete_model_capability_not_found(db):

    with pytest.raises(
        ValueError,
        match="Model capability not found",
    ):
        delete_model_capability_service(
            db=db,
            model_version_id=INVALID_MODEL_VERSION_ID,
            capability="not_existing_capability",
        )