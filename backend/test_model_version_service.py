import pytest
from unittest.mock import patch, MagicMock

from app.services.model_version_service import (
    create_model_version_service,
    get_model_version_service,
    get_model_versions_by_model_service,
    get_model_version_by_version_service,
    get_model_versions_service,
    update_model_version_service,
    delete_model_version_service,
)


# ============================================================
# CREATE
# ============================================================

def test_create_model_version_empty_version():
    db = MagicMock()

    with pytest.raises(ValueError):
        create_model_version_service(
            db=db,
            model_id="model-id",
            version="",
            weights_path="/models/test",
            license="Apache-2.0",
        )


def test_create_model_version_empty_weights_path():
    db = MagicMock()

    with pytest.raises(ValueError):
        create_model_version_service(
            db=db,
            model_id="model-id",
            version="1.0",
            weights_path="",
            license="Apache-2.0",
        )


def test_create_model_version_empty_license():
    db = MagicMock()

    with pytest.raises(ValueError):
        create_model_version_service(
            db=db,
            model_id="model-id",
            version="1.0",
            weights_path="/models/test",
            license="",
        )


def test_create_model_version_invalid_status():
    db = MagicMock()

    with pytest.raises(ValueError):
        create_model_version_service(
            db=db,
            model_id="model-id",
            version="1.0",
            weights_path="/models/test",
            license="Apache-2.0",
            status="invalid",
        )


def test_create_model_version_negative_vram():
    db = MagicMock()

    with pytest.raises(ValueError):
        create_model_version_service(
            db=db,
            model_id="model-id",
            version="1.0",
            weights_path="/models/test",
            license="Apache-2.0",
            vram_required_gb=-1,
        )


def test_create_model_version_duplicate():
    db = MagicMock()

    existing_version = MagicMock()

    with patch(
        "app.services.model_version_service.get_model_version_by_version",
        return_value=existing_version,
    ):

        with pytest.raises(ValueError):
            create_model_version_service(
                db=db,
                model_id="model-id",
                version="1.0",
                weights_path="/models/test",
                license="Apache-2.0",
            )


# ============================================================
# GET
# ============================================================

def test_get_model_version_not_found():
    db = MagicMock()

    with patch(
        "app.services.model_version_service.get_model_version",
        return_value=None,
    ):

        with pytest.raises(ValueError):
            get_model_version_service(
                db=db,
                model_version_id="invalid-id",
            )


def test_get_model_version_by_version_empty_version():
    db = MagicMock()

    with pytest.raises(ValueError):
        get_model_version_by_version_service(
            db=db,
            model_id="model-id",
            version="",
        )


def test_get_model_version_by_version_not_found():
    db = MagicMock()

    with patch(
        "app.services.model_version_service.get_model_version_by_version",
        return_value=None,
    ):

        with pytest.raises(ValueError):
            get_model_version_by_version_service(
                db=db,
                model_id="model-id",
                version="1.0",
            )


def test_get_model_versions_invalid_limit():
    db = MagicMock()

    with pytest.raises(ValueError):
        get_model_versions_service(
            db=db,
            limit=0,
        )


def test_get_model_versions_by_model():
    db = MagicMock()

    expected = [MagicMock(), MagicMock()]

    with patch(
        "app.services.model_version_service.get_model_versions_by_model",
        return_value=expected,
    ):

        result = get_model_versions_by_model_service(
            db=db,
            model_id="model-id",
        )

        assert result == expected


# ============================================================
# UPDATE
# ============================================================

def test_update_model_version_empty_version():
    db = MagicMock()

    with pytest.raises(ValueError):
        update_model_version_service(
            db=db,
            model_version_id="model-id",
            version="",
        )


def test_update_model_version_empty_weights_path():
    db = MagicMock()

    with pytest.raises(ValueError):
        update_model_version_service(
            db=db,
            model_version_id="model-id",
            weights_path="",
        )


def test_update_model_version_empty_license():
    db = MagicMock()

    with pytest.raises(ValueError):
        update_model_version_service(
            db=db,
            model_version_id="model-id",
            license="",
        )


def test_update_model_version_invalid_status():
    db = MagicMock()

    with pytest.raises(ValueError):
        update_model_version_service(
            db=db,
            model_version_id="model-id",
            status="invalid",
        )


def test_update_model_version_negative_vram():
    db = MagicMock()

    with pytest.raises(ValueError):
        update_model_version_service(
            db=db,
            model_version_id="model-id",
            vram_required_gb=-5,
        )


def test_update_model_version_not_found():
    db = MagicMock()

    with patch(
        "app.services.model_version_service.update_model_version",
        return_value=None,
    ):

        with pytest.raises(ValueError):
            update_model_version_service(
                db=db,
                model_version_id="invalid-id",
                version="2.0",
            )


# ============================================================
# DELETE
# ============================================================

def test_delete_model_version_not_found():
    db = MagicMock()

    with patch(
        "app.services.model_version_service.delete_model_version",
        return_value=False,
    ):

        with pytest.raises(ValueError):
            delete_model_version_service(
                db=db,
                model_version_id="invalid-id",
            )