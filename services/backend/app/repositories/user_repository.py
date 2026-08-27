from sqlalchemy.orm import Session

from app.models.user import User


def create_user(
    db: Session,
    email: str,
    display_name: str,
) -> User:
    user = User(
        email=email,
        display_name=display_name,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id,
):
    return (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_users(
    db: Session,
    limit: int = 100,
):
    return (
        db.query(User)
        .limit(limit)
        .all()
    )


def update_user(
    db: Session,
    user_id,
    display_name: str = None,
    is_active: bool = None,
):
    user = get_user(db, user_id)

    if user is None:
        return None

    if display_name is not None:
        user.display_name = display_name

    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user_id,
):
    user = get_user(db, user_id)

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True