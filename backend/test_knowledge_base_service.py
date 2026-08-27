from uuid import uuid4

from app.db.session import SessionLocal

from app.services.knowledge_base_service import (
    create_knowledge_base_service,
    get_knowledge_base_service,
    get_knowledge_bases_by_workspace_service,
    get_knowledge_bases_service,
    update_knowledge_base_service,
    delete_knowledge_base_service,
)

from app.models.workspace import Workspace


db = SessionLocal()

knowledge_base_name = (
    f"PRAMAAN-Test-KB-{uuid4().hex[:8]}"
)

updated_name = (
    f"{knowledge_base_name}-Updated"
)

try:

    workspace = db.query(Workspace).first()

    if workspace is None:
        print("No workspace found.")
    else:

        # CREATE
        knowledge_base = create_knowledge_base_service(
            db=db,
            workspace_id=workspace.workspace_id,
            name=knowledge_base_name,
            description="Knowledge base service test.",
            status="active",
        )

        print("Created Knowledge Base:")
        print("ID:", knowledge_base.knowledge_base_id)
        print(
            "Workspace ID:",
            knowledge_base.workspace_id,
        )
        print("Name:", knowledge_base.name)
        print(
            "Description:",
            knowledge_base.description,
        )
        print("Status:", knowledge_base.status)

        # GET BY ID
        found = get_knowledge_base_service(
            db,
            knowledge_base.knowledge_base_id,
        )

        print("\nGet Knowledge Base:")
        print("Name:", found.name)

        # GET BY WORKSPACE
        workspace_kbs = (
            get_knowledge_bases_by_workspace_service(
                db,
                workspace.workspace_id,
            )
        )

        print("\nKnowledge Bases in Workspace:")
        print(len(workspace_kbs))

        # GET ALL
        knowledge_bases = get_knowledge_bases_service(
            db,
            limit=100,
        )

        print("\nTotal Knowledge Bases:")
        print(len(knowledge_bases))

        # UPDATE
        updated = update_knowledge_base_service(
            db=db,
            knowledge_base_id=(
                knowledge_base.knowledge_base_id
            ),
            name=updated_name,
            description="Updated knowledge base test.",
            status="inactive",
        )

        print("\nUpdated Knowledge Base:")
        print("Name:", updated.name)
        print(
            "Description:",
            updated.description,
        )
        print("Status:", updated.status)

        # VERIFY UPDATE
        verified = get_knowledge_base_service(
            db,
            knowledge_base.knowledge_base_id,
        )

        print("\nVerified Updated Knowledge Base:")
        print("Name:", verified.name)
        print("Status:", verified.status)

        # DELETE
        deleted = delete_knowledge_base_service(
            db,
            knowledge_base.knowledge_base_id,
        )

        print("\nDeleted Knowledge Base:")
        print(deleted)

finally:
    db.close()