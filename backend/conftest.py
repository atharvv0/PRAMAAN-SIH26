import pytest

from app.db.session import SessionLocal


@pytest.fixture
def db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()