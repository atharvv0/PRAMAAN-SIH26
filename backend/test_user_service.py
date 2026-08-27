from app.db.session import SessionLocal

from app.services.user_service import (
    create_user_service,
    get_user_service,
    get_user_by_email_service,
    get_users_service,
    update_user_service,
    delete_user_service,
)


db = SessionLocal()

try:

    email = "pramaan-test-user@example.com"

    # If you have already run this test before,
    # change the email to another value.

    user = create_user_service(
        db=db,
        email=email,
        display_name="PRAMAAN Test User",
    )

    print("Created User:")
    print("ID:", user.user_id)
    print("Email:", user.email)
    print("Display Name:", user.display_name)
    print("Active:", user.is_active)

    found = get_user_service(
        db,
        user.user_id,
    )

    print("\nGet User:")
    print("Email:", found.email)

    found_by_email = get_user_by_email_service(
        db,
        email,
    )

    print("\nGet By Email:")
    print("Display Name:", found_by_email.display_name)

    users = get_users_service(
        db,
        limit=100,
    )

    print("\nTotal Users:")
    print(len(users))

    updated = update_user_service(
        db=db,
        user_id=user.user_id,
        display_name="PRAMAAN Test User Updated",
        is_active=False,
    )

    print("\nUpdated User:")
    print("Display Name:", updated.display_name)
    print("Active:", updated.is_active)

    deleted = delete_user_service(
        db,
        user.user_id,
    )

    print("\nDeleted User:")
    print(deleted)

finally:
    db.close()