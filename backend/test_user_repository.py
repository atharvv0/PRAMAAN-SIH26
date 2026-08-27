from app.db.session import SessionLocal
from app.repositories.user_repository import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
)


db = SessionLocal()

try:
    user = create_user(
        db,
        email="test@pramaan.local",
        display_name="Test User",
    )

    print("Created User:")
    print(user.user_id)
    print(user.email)
    print(user.display_name)

    found = get_user(db, user.user_id)

    print("\nGet User:")
    print(found.email)

    found_by_email = get_user_by_email(
        db,
        "test@pramaan.local",
    )

    print("\nGet By Email:")
    print(found_by_email.display_name)

    users = get_users(db)

    print("\nTotal Users:", len(users))

finally:
    db.close()