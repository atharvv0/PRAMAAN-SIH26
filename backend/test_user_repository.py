from uuid import uuid4

from app.db.session import SessionLocal
from app.repositories.user_repository import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
)


def test_user_repository():

    db = SessionLocal()

    try:
        email = f"test-{uuid4().hex}@pramaan.local"

        # Create User
        user = create_user(
            db,
            email=email,
            display_name="Test User",
        )

        assert user is not None
        assert user.email == email
        assert user.display_name == "Test User"

        # Get User
        found = get_user(
            db,
            user.user_id,
        )

        assert found is not None
        assert found.email == email

        # Get By Email
        found_by_email = get_user_by_email(
            db,
            email,
        )

        assert found_by_email is not None
        assert found_by_email.user_id == user.user_id

        # Get All Users
        users = get_users(db)

        assert len(users) >= 1

    finally:
        db.close()