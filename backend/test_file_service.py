from app.db.session import SessionLocal

from app.services.file_service import (
    create_file_service,
    get_file_service,
    get_files_by_project_service,
    get_files_by_user_service,
    get_file_by_sha256_service,
    get_files_service,
    update_file_service,
    delete_file_service,
)

from app.repositories.project_repository import get_projects
from app.repositories.user_repository import get_users


db = SessionLocal()

try:
    # Get existing project
    projects = get_projects(db, limit=1)

    if not projects:
        raise ValueError(
            "No project found. Create a project first."
        )

    project = projects[0]

    # Get existing user
    users = get_users(db, limit=1)

    if not users:
        raise ValueError(
            "No user found. Create a user first."
        )

    user = users[0]

    # Create File
    file = create_file_service(
        db=db,
        project_id=project.project_id,
        uploaded_by=user.user_id,
        filename="PRAMAAN-Test-File.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        storage_path="test/pramaan-test-file.pdf",
        sha256="pramaan-test-sha256-001",
        sensitivity_class="confidential",
    )

    print("Created File:")
    print("ID:", file.file_id)
    print("Filename:", file.filename)
    print("MIME Type:", file.mime_type)
    print("Size:", file.size_bytes)
    print("Storage Path:", file.storage_path)
    print("SHA256:", file.sha256)
    print("Sensitivity:", file.sensitivity_class)

    # Get File
    found = get_file_service(
        db,
        file.file_id,
    )

    print("\nGet File:")
    print("Filename:", found.filename)

    # Get By SHA256
    found_by_sha256 = get_file_by_sha256_service(
        db,
        "pramaan-test-sha256-001",
    )

    print("\nGet By SHA256:")
    print("Filename:", found_by_sha256.filename)

    # Get Files By Project
    project_files = get_files_by_project_service(
        db,
        project.project_id,
    )

    print("\nFiles By Project:")
    print(len(project_files))

    # Get Files By User
    user_files = get_files_by_user_service(
        db,
        user.user_id,
    )

    print("\nFiles By User:")
    print(len(user_files))

    # Get All Files
    files = get_files_service(
        db,
        limit=100,
    )

    print("\nTotal Files:")
    print(len(files))

    # Update File
    updated = update_file_service(
        db=db,
        file_id=file.file_id,
        filename="PRAMAAN-Test-File-Updated.pdf",
        sensitivity_class="restricted",
    )

    print("\nUpdated File:")
    print("Filename:", updated.filename)
    print("Sensitivity:", updated.sensitivity_class)

    # Delete File
    deleted = delete_file_service(
        db,
        file.file_id,
    )

    print("\nDeleted File:")
    print(deleted)

finally:
    db.close()