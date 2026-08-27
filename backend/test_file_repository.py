from app.db.session import SessionLocal

from app.repositories.file_repository import (
    create_file,
    get_file,
    get_files_by_project,
    get_files_by_user,
    get_file_by_sha256,
    get_files,
)

from app.models.project import Project
from app.models.user import User


db = SessionLocal()

try:

    project = db.query(Project).first()
    user = db.query(User).first()

    if project is None:
        print("No project found.")

    elif user is None:
        print("No user found.")

    else:

        file = create_file(
            db=db,
            project_id=project.project_id,
            uploaded_by=user.user_id,
            filename="repository_test.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            storage_path="uploads/repository_test.pdf",
            sha256="a" * 64,
            sensitivity_class="confidential",
        )

        print("Created File:")
        print("File ID:", file.file_id)
        print("Project ID:", file.project_id)
        print("Uploaded By:", file.uploaded_by)
        print("Filename:", file.filename)
        print("MIME Type:", file.mime_type)
        print("Size:", file.size_bytes)
        print("Storage Path:", file.storage_path)
        print("SHA256:", file.sha256)
        print("Sensitivity:", file.sensitivity_class)

        found = get_file(
            db,
            file.file_id,
        )

        print("\nGet File:")
        print(found.filename)

        project_files = get_files_by_project(
            db,
            project.project_id,
        )

        print(
            "\nFiles in Project:",
            len(project_files),
        )

        user_files = get_files_by_user(
            db,
            user.user_id,
        )

        print(
            "Files uploaded by User:",
            len(user_files),
        )

        hash_file = get_file_by_sha256(
            db,
            "a" * 64,
        )

        print(
            "File found by SHA256:",
            hash_file.filename if hash_file else None,
        )

        files = get_files(db)

        print(
            "Total Files:",
            len(files),
        )

finally:
    db.close()