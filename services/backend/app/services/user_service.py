from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
    update_user,
    delete_user,
)


def create_user_service(
    db: Session,
    email: str,
    display_name: str,
):
    # Validate email
    if not email or not email.strip():
        raise ValueError("Email is required.")

    email = email.strip().lower()

    # Validate display name
    if not display_name or not display_name.strip():
        raise ValueError("Display name is required.")

    display_name = display_name.strip()

    # Check duplicate email
    existing = get_user_by_email(
        db,
        email,
    )

    if existing is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    return create_user(
        db=db,
        email=email,
        display_name=display_name,
    )


def get_user_service(
    db: Session,
    user_id,
):
    user = get_user(
        db,
        user_id,
    )

    if user is None:
        raise ValueError(
            "User not found."
        )

    return user


def get_user_by_email_service(
    db: Session,
    email: str,
):
    if not email or not email.strip():
        raise ValueError(
            "Email is required."
        )

    email = email.strip().lower()

    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        raise ValueError(
            "User not found."
        )

    return user


def get_users_service(
    db: Session,
    limit: int = 100,
):
    if limit <= 0:
        raise ValueError(
            "Limit must be greater than 0."
        )

    return get_users(
        db,
        limit=limit,
    )


def update_user_service(
    db: Session,
    user_id,
    display_name: str = None,
    is_active: bool = None,
):
    user = get_user(
        db,
        user_id,
    )

    if user is None:
        raise ValueError(
            "User not found."
        )

    if display_name is not None:
        if not display_name.strip():
            raise ValueError(
                "Display name cannot be empty."
            )

        display_name = display_name.strip()

    return update_user(
        db=db,
        user_id=user_id,
        display_name=display_name,
        is_active=is_active,
    )


def delete_user_service(
    db: Session,
    user_id,
):
    deleted = delete_user(
        db,
        user_id,
    )

    if not deleted:
        raise ValueError(
            "User not found."
        )

    return True