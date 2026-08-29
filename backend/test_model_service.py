import uuid
import pytest

from app.services.model_service import (
    create_model_service,
    get_model_service,
    get_model_by_name_service,
    get_models_service,
    get_models_by_runtime_service,
    update_model_service,
    delete_model_service,
)


INVALID_MODEL_ID = "00000000-0000-0000-0000-000000000000"


def test_create_model_empty_name(db):

    with pytest.raises(
        ValueError,
        match="Model name is required",
    ):
        create_model_service(
            db=db,
            name="",
            runtime="test_runtime",
        )


def test_create_model_empty_runtime(db):

    with pytest.raises(
        ValueError,
        match="Model runtime is required",
    ):
        create_model_service(
            db=db,
            name="test_model",
            runtime="",
        )


def test_create_model_duplicate_name(db):

    unique_name = f"duplicate_test_model_{uuid.uuid4().hex}"

    create_model_service(
        db=db,
        name=unique_name,
        runtime="test_runtime",
    )

    with pytest.raises(
        ValueError,
        match="A model with this name already exists",
    ):
        create_model_service(
            db=db,
            name=unique_name,
            runtime="test_runtime",
        )


def test_get_model_not_found(db):

    with pytest.raises(
        ValueError,
        match="Model not found",
    ):
        get_model_service(
            db=db,
            model_id=INVALID_MODEL_ID,
        )


def test_get_model_by_name_not_found(db):

    with pytest.raises(
        ValueError,
        match="Model not found",
    ):
        get_model_by_name_service(
            db=db,
            name="not_existing_model",
        )


def test_get_models(db):

    result = get_models_service(
        db=db,
        limit=100,
    )

    assert isinstance(result, list)


def test_get_models_by_runtime_empty_runtime(db):

    with pytest.raises(
        ValueError,
        match="Runtime is required",
    ):
        get_models_by_runtime_service(
            db=db,
            runtime="",
        )


def test_get_models_by_runtime(db):

    result = get_models_by_runtime_service(
        db=db,
        runtime="test_runtime",
    )

    assert isinstance(result, list)


def test_update_model_not_found(db):

    with pytest.raises(
        ValueError,
        match="Model not found",
    ):
        update_model_service(
            db=db,
            model_id=INVALID_MODEL_ID,
            name="updated_model",
        )


def test_update_model_empty_name(db):

    with pytest.raises(
        ValueError,
        match="Model not found",
    ):
        update_model_service(
            db=db,
            model_id=INVALID_MODEL_ID,
            name="",
        )


def test_update_model_empty_runtime(db):

    with pytest.raises(
        ValueError,
        match="Model not found",
    ):
        update_model_service(
            db=db,
            model_id=INVALID_MODEL_ID,
            runtime="",
        )


def test_delete_model_not_found(db):

    with pytest.raises(
        ValueError,
        match="Model not found",
    ):
        delete_model_service(
            db=db,
            model_id=INVALID_MODEL_ID,
        )